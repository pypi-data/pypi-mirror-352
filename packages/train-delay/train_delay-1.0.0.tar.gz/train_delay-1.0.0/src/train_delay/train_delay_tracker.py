from deutsche_bahn_api import *
from . import train_data
from .auth_data import AuthData, DatabaseConfig
import mysql.connector
import datetime 
import os, sys
import traceback


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, "..", "logs","logs.log")
ERROR_LOG_PATH = os.path.join(SCRIPT_DIR,"..","logs", "error.log")
SCHEMA_PATH = os.path.join(SCRIPT_DIR, "db", "schema.sql")

class TrainDelayTracker:

    def __init__(self, auth_data : AuthData, database_config : DatabaseConfig):
        self.api_auth = ApiAuthentication(auth_data.client_id, auth_data.client_secret)
        self.database_connection = mysql.connector.connect(host=database_config.hostname, user=database_config.user, password=database_config.password)
        self.create_database(database_config.database)


    def track_station(self, train_station_name_userinput):
        try:
            train_station_data = self.get_station_data(train_station_name_userinput) 
            self.train_station_name = train_station_data[3]
            trains_in_this_hour = self.get_trains_in_this_hour(train_station_data)
            self.to_database(trains_in_this_hour)
        except Exception as e:
            if not os.path.exists(os.path.dirname(LOG_PATH)):
                os.makedirs(os.path.dirname(LOG_PATH))
            with open(ERROR_LOG_PATH,'a') as error_log:
                print("ERROR")
                error_log.write("ERROR:\n")
                traceback.print_exc(file=error_log)

    def get_station_data(self, train_station_name):
        station_helper = StationHelper()
        found_stations_by_name = station_helper.find_stations_by_name(train_station_name)
        station_data = found_stations_by_name[0]
        return station_data
    
    def get_trains_in_this_hour(self, train_station_data):
        timetable_helper = TimetableHelper(train_station_data, self.api_auth)
        timetable = timetable_helper.get_timetable()
        trains_in_this_hour = timetable_helper.get_timetable_changes(timetable)
        return trains_in_this_hour
    
    def prepare_trains_data(self, trains_list):
        trains_list_prepared = []
        for train in trains_list:
            line = self.get_trainline(train)
            train_id = train.train_number
            first_station = self.get_first_station(train)
            last_station = train.stations.split("|")[-1]
            planned_departure = train.departure
            current_departure = self.get_current_departure(train)
            track = train.platform
            messages = self.get_train_message(train.train_changes.messages)
            train_station = self.train_station_name

            train_info = train_data.TrainData(line, train_id, first_station, last_station, planned_departure, current_departure, track, messages, train_station)
            trains_list_prepared.append(train_info)
        return trains_list_prepared

    def get_trainline(self, train):
            if hasattr(train,'train_line'):
                line = str(train.train_type) + str(train.train_line)
            else: line = str(train.train_type)
            return line
    
    def get_first_station(self, train):
            if hasattr(train, 'passed_stations'):
                first_station = train.passed_stations.split("|")[0]
            else:
                 first_station = train.stations.split("|")[0]
            return first_station
                 
    def get_current_departure(self, train):
                if hasattr(train.train_changes, 'departure'):
                    current_departure = train.train_changes.departure
                else:
                    current_departure = None
                return current_departure
    
    def get_train_message(self, message_object_list):
         message_string = ""
         for message_object in message_object_list:
              message_string += str(message_object.message)
         return message_string
         
    def to_database(self, trains_list):
         trains_data_prepared = self.prepare_trains_data(trains_list)
         database_cursor = self.database_connection.cursor()

         for train_info in trains_data_prepared:
            if self.dataset_is_new(database_cursor, train_info.planned_departure, train_info.current_departure, train_info.train_id):    
                self.add_to_database(database_cursor, train_info)
                self.database_connection.commit()
         self.log(train_info.train_station)
         
    def dataset_is_new(self, mycursor, planned_departure, current_departure, train_id):
        mycursor.execute("SELECT * FROM trains ORDER by planned_departure DESC LIMIT 10000")
        results = mycursor.fetchall()
        for result in results:
            # Format the String date to a datetime object to compare with database results
            # Incoming String: 2405162133 -> 16th May 2024 21:33
            if isinstance(planned_departure, str): # api delivers string or date for some reason
             planned_departure = datetime.datetime.strptime(planned_departure, '%y%m%d%H%M') 
            if isinstance(current_departure, str):
             current_departure = datetime.datetime.strptime(current_departure, '%y%m%d%H%M')        

            if ((str(result[2]) == str(train_id) and str(result[5]) == str(planned_departure) and str(result[6]) == str(current_departure))):
                return False
        return True    
    
    def add_to_database(self, database_cursor, train_info):
        sql = "INSERT INTO trains VALUES (DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        parameters = (train_info.line, train_info.train_id, train_info.first_station, train_info.last_station, 
                      train_info.planned_departure,train_info.current_departure, train_info.track, 
                      train_info.message, train_info.train_station)
        print("Dataset inserted: "+train_info.line+" "+train_info.train_id)
        database_cursor.execute(sql, parameters)
        
    def log(self, train_station):
        print("Finished tracking station: "+train_station+"  time: "+str(datetime.datetime.now()))
        with open(LOG_PATH,'w') as log_file:
            log_file.write("Finished tracking station: "+train_station+"  time: "+str(datetime.datetime.now())) 
        log_file.close()

    def create_database(self, database_name):
        statements = self.get_create_statements(database_name)
        for statement in statements:
            try:
                self.database_connection.cursor().execute(statement.strip())
            except mysql.connector.Error as err:
                print(f"Error while creating database: {err}")
                sys.exit(1)

    def get_create_statements(self, database_name):
        with open(SCHEMA_PATH, 'r') as schema_file:
            statements = schema_file.read()
            statements = statements.replace("{database_name}", database_name)
            statements = statements.split(';')
            return statements
