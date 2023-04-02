import os
import requests
import json
import psycopg2

# Download the JSON file from the web
url = 'https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/collection.json'  # Replace with the actual URL of the JSON file
response = requests.get(url)
data = response.json()

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host='db',
    port='5432'
)
cursor = conn.cursor()

# Insert the JSON data into the 'collections' table
insert_query = '''
    INSERT INTO collections (content)
    VALUES (%s)
    ON CONFLICT (id)
    DO UPDATE SET
        content = EXCLUDED.content;  
'''
cursor.execute(insert_query, (json.dumps(data),))

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()
