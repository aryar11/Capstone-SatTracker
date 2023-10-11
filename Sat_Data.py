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
    satellite_data = []
    connection = connect_to_rds()
    try:
        with connection.cursor() as cursor:
            # List of tables representing satellite categories
            satellite_tables = ["LEO", "MEO", "oneweb", "starlink", "thorad", "tle"]
            
            for table_name in satellite_tables:
                satellites_for_category = []
                sql_query = f"SELECT lat, lng, alt, satName FROM SatTracker.{table_name} LIMIT 1" #cange 1 to whatever you want
                
                cursor.execute(sql_query)
                
                results = cursor.fetchall()
                for result in results:
                    for result in results:
                     lat = float(result['lat'])   #LEO is stored as strings, covert to floats
                     lon = float(result['lng'])
                     alt = float(result['alt'])
                    name = result['satName']
                    entry = [lat, lon, alt, name]
                    satellites_for_category.append(entry)


                satellite_data.append([table_name] + satellites_for_category) #removes extra bracket from the list


        # Output to a JSON file
        with open("satellites.json", "w") as json_file:
            json_file.write('[')  # Start of the main list
            for category_data in satellite_data:
                category_name = category_data[0]
                satellites = category_data[1]

                # Write the category name
                json_file.write(f'\n["{category_name}",')
                
                # Write all satellites for this category in a single line
                json_file.write(json.dumps(satellites))

                # Add a comma to separate from the next category (if there is one)
                if category_data != satellite_data[-1]:
                    json_file.write('],')
                else:
                    json_file.write(']')
            json_file.write('\n]')  # End of the main list

    finally:
        connection.close()

fetch_tles()


