import sqlite3
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import html
import json




def populate_users():
    print("[Populating Users table]")
    #connect to db
    db = sqlite3.connect("radio_project\\station_data.sqlite3")

    #create users table
    try:
        db.execute('''
        CREATE TABLE users
        (username CHAR(100) NOT NULL,
        message TEXT NOT NULL
        );''')
    except Exception as e:
        print(e)

    # hardcoded urls of chat logs
    urls=["https://www4.cbox.ws/box/index.php?boxid=3355984&boxtag=8114&sec=archive&i=13735091",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13735011&p=2",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13734931&p=3",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13734851&p=4",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13734771&p=5",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13734686&p=6",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13734606&p=7",
        "https://www4.cbox.ws/box/?boxid=3355984&boxtag=8114&sec=archive&i=13735091&pi=13734526&p=8"
        ]

    # scrape user chat data from chat logs
    messages=[]
    for url in urls:
        chat_page = requests.get(url)
        chat_page = BeautifulSoup(chat_page.content, "html.parser")

        for text in chat_page.find_all(class_="msg"):
            text = text.get_text()
            msg_time = text[0:17]
            msg = text[17:].split(":")
            msg_sender = msg[0]
            msg_body = html.escape(msg[1])

            #insert into db
            db.execute(f"INSERT INTO users(username, message) VALUES('{msg_sender}', '{msg_body[1:]}');")
            db.commit()
            # print(f"at {msg_time}, {msg_sender} sent {msg_body}")


def populate_stations():
    print("[Populating Stations table]")
    # config selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")

    db = sqlite3.connect("radio_project\\station_data.sqlite3")

    # create stations table
    try:
        db.execute('''
        CREATE TABLE stations
        (station_id INT PRIMARY KEY NOT NULL,
        station_name CHAR(100) NOT NULL,
        stream_url TEXT NOT NULL
        );''')
    except Exception as e:
        pass

    # simulate organic traffic, scrape station stream data
    driver = webdriver.Chrome(options=chrome_options)
    with open("radio_project\\radio_project\stations.txt", "r") as file:
        for line in file.readlines():

            line = line.strip().split(">")

            id = line[0].replace(')', '')
            id = id.replace('(', '')

            name = line[1].replace("'", '')

            # insert into db
            stream_url=""
            driver.get(f"http://player.181fm.com/?autoplay={id}")
            stream_url = driver.execute_script("return streamUrl;")
            stream_url = stream_url.split("?")[0]
            print(f"Inserting {id}-{name}-{stream_url}")
            db.execute(f"INSERT INTO stations(station_id, station_name, stream_url) VALUES({id}, '{name}', '{stream_url}');")
            db.commit()
def usedb():
    db = sqlite3.connect("radio_project\\station_data.sqlite3")
    stations = db.execute("SELECT station_id, station_name FROM stations;")
    stations= str(dict(stations))
    stations = json.dumps(stations)
    print(stations)
def use_station(id):
    db = sqlite3.connect("radio_project\\station_data.sqlite3")
    station = db.execute("SELECT station_id, station_name, stream_url FROM stations WHERE station_id=" + str(id) + ";")

    station= list(station)
    if station:
        station = str({"id":station[0][0], "name": station[0][1], "stream_url": station[0][2]})
        station = json.dumps(station)
    else:
        station = {"error": "Station not found."}
    print(station)

def user(user):
    db = sqlite3.connect("radio_project\\station_data.sqlite3")
    user = db.execute(f"SELECT message FROM users WHERE username = '{str(user)}';")
    user = list([str(u[0]) for u in user])
    user = {"messages": user, "count":str(len(user))}
    print(user)
def add_station(id, name, stream_url):
    if (not id) or (not name) or (not stream_url):
        error = "Invalid input."

    db = sqlite3.connect("radio_project\\station_data.sqlite3")
    db.execute(f"INSERT INTO stations(station_id, station_name, stream_url) VALUES({id}, '{name}', '{stream_url}');")
    db.commit()

# print("go")
# populate_users()
# populate_stations()
# usedb()

# use_station(5)

user("Mika")
