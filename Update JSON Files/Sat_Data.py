                                                                                                                       
import pymysql
import json
from skyfield.api import EarthSatellite, Topos, load
import boto3
import math
import time
from datetime import timedelta

def connect_to_rds():
    connection = pymysql.connect(
        host='sattrack.ckiq4qoeqhbu.us-east-2.rds.amazonaws.com',
        user='admin',
        password='SatTracker23',
        db='SatTracker',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
def fetch_tles():
    satellite_data = []  # Create an empty list to store all satellite data
    connection = connect_to_rds()
    try:
        with connection.cursor() as cursor:
            # List of tables representing satellite categories
            satellite_tables = ["tle", "LEO", "MEO", "oneweb", "starlink", "thorad"]
            ts = load.timescale()
            for table_name in satellite_tables:
                sql_query = f"SELECT lat, lng, alt, satName, line1, line2, line3 FROM SatTracker.{table_name} LIMIT 10001"
                cursor.execute(sql_query)
                results = cursor.fetchall()
                satellites_for_category = []

                for result in results:
                    lat = float(result['lat'])
                    lon = float(result['lng'])
                    alt = float(result['alt'])
                    name = result['satName']
                    satellite = EarthSatellite(result['line2'], result['line3'], result['line1'], ts=None)
                    geocentric = satellite.at(ts.now() + timedelta(seconds = 30)) #plotting for 30 seconds in the future to compensate for script runtime
                    subpoint = geocentric.subpoint()
                    #Confirm no Invalid numbers are being passed
                    if(not math.isnan(float(subpoint.latitude.degrees)) and not math.isnan(float(subpoint.longitude.degrees))):
                        satellites_for_category.extend([ float(subpoint.latitude.degrees), float(subpoint.longitude.degrees), float(subpoint.elevation.km), name])
                satellite_data.append([table_name, satellites_for_category])

        # Output to a JSON file
        with open("satellites.json", "w") as json_file:
            json.dump(satellite_data, json_file, indent=4)
        #####Importing to bucket######
        s3 = boto3.client(
            's3',
            aws_access_key_id='AKIA2GBQBRJE53N4XPM3',
            aws_secret_access_key='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'
        )
        bucket_name = "satdate"
        html_file_path = "https://satdate.s3.us-east-2.amazonaws.com/satellites.json"

        #upload the HTML to S3 aws
        s3.upload_file('satellites.json', bucket_name, 'satellites.json')
    finally:
        connection.close()
start = time.time()
fetch_tles()
end = time.time()
print(end-start)
