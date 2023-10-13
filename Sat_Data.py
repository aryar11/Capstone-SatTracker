import pymysql
import json

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
            
            for table_name in satellite_tables:
                sql_query = f"SELECT lat, lng, alt, satName FROM SatTracker.{table_name} LIMIT 10000"
                cursor.execute(sql_query)
                results = cursor.fetchall()
                satellites_for_category = []

                for result in results:
                    lat = float(result['lat'])
                    lon = float(result['lng'])
                    alt = float(result['alt'])
                    name = result['satName']
                    satellites_for_category.extend([lat, lon, alt, name])

                satellite_data.append([table_name, satellites_for_category])

        # Output to a JSON file
        with open("satellites.json", "w") as json_file:
            json.dump(satellite_data, json_file, indent=4)

    finally:
        connection.close()

fetch_tles()
