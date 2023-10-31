import pymysql
import json
from skyfield.api import EarthSatellite, load
import boto3
import math
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

username = "test"
SAT_DATA_STRING = "5U, 00011U, 20U"
# Convert the string to a list
satellite_data = SAT_DATA_STRING.split(',')

connection = connect_to_rds()
try:
    with connection.cursor() as cursor:
        # Step 1: Get the "favSat" column for the given username
        select_query = "SELECT favSat FROM users2 WHERE username=%s"
        cursor.execute(select_query, (username,))
        result = cursor.fetchone()

        if result:
            print("exists")
            #  Combine the existing list with the new data
            existing_favSat = result["favSat"]
            existing_satellite_data = existing_favSat.split(', ')
            combined_satellite_data = existing_satellite_data  + satellite_data
            print(combined_satellite_data)
            #  Remove duplicates and create a new list
            unique_satellite_data = list(set(combined_satellite_data))

            # Update the "favSat" column with the new list
            update_query = "UPDATE users2 SET favSat=%s WHERE username=%s"
            cursor.execute(update_query, (','.join(unique_satellite_data), username))
            connection.commit()
        else:
            unique_satellite_data = satellite_data
            # Update the "favSat" column with the new list
            update_query = "UPDATE users2 SET favSat=%s WHERE username=%s"
            cursor.execute(update_query, (','.join(unique_satellite_data), username))
            connection.commit()

        ts = load.timescale()
        satellites_for_category = []
        satellite_data_json = []
        for item in unique_satellite_data: 
            select_tle_query = "SELECT * FROM tle WHERE satCat = %s"
            cursor.execute(select_tle_query, (item,))
            tle_result = cursor.fetchall()

            for row in tle_result:
                #lat = float(result['lat'])
                #lon = float(result['lng'])
                #alt = float(result['alt'])
                name = row['satName']
                satellite = EarthSatellite(row['line2'], row['line3'], row['line1'], ts=None)
                geocentric = satellite.at(ts.now())
                subpoint = geocentric.subpoint()
                if(not math.isnan(float(subpoint.latitude.degrees)) and not math.isnan(float(subpoint.longitude.degrees))):
                    satellites_for_category.extend([ float(subpoint.latitude.degrees), float(subpoint.longitude.degrees), float(subpoint.elevation.km), name])
        satellite_data_json.append(["Favorites", satellites_for_category])
    #Below is code to combine favorites with rest, not using that anymore
    '''
    s3 = boto3.client(
        's3',
        aws_access_key_id='AKIA2GBQBRJE53N4XPM3',
        aws_secret_access_key='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'
    )

    bucket_name = "satdate"
    html_file_path = "https://satdate.s3.us-east-2.amazonaws.com/satellites.json"

    # Specify the object key for the JSON file in S3
    json_file_key = "satellites.json"

    # Check if the JSON file exists in the S3 bucket
    try:
        response = s3.get_object(Bucket=bucket_name, Key=json_file_key)
        existing_json_str = response['Body'].read().decode('utf-8')
        existing_json = json.loads(existing_json_str)
    except s3.exceptions.NoSuchKey:
        # If the file doesn't exist in the bucket, initialize an empty JSON structure
        existing_json = []
    # Append the new JSON data to the existing structure
    existing_json.append(satellite_data_json[0])
    # Convert the updated JSON structure to a string
    updated_json_str = json.dumps(existing_json, indent=4)
    
    # Upload the updated JSON back to the S3 bucket
    s3.put_object(Bucket=bucket_name, Key=json_file_key, Body=updated_json_str)
    '''
    s3 = boto3.client(
        's3',
        aws_access_key_id='AKIA2GBQBRJE53N4XPM3',
        aws_secret_access_key='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'
    )

    bucket_name = "satdate"
    html_file_path = "https://satdate.s3.us-east-2.amazonaws.com/favoriteData.json"

    # Specify the object key for the JSON file in S3
    json_file_key = "favoriteData.json"
    existing_json = []
    # Append the new JSON data to the existing structure
    existing_json.append(satellite_data_json[0])
    # Convert the updated JSON structure to a string
    updated_json_str = json.dumps(existing_json, indent=4)
    
    # Upload the updated JSON back to the S3 bucket
    s3.put_object(Bucket=bucket_name, Key=json_file_key, Body=updated_json_str)

    
finally:
    connection.close()

