# RAD Backend Task

- At a glance
    - List stations at [https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/list_stations/](https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/list_stations/)
    - Query a station at [https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_station/1](https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_station/1) (substitute 1 for a valid station ID)
    - Query an individual user at [https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_user/Mika](https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_user/Mika) (substitute ‘Mika’ for a valid username. Other users are PrinceDaddy, jada, and Design Man.)
- Requirements
    - Create an API endpoint for obtaining a list of radio stations
    - The results of this api call should allow us to obtain individual radio stations
    - Create an API endpoint for obtaining the details for a singular radio station
    - Create an API endpoint for obtaining details about a user
    - Support the API with a database
    - Implement the endpoints as either a REST API or a GraphQL API
    - Ensure you have a mechanism or tool available for adding data into the database
    - Introduce a migration tool for managing the database schema
    - Ensure the steps are outlined for how to run the application
- Background - Research ([181fm.com](http://181fm.com))
    
    First, I took a look at the website. It had no direct API endpoints I could find to list radio stations, so I decided to do things the hacky way: web scraping. Looking at the website’s javascript, I discovered some interesting variables:
    
    - streamUrl variable exposes station’s stream link
    - cfg_cc_title variable exposes name of the station
    - [http://player.181fm.com/?autoplay=](http://player.181fm.com/?autoplay=1){n} points to stations, where **n** is a station identification number of sorts.
    - The setsong function plays a song
    
    At this point, it was just over half an hour since I started the task so I abandoned finding a perfectly optimal solution to obtaining a list of radio stations. I used ****************selenium**************** to webscrape the homepage and grabbed a list of stations and their corresponding station IDs and stream URLs. These were then inserted into an sqlite3 database. For example, The station ‘The Vibe of Vegas’ had a station ID of 1. This was enough to provide functionality pertaining to radio stations.
    
    - Station Scraper Code
        
        ```python
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
        ```
        
    
    Concerning users, I am assuming the task was referring to the chatbox functionality, as I did not find any other mentions to ‘user’ within the time limit. Poking at the chat tab revealed it to be an embedded chatting widget provided by cbox.ws. This also proved scrapable and I wrote another function to scrape all messages sent till date (8th dec) and inserted them into an sqlite database.
    
    - User scraper code
        
        ```python
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
        ```
        
- Implementing Functionality
    
    The API is implemented in python 3.9 using the Django web framework.
    
    - Listing radio stations
        
        **endpoint**: [https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/list_stations/](https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/list_stations/)
        
        - Code
            
            ```python
            def list_stations(request):
            		# return a json object of station ids and names
                db = sqlite3.connect("station_data.sqlite3")
                stations = db.execute("SELECT station_id, station_name FROM stations;")
                stations= str(dict(stations))
                stations = json.dumps(stations)
                return HttpResponse(stations)
            ```
            
        
        After doing the preliminary scraping and database insertion described in the background section, implementing this functionality became straightforward. The view returns a JSON object in this format: `{station_id1: station_name1, station_id2: station_name2...station_id_n: station_name_n}.`As show, it returns a list of stations by their station id and names. These IDs could then be used to query individual stations, as will be discussed in the next section.
        
        ![Untitled](RAD%20Backend%20Task%20046e2d0faf63458c90a2f64afd3c9c5e/Untitled.png)
        
    - Querying Individual Stations
        
        **endpoint**:[https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_station/1](https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_station/1)
        
        After obtaining a list of stations, one might then want to query an individual station to obtain its stream URL.
        
        - Code
            
            ```python
            def get_station(request, id):
                db = sqlite3.connect("station_data.sqlite3")
                station = db.execute("SELECT station_id, station_name, stream_url FROM stations WHERE station_id=" + str(id) + ";")
            
                # return a json object of a station id, station name, and streamurl
                station= list(station)
                if station:
                    station = str({"id":station[0][0], "name": station[0][1], "stream_url": station[0][2]})
                    station = json.dumps(station)
                else:
                    station = json.dumps(str({"error": "Station not found."}))
                return HttpResponse(station)
            ```
            
        
        The code has basic error-checking functionality. If a known station id is supplied, it returns a JSON object containing the station id, its name, and stream URL:
        
        ![Untitled](RAD%20Backend%20Task%20046e2d0faf63458c90a2f64afd3c9c5e/Untitled%201.png)
        
    - Querying an individual user
        
        **endpoint**: [https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_user/Mika](https://yxcs86ujva.execute-api.eu-west-2.amazonaws.com/dev/get_user/Mika)
        
        - Code
            
            ```python
            def get_user(request, usern):
                db = sqlite3.connect("station_data.sqlite3")
                user = db.execute(f"SELECT message FROM users WHERE username = '{str(usern)}';")
                user = list(user)
            
                # return a json object containing user's messages and message count
                if user:
                    user = list([str(u[0]) for u in user])
                    user = {"name": usern, "messages": user, "count":str(len(user))}
                    user = json.dumps(str(user))
                else:
                    user = json.dumps(str({"error": "User not found."}))
            ```
            
        
        As cbox did not allow obtaining arbitrary details about a particular user, I instead decided that the get_user view would provide a list and count of messages sent by a particular user in the chatbox. The JSON object returned contains the username, list of messages, and message count for a valid user:
        
        ![Untitled](RAD%20Backend%20Task%20046e2d0faf63458c90a2f64afd3c9c5e/Untitled%202.png)
        
    - Adding stations
        
        endpoint unavailable, I have given the lambda function read-only permissions.
        
        - Code
            
            ```python
            def add_station(request):
                id=name=stream_url=""
                try:
                    id=int(request.GET["id"])
                    name=html.escape(request.GET["name"])
                    stream_url=html.escape(request.GET["stream_url"])
                except:
                    response = json.dumps(str({"error": "Invalid Input"}))
                
                if (not id) or (not name) or (not stream_url):
                    return HttpResponse(response)
            
                db = sqlite3.connect("station_data.sqlite3")
            
                check_id = list(db.execute(f"SELECT * FROM stations WHERE station_id = '{id}';"))
            
                if not check_id:
                    db.execute(f"INSERT INTO stations(station_id, station_name, stream_url) VALUES({id}, '{name}', '{stream_url}');")
                    db.commit()
                    response = json.dumps(str({"Success": "Added station."}))
                else:
                    response = json.dumps(str({"error": "Station ID exists."}))
                # print(id, name, stream_url)
                
                return HttpResponse(response)
            ```
            
        
        I also implemented the ability to add stations to the database.
        
    - Migration Functionality
        
        Django has built-in schema migration functionality.
        
- Deployment
    
    The API is currently hosted as an AWS lambda function for the next 7 days. It was deployed using the Zappa python package.
