# Visa appointments scraper
This scraper is made for checking the ais.usvisa-info.com site in time intervals. It logs you in, and scrape the payment site and when there's an available appointment (a change on the original site where there are not appointments) it will notify you through a Telegram bot.

## Prerequesites
1. Create telegram bot

## Installation
1. Install chromedriver
2. Install requirements

## Usage
1. Update creds.py
2. Run the script
```
nohup python3 selenium_scraper.py &
```

This is script is based on [Ed1123](https://github.com/Ed1123/visa_web_scraper) work.
