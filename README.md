NFL Quarterback Scraper
=======================

Scrape Wikipedia and nfl.com for the list of starting quarterbacks during the 2015 NFL 
season.

Installing
----------

This code is build for Python 2.7.  Use pip to install all the requirements:

```shell
pip install -r requirements.txt
```

Running
-------

To scrape the websites run this script to update the `.csv` and `.json` files:

```shell
python scrape-names.py
```

The code will build a simple file-based local cache of the webpages so you can tweak the 
scraper without pinging their websites over an over again.
