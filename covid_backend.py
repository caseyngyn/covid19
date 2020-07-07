
'''
Casey Nguyen
back-end
'''

import lxml
from bs4 import BeautifulSoup
import requests
import re
import pickle
import json
import sqlite3

'''
url = 'https://www.worldometers.info/coronavirus/'

#get the web page and create repsonse object
response = requests.get(url)
#make easier to navigate data structure have to pass data to the BeautifulSoup
soup = BeautifulSoup(response.content,'lxml')
table = soup.find("tbody")
world_data = []

for row in table.find_all('tr'):
    country = []

    for td in row.find_all('td'):
        if len(td.text.strip()) == 0:
            country.append(0)
        elif any(map(str.isdigit,td.text.strip())):
            if td.text.strip().count('.') == 0:
                country.append(int(td.text.replace(',','').strip()))
            else:
                country.append(float(td.text.replace(',','').strip()))
        else:
            country.append(td.text.replace('\u00e7','').strip())
    #remove the # and the continent they belong to and the continent they belong to
    del country[0]
    del country[len(country)-1]
    world_data.append(country)


with open('data.json', 'w') as fh:
    json.dump(world_data, fh, indent=3)    
'''

with open('data.json', 'r') as fh:
    covid_data = json.load(fh)

#create database
col_int = ['TotalCases','NewCases','TotalDeaths','NewDeaths','TotalRecovered','ActiveCases','SeriousCritical','TotalTests','TestsPer1mPop','Population']
col_real = ['TotCasesPer1Mpop','DeathPer1mPop']

conn = sqlite3.connect('covid.db')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS CovidDB")
#create table and key country
cur.execute('''CREATE TABLE CovidDB (Country TEXT NOT NULL PRIMARY KEY UNIQUE)''')
#from the take the first 7 values bc they are ints in the json file
for col in col_int[0:7]:
    cur.execute('''ALTER TABLE CovidDB ADD {} INTEGER'''.format(col) )
#next 2 data values are going to be read in as float
for col in col_real:
    cur.execute('''ALTER TABLE CovidDB ADD {} REAL'''.format(col) )
#last 2 are ints again
for col in col_int[7:]:
    cur.execute('''ALTER TABLE CovidDB ADD {} INTEGER'''.format(col) )

#Inserting data into sql table
for country in covid_data:
    cur.execute('''INSERT INTO CovidDB VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (country))

#remove the weird 0 country
cur.execute('''DELETE FROM  CovidDB WHERE Country = 0''' )

conn.commit()
cur.close()
conn.close()
