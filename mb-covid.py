#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import datetime
from datetime import datetime
from influxdb import InfluxDBClient
import time

timestamp = datetime.datetime.utcnow().isoformat("T") + "Z"
date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "email@gmail.com"  # Enter your address
receiver_email = "email@gmail.com"  # Enter receiver address
password = "password"



# InfluxDB info
InfluxIP = "192.168.0.0"
InfluxPort = 8086
InfluxDB = "db-name"
InfluxUser = "user-name"
InfluxPass = "user-pass"

postdata = []

"""
# ========================================================================
    FUNCTION: PARSE TABLE
    PURPOSE: parse "real time" COVID Data in Manitoba from Wikipedia
    INPUT: NONE
    OUTPUT: [LIST] MB COVID INFO. [province, population, tests, perk k,
    cases, per m, recovered, deaths, per m, active, ref]
# ========================================================================
 """


def parse_table():
    website_url = requests.get(
        'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/Canada_medical_cases_by_province').text
    soup = BeautifulSoup(website_url, 'lxml')
    covid_table = soup.find('table', {'class': 'wikitable sortable'})
    for row in covid_table.findAll("tr"):
        cells = row.findAll('td')
    rows = covid_table.findAll("tr")
    header = [th.text.rstrip() for th in rows[0].find_all('th')]

    lst_data = []
    for row in rows[1:]:
        data = [d.text.rstrip() for d in row.find_all('td')]
        lst_data.append(data)

    lst_data1 = []
    for row in rows[1:]:
        data = [d.text.rstrip() for d in row.select('td')]
        lst_data1.append(data)
    return (lst_data1[4])

stats = parse_table()
print(stats)

with open('covid-test.txt', 'a') as f:
    for item in stats:
        f.write(" ")
        f.write(item)

cases = stats[4].replace(',', '')
casesi = int(cases)

recov = stats[6].replace(',', '')
recovi = int(recov)

deaths = stats[7].replace(',', '')
deathsi = int(deaths)

active = stats[9].replace(',', '')
activei = int(active)

postdata.append(
    {
        "measurement": "Manitoba",
        "tags": {
            "host": "db1",
        },
        "time": timestamp,
        "fields": {
            "cases": casesi
        }
    }
)
postdata.append(
    {
        "measurement": "Manitoba",
        "tags": {
	    "host": "db1",
        },
        "time": timestamp,
        "fields": {
            "recovered": recovi
        }
    }
)
postdata.append(
    {
        "measurement": "Manitoba",
        "tags": {
            "host": "db1",
        },
        "time": timestamp,
        "fields": {
            "deaths": deathsi
        }
    }
)
postdata.append(
    {
        "measurement": "Manitoba",
        "tags": {
            "host": "db1",
        },
        "time": timestamp,
        "fields": {
            "active": activei
        }
    }
)
client = InfluxDBClient(InfluxIP, InfluxPort, InfluxUser, InfluxPass, InfluxDB)
client.write_points(postdata)


'''
Send emails
'''

body = f"""\
Subject: Covid stats {date}

Cases: {stats[4]}
Recovery: {stats[6]}
Deaths: {stats[7]}
Active: {stats[9]}
"""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, body)
