package main

import (
	"bytes"
	"encoding/base64"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/joho/godotenv"
)

type Config struct {
	domain   string
	user     string
	password string
}

type FAQPost struct {
	Title   string `json:"title"`
	Content string `json:"content"`
	Slug    string `json:"slug"`
	Status  string `json:"status"`
	Tags    []int  `json:"tags,omitempty"`
}

type faqRow struct {
	question string
	answer   string
	cluster  string
	slug     string
}

// wpTag is the subset of a WordPress tag term we care about.
type wpTag struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

const (
	csvFile = "foxhaven-faqs.csv"
)

func main() {
	config := Config{}

	if err := godotenv.Load(); err != nil {
		log.Fatalf("loading .env: %v", err)
	}

	config.domain = os.Getenv("wordpress.foxhaven.domain")
	config.user = os.Getenv("wordpress.foxhaven.user")
	config.password = os.Getenv("wordpress.foxhaven.password")

	if config.user == "" || config.password == "" || config.domain == "" {
		log.Fatal("crucial value is missing from .env")
	}

	rows, err := readFAQs(csvFile)
	if err != nil {
		log.Fatalf("reading csv: %v", err)
	}

	auth := base64.StdEncoding.EncodeToString([]byte(config.user + ":" + config.password))
	baseURL := fmt.Sprintf("https://%s/wp-json/wp/v2", config.domain)
	postsEndpoint := baseURL + "/posts" // NOTE: we can change this to /faqs for creating faq posts
	client := &http.Client{Timeout: 30 * time.Second}

	// tagCache maps a cluster name to its WordPress tag ID so repeated
	// clusters don't trigger redundant lookups/creations.
	tagCache := map[string]int{}

	for i, row := range rows {
		post := FAQPost{
			Title:   row.question,
			Content: row.answer,
			Slug:    row.slug,
			Status:  "publish",
		}

		// Tag the post with its cluster value.
		if cluster := strings.TrimSpace(row.cluster); cluster != "" {
			tagID, err := resolveTag(client, baseURL, auth, cluster, tagCache)
			if err != nil {
				log.Printf("row %d (%s): resolving tag %q: %v", i+1, row.slug, cluster, err)
			} else if tagID != 0 {
				post.Tags = []int{tagID}
			}
		}

		if err := createFAQ(client, postsEndpoint, auth, post); err != nil {
			log.Printf("row %d (%s): %v", i+1, row.slug, err)
			continue
		}
		log.Printf("created: %s", row.slug)
	}
}

func readFAQs(path string) ([]faqRow, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	r := csv.NewReader(f)
	header, err := r.Read()
	if err != nil {
		return nil, fmt.Errorf("reading header: %w", err)
	}

	idx := map[string]int{}
	for i, col := range header {
		idx[col] = i
	}
	for _, required := range []string{"question", "answer", "cluster", "slug"} {
		if _, ok := idx[required]; !ok {
			return nil, fmt.Errorf("missing column %q", required)
		}
	}

	var rows []faqRow
	for {
		rec, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}
		rows = append(rows, faqRow{
			question: rec[idx["question"]],
			answer:   rec[idx["answer"]],
			cluster:  rec[idx["cluster"]],
			slug:     rec[idx["slug"]],
		})
	}
	return rows, nil
}

func createFAQ(client *http.Client, endpoint, auth string, post FAQPost) error {
	body, err := json.Marshal(post)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Basic "+auth)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 300 {
		b, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("status %d: %s", resp.StatusCode, string(b))
	}
	return nil
}

// resolveTag returns the WordPress tag ID for name, looking it up first and
// creating it if it doesn't already exist. Results are memoized in cache.
func resolveTag(client *http.Client, baseURL, auth, name string, cache map[string]int) (int, error) {
	name = strings.TrimSpace(name)
	if name == "" {
		return 0, nil
	}
	if id, ok := cache[name]; ok {
		return id, nil
	}

	id, err := findTag(client, baseURL, auth, name)
	if err != nil {
		return 0, err
	}
	if id == 0 {
		id, err = createTag(client, baseURL, auth, name)
		if err != nil {
			return 0, err
		}
	}

	cache[name] = id
	return id, nil
}

// findTag searches existing tags and returns the ID of an exact (case-insensitive)
// name match, or 0 if none exists.
func findTag(client *http.Client, baseURL, auth, name string) (int, error) {
	endpoint := fmt.Sprintf("%s/tags?search=%s", baseURL, url.QueryEscape(name))
	req, err := http.NewRequest(http.MethodGet, endpoint, nil)
	if err != nil {
		return 0, err
	}
	req.Header.Set("Authorization", "Basic "+auth)

	resp, err := client.Do(req)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	b, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 300 {
		return 0, fmt.Errorf("status %d: %s", resp.StatusCode, string(b))
	}

	var tags []wpTag
	if err := json.Unmarshal(b, &tags); err != nil {
		return 0, err
	}
	for _, t := range tags {
		if strings.EqualFold(t.Name, name) {
			return t.ID, nil
		}
	}
	return 0, nil
}

// createTag creates a tag with the given name and returns its ID. If the tag
// already exists (term_exists), the existing ID is returned.
func createTag(client *http.Client, baseURL, auth, name string) (int, error) {
	body, err := json.Marshal(map[string]string{"name": name})
	if err != nil {
		return 0, err
	}
	req, err := http.NewRequest(http.MethodPost, baseURL+"/tags", bytes.NewReader(body))
	if err != nil {
		return 0, err
	}
	req.Header.Set("Authorization", "Basic "+auth)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	b, _ := io.ReadAll(resp.Body)
	if resp.StatusCode < 300 {
		var t wpTag
		if err := json.Unmarshal(b, &t); err != nil {
			return 0, err
		}
		return t.ID, nil
	}

	// A tag with this name may already exist; WordPress returns its ID in the error.
	var apiErr struct {
		Code string `json:"code"`
		Data struct {
			TermID int `json:"term_id"`
		} `json:"data"`
	}
	if json.Unmarshal(b, &apiErr) == nil && apiErr.Code == "term_exists" && apiErr.Data.TermID != 0 {
		return apiErr.Data.TermID, nil
	}
	return 0, fmt.Errorf("status %d: %s", resp.StatusCode, string(b))
}
