# Squarespace Blog Analytics Scraper

This program automatically retrieves and stores the top 100 blog posts of the previous month. 

It outputs this file into a neat .csv file that filters out all non-blog pages and the blog page itself.

### This program requires several environment variables:

- SQUARESPACE_COOKIE
- OUTPUT_DIR
- SQUARESPACE_SUBDOMAIN

Yes, this will require a cookie from your headers in your logged-in browser. This is likely the most streamlined flow for this process.