from pymongo import MongoClient
import os


MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")


def get_database():
   client = MongoClient(MONGODB_CONNECTION_STRING)
   print(client)
 
   # Create the database for our example (we will use the same database throughout the tutorial
   return client["py_auth_app"]
  
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
   dbname = get_database()
