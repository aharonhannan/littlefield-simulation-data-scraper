# Littlefield Simulations Data Scraper

The Littlefield Simulation has an interface that requires a bunch of manual effort to export and/or analyze data. Given that data is updated in short intervals throughout a "realtime" day, analyzing up to ten separate graphs across different browser windows can be time-consuming and cumbersome. 

This script calls all  endpoints of the Littlefield simulation and scrapes data from the HTML and consolidates them into a single data table. 

This project was based on [@flapjack29](https://github.com/flapjack29/littlefield_simulation_web_scraper)'s implementation. The difference in this repo is that the data is exported into several Excel files locally, removes a dependency on Google Sheets, and introduces easier tweaking through a config file.

## Prerequisites/Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies that this script uses.

```bash
pip install configparser
pip install mechanize
pip install pandas as pd
pip install xlsxwriter
pip install BeautifulSoup
pip install CookieJar
```

## Configuration

In the included config.ini file, you'll need to edit the values in order to successfully connect to the simulation.

Once that is set, you're ready to run the simulation.

From a Terminal window, you can simply execute the Python file. 

```python
python .\littlefieldscraper.py
```

If things succeeded, you should have a success message returned, along with an output of the following files:
- data.xlsx
- history.xlsx
- standings.xlsx

## Output

The script will output three separate Excel spreadsheets, which you can feed into a dashboard-building tool, such as Power BI.

- data.xlsx - The consolidated data table of all inputs and outputs of the system across all machines, updated at each day interval.
- history.xlsx - The table of your team's decisions, updated at each day interval.
- standings.xlsx - The table of every team's rank and their cash-on-hand at the latest script run time.