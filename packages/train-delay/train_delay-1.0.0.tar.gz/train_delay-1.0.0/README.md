# TrainDelay 

TrainDelay is a Python package for tracking train delays at various stations using the Deutsche Bahn API. It collects real-time train data, processes delay information, and stores it in a MySQL database for further analysis.

## Features

- Fetches train timetable and delay data for specified stations
- Stores train data in a MySQL database
- Logs tracking operations and errors

## Requirements
1. Get a MySQL Server running on your machine, the database and tables will be created my the module
2. Register for the Deutsche Bahn API (free)
- Create a account at: https://developers.deutschebahn.com
- Create a new application using this url: https://developers.deutschebahn.com/db-api-marketplace/apis/application/new and choose a name that you want
- After that save you the client id and the client secret. You need it to interact with the api
- Navigate to all available apis page at: https://developers.deutschebahn.com/db-api-marketplace/apis/product and select the "Timetables" api
- And click the red subscribe button and select your application
- Now you are done and can start using the api

## Setup
1. Install train_delay using: `pip install train_delay`
2. import module 
```python
from train_delay import *
```
3. Create an AuthData object and a DatabaseConfig object
```python
auth_data = AuthData(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)  
database_config = DatabaseConfig(YOUR_DB_HOSTNAME, YOUR_DB_USER, YOUR_DB_PASSWORD, YOUR_DATABASE_NAME)
```
You can choose the YOUR_DATABASE_NAME freely. The module will create the database and necessary table where all trains will be stored.

4. Now you can create a TrainDelayTracker object
```python
train_delay_tracker = TrainDelayTracker(auth_data, database_config)
```

5. Track your desired train stations with the track_station() Method
```python
train_delay_tracker.track_station("Bonn")
```
6. You'll find your trains at YOUR_DATABASE_NAME.trains
![alt text](docs/db.png)

## Credits  
[deutsche_bahn_api](https://github.com/Tutorialwork/deutsche_bahn_ap)