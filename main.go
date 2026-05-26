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
	"os"
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
}

type faqRow struct {
	question string
	answer   string
	slug     string
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
	endpoint := fmt.Sprintf("https://%s/wp-json/wp/v2/posts", config.domain) // NOTE: we can change this to /faqs for creating faq posts
	client := &http.Client{Timeout: 30 * time.Second}

	for i, row := range rows {
		post := FAQPost{
			Title:   row.question,
			Content: row.answer,
			Slug:    row.slug,
			Status:  "publish",
		}
		if err := createFAQ(client, endpoint, auth, post); err != nil {
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
	for _, required := range []string{"question", "answer", "slug"} {
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
