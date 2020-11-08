import configparser
import mechanize
import xlsxwriter
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar
import pandas as pd

def littlefieldDataScraper():
    BASE_URL = "http://op.responsive.net"

    #Read from the config ini file
    config = configparser.ConfigParser()
    config.read('./config.ini')
    TEAM_ID = config['ConnectionInfo']['teamId']
    PASSWORD = config['ConnectionInfo']['password']
    SECTION_ID = config['ConnectionInfo']['sectionId']
    OUTPUT_FOLDERPATH = config['ExcelOutput']['outputfolderpath']
    SHEET_NAME = config['ExcelOutput']['sheetName']

    # Establish auth connection
    cj = CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    br.open(BASE_URL + "/lt/" + SECTION_ID + "/entry.html")
    br.select_form(nr=0)
    br.form['id'] = TEAM_ID
    br.form['password'] = PASSWORD
    br.submit()

    # Plots of charts with 2-columns of data
    url_list = ["CASH", "JOBIN", "JOBQ", "S1Q",
                "S2Q", "S3Q", "S1UTIL", "S2UTIL", "S3UTIL"]

    # Endpoints with 3-columns of data
    url_list_3col = ["JOBT", "JOBREV", "JOBOUT"]

    #Save data into dictionaries
    LF_DATA = {}

    #Create list for standings data
    STANDINGS_DATA = []

    #Create list for history data
    HISTORY_DATA = []

    # Get STANDINGS data
    standings_url = BASE_URL + "/Littlefield/Standing"
    soup = BeautifulSoup(br.open(standings_url), "lxml")
    table = soup.find('table')
    table_rows = table.find_all('tr')

    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        STANDINGS_DATA.append(row)

    writer = pd.ExcelWriter(
        OUTPUT_FOLDERPATH + "\standings.xlsx", engine='xlsxwriter')
    df = pd.DataFrame.from_dict(STANDINGS_DATA)
    df.index = df.index.map(str)
    df.columns = df.iloc[0]
    df = df[1:]  # Removes the first row of data

    #Covert to XlsxWriter Excel Object
    df.to_excel(writer, sheet_name=SHEET_NAME)

    writer.save()

    #Get HISTORY data
    history_url = BASE_URL + "/Littlefield/History"

    soup = BeautifulSoup(br.open(history_url), "lxml")
    table = soup.find('table')
    table_rows = table.find_all('tr')

    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        HISTORY_DATA.append(row)

    writer = pd.ExcelWriter(
        OUTPUT_FOLDERPATH + "\history.xlsx", engine='xlsxwriter')
    df = pd.DataFrame.from_dict(HISTORY_DATA)
    df.index = df.index.map(str)
    df.columns = df.iloc[0]
    df = df[1:]  # Removes the first row of data

    #Covert to XlsxWriter Excel Object
    df.to_excel(writer, sheet_name=SHEET_NAME)

    writer.save()

    # Get INVENTORY first
    inv_url = BASE_URL + "/Littlefield/Plot?data=INV&x=all"
    soup = BeautifulSoup(br.open(inv_url), "lxml")
    data = soup.find_all("script")[5].string
    data = data.split("\n")[4].split("'")[3].split()

    counter = 1
    for i in data:
        if counter % 2 == 1:
            counter += 1
            day = float(i)
            LF_DATA[day] = []
        elif counter % 2 == 0:
            row_data = [float(i)]
            LF_DATA[day].extend(row_data)
            counter += 1

    # List comprehension to delete values from inventory dictionary that are not "integers".
    # This is essentially getting rid of the data where the system records inventory receipts.
    delete = [i for i in LF_DATA if i % int(i) != 0]
    for i in delete:
        del LF_DATA[i]

    # iterate through and scrape all two-column tables
    for url in url_list:
        lf_url = BASE_URL + "/Littlefield/Plot?data=%s&x=all" % url
        soup = BeautifulSoup(br.open(lf_url), "lxml")
        data = soup.find_all("script")[5].string
        data = data.split("\n")[4].split("'")[3].split()
        counter = 1
        for i in data:
            if counter % 2 == 0:
                day = counter / 2
                LF_DATA[day].append(float(i))
                counter += 1
            else:
                counter += 1

    # iterate through and scrape all three-column tables
    for url in url_list_3col:
        lf_url = "http://op.responsive.net/Littlefield/Plot?data=%s&x=all" % url
        soup = BeautifulSoup(br.open(lf_url), "lxml")
        data = soup.find_all("script")[5].string
        data0 = data.split("\n")[4].split("'")[5].split()
        data1 = data.split("\n")[5].split("'")[5].split()
        data2 = data.split("\n")[6].split("'")[5].split()

        counter = 1
        for i in data0:
            if counter % 2 == 0:
                day = counter / 2
                LF_DATA[day].append(float(i))
                counter += 1
            else:
                counter += 1
        counter = 1
        for i in data1:
            if counter % 2 == 0:
                day = counter / 2
                LF_DATA[day].append(float(i))
                counter += 1
            else:
                counter += 1
        counter = 1
        for i in data2:
            if counter % 2 == 0:
                day = counter / 2
                LF_DATA[day].append(float(i))
                counter += 1
            else:
                counter += 1

    # Add dummy data to fill out fractional day rows
    dummy_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for key, value in LF_DATA.items():
        if len(value) < 19:
            value.extend(dummy_data)

    # Prepare the dataframe to be written to the google sheet
    writer = pd.ExcelWriter(
        OUTPUT_FOLDERPATH + "\data.xlsx", engine='xlsxwriter')
    headers = ["inventory", "cash", "orders", "order \nqueue", "s1\nqueue", "s2\nqueue", "s3\nqueue", "s1\nutilization", "s2\nutilization", "s3\nutilization",
               "c1\naverage\nleadtime", "c2\naverage\nleadtime", "c3\naverage\nleadtime", "c1\naverage\nrevenues", "c2\naverage\nrevenues", "c3\naverage\nrevenues",
               "c1\njobs\ncompleted", "c2\njobs\ncompleted", "c3\njobs\ncompleted"]
    df = pd.DataFrame.from_dict(LF_DATA, orient="index")
    df.index = df.index.map(str)
    df.columns = headers

    # Fix issue with cash in $1,000's
    df.loc[:, 'cash'] *= 1000

    #Covert to XlsxWriter Excel Object
    df.to_excel(writer, sheet_name=SHEET_NAME)

    #Close the Excel Writer
    writer.save()

littlefieldDataScraper()
print("Script executed successfully")