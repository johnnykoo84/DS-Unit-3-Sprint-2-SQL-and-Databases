import pandas as pd
import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
import numpy as np

import pymongo
import os

load_dotenv()
print(__file__)
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)

# load csv to dataframe
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'titanic.csv')
df = pd.read_csv(CSV_FILE_PATH)

# take care of env
psq_dbname = os.getenv('dbname')
psq_user = os.getenv('user')
psq_password = os.getenv('password')
psq_host = os.getenv('host')

mongo_username = os.getenv('mongo_username')
mongo_password = os.getenv('mongo_password')
mongo_host = os.getenv('mongo_host')

# Connect to ElephantSQL-hosted PostgreSQL
psq_conn = psycopg2.connect(
    dbname=os.getenv("dbname"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    host=os.getenv("host")
)
# A "cursor", a structure to iterate over db records to perform queries
cur = psq_conn.cursor()

# Drop the table if exist
cur.execute('DROP TABLE IF EXISTS Titanic;')

# CREATE TABLE query
query_create = """CREATE TABLE Titanic (
    Survived            INT,
    Pclass              INT,
    Name                varchar(120),
    Sex                 varchar(10),
    Age                 INT,
    SiblingsSpouses     INT,
    ParentsChildren     INT,
    Fare                INT);
"""
cur.execute(query_create)

# insert data
list_of_tuples = list(df.to_records(index=False))
ins_query = 'INSERT INTO Titanic (Survived, Pclass, Name, Sex, Age, SiblingsSpouses, ParentsChildren, Fare) VALUES %s;'
extras.execute_values(cur, ins_query, list_of_tuples)

psq_conn.commit()

# check
cur.execute('SELECT * FROM Titanic')
psql_result = cur.fetchall()
# print('second fetch', psql_result)
# print('type psql_result', type(psql_result))

# for mongoDB
client = pymongo.MongoClient(
    f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_host}/test?retryWrites=true&w=majority")
db = client.test

list_data = []

for row in psql_result:
    obj = {
        'survived': row[0],
        'pclass': row[1],
        'name': row[2],
        'sex': row[3],
        'age': row[4],
        'siblings_spouse_aboard': row[5],
        'parents_children_abord': row[6],
        'Fare': row[7],
    }
    list_data.append(obj)
db['Titanic'].drop()
db.create_collection('Titanic')
db['Titanic'].insert_many(list_data)

cursor = db['Titanic'].find({})

# for document in cursor:
#     print('result', document)

# - How many passengers survived, and how many died?
cursor = db['Titatnic'].find({
    'survived': 1
})
print('@@', cursor.count())

# - How many passengers were in each class?
# - How many passengers survived/died within each class?
# - What was the average age of survivors vs nonsurvivors?
# - What was the average age of each passenger class?
# - What was the average fare by passenger class? By survival?
# - How many siblings/spouses aboard on average, by passenger class? By survival?
# - How many parents/children aboard on average, by passenger class? By survival?
# - Do any passengers have the same name?
# - (Bonus! Hard, may require pulling and processing with Python) How many married
#   couples were aboard the Titanic? Assume that two people (one `Mr.` and one
#   `Mrs.`) with the same last name and with at least 1 sibling/spouse aboard are
#   a married couple.
