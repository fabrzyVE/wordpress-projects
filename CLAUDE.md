## Backyard Care Pages 

We have a clients webflow site to implement pages on. This task will be creating those pages in draft mode by using the avialable resources.

### Resources 

- figma designs ("designs/services" and "designs/neighborhoods" folder) 
- assets ("assets/" folder)
- implementation sheet (xlsx file in root of project)

### Notes 

the xlsx file and figma file serves as your source of truth. Figma for the styling and the xlsx file for the correct copywrite and content. The xlsx file has 2 worksheets one for services and one for neighborhoods that serve as the copywrite and content for the pages. 

If you cannot find the content for a specific element from the content sheet fallback to the figma design and last resort fallback to lorem ipsum text.

### Rules 

1. Do not publish anything live everything must be drafted

2. Do not modify any existing pages or do any actions that will affect any other pages of the webflow site

3. Use the figma quality check skill we have to make sure each page follows the figma design perfectly

4. Reuse global Navbar and Footer component in the site for all pages do not create a new one 


### Tasks 

- use the skill or agent to quality check your output until you are confident that the pages are perfectly matching the design 

- prompt me what you need to finalize everything such as where hrefs point to or any missing design elements you need 

## Special Rules 

- there will be a section that is the testimonial section. There are two one for services page and one for areas, there is one dependent for google reviews testimonials , if there is no way to source those reviews from google just fallback to the version that doesnt require google reviews. 

- Any sections that require showing a list of areas such as sections with the heading of "Areas we serve in X" will require you to accurately show a list of all of our neighborhoods in the sheet in geographically closest order respective to the neighborhood page we are implementing

## Strategy

Since we want to mass create pages here we should be using templates in webflow and creating a template schema where we can easily swap in dynamic content in and out such as images and certain texts. Create the templates in this manner and create an efficient schema and then draft all the pages using the template. 
