# Scraper

Scraper is a web scraping tool designed to extract structured data from websites. This project is built using Python and leverages libraries such as `requests`, `BeautifulSoup`, and `pandas` for scraping and data manipulation.

## Table of Contents
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)


## Getting Started

This project allows users to easily scrape data from websites and store the results in CSV or JSON formats. It's designed to be flexible and extendable for different types of websites and data structures.

## Prerequisites

Make sure you have the following installed:

- Python 3.8+
- Git
- A virtual environment tool like `venv` or `virtualenv`

To install Python, you can refer to the [official Python documentation](https://www.python.org/downloads/).

## Local Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/pauleatonc/scraper.git
   cd scraper

2. Create and activate a virtual environment:

    python3 -m venv venv
    source venv/bin/activate  # Activate the virtual enviroment

3. Install the required dependencies:

    pip install -r requirements.txt

4. Run locally

    python3 manage.py runserver


## Start with Docker for easyer run.

1. Clone the repository:

   ```bash
   git clone https://github.com/pauleatonc/scraper.git
   cd scraper

2. Use docker compose

    docker compose -f docker-compose-dev.yml up
