
About Lazyscraper
=================

Lazyscraper is a simple command line tool and library, a swiss knife for scraper writers. It's created to work only from command line and to make easier
scraper writing for very simple tasks like extraction of external urls or simple table.


Supported patterns
==================
* simpleul - Extracts list of urls with pattern ul/li/a. Returns array of urls with "_text" and "href" fields
* simpleopt - Extracts list of options values with pattern select/option. Returns array: "_text", "value"
* exturls - Extracts list of urls that leads to external websites. Returns array of urls with "_text" and "href" fields
* getforms - Extracts all forms from website. Returns complex JSON data with each form on the page


Command-line tool
=================
Usage: lazyscraper.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
* extract   Extract data with xpath
* gettable  Extracts table with data from html
* use       Uses predefined pattern to extract page data

Examples
========

Extracts list of photos and names of Russian government ministers and outputs it to "gov_persons.csv"

    python lscraper.py extract --url http://government.ru/en/gov/persons/ --xpath "//img[@class='photo']" --fieldnames src,srcset,alt --absolutize True --output gov_persons.csv --format csv

Extracts list of ministries from Russian government website using pattern "simpleul" and from UL tag with class "departments col col__wide" and outputs absolutized urls.

    python lscraper.py use --pattern simpleul --nodeclass "departments col col__wide" --url http://government.ru/en/ministries  --absolutize True


Extracts list of territorial organizations urls from Russian tax service website using pattern "simpleopt".

    python lscraper.py use --pattern simpleopt --url http://nalog.ru

Extracts all forms from Russian tax service website using pattern "getforms". Returns JSON with each form and each button, input and select

    python lscraper.py use --pattern getforms --url http://nalog.ru

Extracts list of websites urls of Russian Federal Treasury and uses awk to extract domains.

    python lscraper.py extract --url http://roskazna.ru --xpath "//ul[@class='site-list']/li/a" --fieldnames href | awk -F/ '{print $3}'

How to use library
==================

Extracts all urls with fields: src, alt, href and _text from gov.uk website
    >>> from lazyscraper import extract_data_xpath
    >>> extract_data_xpath('http://gov.uk', xpath='//a', fieldnames='src,alt,href,_text', absolutize=True)


Run pattern 'simpleopt' against Russian federal treasury website
    >>> from lazyscraper import use_pattern
    >>> use_pattern('http://roskazna.ru', 'simpleopt')

Requirements
============
* Python3 https://www.python.org
* click https://github.com/pallets/click
* lxml http://lxml.de/
