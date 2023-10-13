import os
#os.chdir("/home/ubuntu/ecen403/ecen403/sqlUpdateValidate")
import pyodbc
import requests  # Connect to space-track.com
from scrapy import Selector  # Scrape the TLE.txt
import datetime #To time script
import tle_download
import mysql.connector
from skyfield.api import EarthSatellite, Topos, load
def importToSQL(line_iterator, tableName):
    host = 'sattrack.ckiq4qoeqhbu.us-east-2.rds.amazonaws.com'
    database = 'SatTracker'
    username = 'admin'
    password = 'SatTracker23'

    try:
        connection = mysql.connector.connect(host=host, user=username, password=password, database=database)
        cursor = connection.cursor()

        print("Connected to the database")

        #### Clearing table ####
        try:
            # Execute the query
            print("Clearing table")
            cursor.execute("DELETE FROM " + tableName)
            connection.commit()

        except Exception as e:
            print("Error executing query:", e)

        values = []
        satOrder = 0
        ts = load.timescale()
        # Loop through every three lines
        for line1, line2, line3 in zip(line_iterator, line_iterator, line_iterator):
            # Split line 1
            line1_split = line1.split()
            # get name
            satName = ' '.join(line1_split[1:])

            # split line 2
            line2_split = line2.split()
            # assign values
            satCat = line2_split[1]
            intlDesignator = line2_split[2]
            elSetEpoch = line2_split[3]
            firstTimeDeriv = line2_split[4]
            secondTimeDeriv = line2_split[5]
            bDragTerm = line2_split[6]
            elSetType = line2_split[7]
            elementNum = line2_split[8]

            # split line 3
            line3_split = line3.split()
            # assign values in 3rd line
            orbitInclination = line3_split[2]
            rightAscending = line3_split[3]
            eccentricity = line3_split[4]
            perigee = line3_split[5]
            anomaly = line3_split[6]
            meanMotion = line3_split[7]

            #Getting lat long and altitude
            satellite = EarthSatellite(line2, line3, line1, ts=None)
            geocentric = satellite.at(ts.now())
            subpoint = geocentric.subpoint()
            # Location on Earth (latitude, longitude, altitude)
            latitude = float(subpoint.latitude.degrees)
            longitude = float(subpoint.longitude.degrees)
            altitude = float(subpoint.elevation.km)
            query = """
            INSERT INTO {} (satName, satCat, intlDesignator, elSetEpoch, firstTimeDeriv, secondTimeDeriv, bDragTerm, elSetType, elementNum, orbitInclination, rightAscending, eccentricity, perigee, anomaly, meanMotion, satOrder, lat, lng, alt, line1, line2, line3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """.format(tableName)

            # Values to insert into the table as a tuple
            values = (satName, satCat, intlDesignator, elSetEpoch, firstTimeDeriv, secondTimeDeriv, bDragTerm, elSetType, elementNum, orbitInclination, rightAscending, eccentricity, perigee, anomaly, meanMotion, satOrder, latitude, longitude, altitude, line1, line2, line3)
            
            try:
                # Execute the query
                #print("executing: ", satName)
                cursor.execute(query, values)
            except Exception as e:
                print("Error executing query:", e)
            satOrder += 1
        print("Committing Inserts...")
        connection.commit()
        cursor.close()
        connection.close()
        print("Done committing")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    ##################################################
    ##Connect to Space-track.org and download TLE#####
    ##################################################
    LOGIN_URL = "https://www.space-track.org/auth/login"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.space-track.org",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    #Login Information
    payload = "spacetrack_csrf_token={}&identity=arya.r11223%40gmail.com&password=Password123456%21&btnLogin=LOGIN"
    #Use Request libraru to connect to webpage
    sess = requests.session()  
    r = sess.get(LOGIN_URL, headers={"User-Agent": headers.get("User-Agent")})
    response = Selector(text=r.content)
    csrf_token = response.xpath("//input[@name='spacetrack_csrf_token']/@value").get()
    sess.post(LOGIN_URL, headers=headers, data=payload.format(csrf_token))

    #######Download Bulk TLE########
    print("Downloading 3le")

    bulk_TLE_lines = tle_download.download_bulk_TLE(sess, headers, "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le")

    leo_TLE_lines =  tle_download.download_LEO(sess,  headers, "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/MEAN_MOTION/%3E11.25/ECCENTRICITY/%3C0.25/OBJECT_TYPE/payload/orderby/NORAD_CAT_ID,EPOCH/format/3le")
 
    meo_TLE_lines =  tle_download.download_MEO(sess,  headers, "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/MEAN_MOTION/1.8--2.39/ECCENTRICITY/%3C0.25/OBJECT_TYPE/payload/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    
    starlink_TLE_lines = tle_download.GET_starlink_lines()
    thorad_TLE_lines = tle_download.GET_thorad_lines()
    oneweb_TLE_lines = tle_download.GET_oneweb_lines()

    ######################################
    ###########Import to SQL##############
    ######################################
    print("Updating TLE...")
    importToSQL(bulk_TLE_lines, "tle")
    print("Updating LEO...")
    importToSQL(leo_TLE_lines, "LEO")
    print("Updating MEO...")
    importToSQL(meo_TLE_lines, "MEO")  
    print("Updating starlink...")
    importToSQL(starlink_TLE_lines, "starlink")
    print("Updating thorad...")
    importToSQL(thorad_TLE_lines, "thorad")
    print("Updating oneweb...")
    importToSQL(oneweb_TLE_lines, "oneweb")
    
if __name__ == "__main__":
   
	 #store the start time just before updating sql
    start_time = datetime.datetime.now()

    main()

    #Store the end time just after the main() function finishes execution.
    end_time = datetime.datetime.now()
        
    # Calculate the time taken (duration) in seconds.
    duration_seconds = (end_time - start_time).total_seconds()


    # Convert duration to minutes and seconds.
    minutes = int(duration_seconds // 60)  # Get the whole number of minutes
    seconds = int(round(duration_seconds % 60))  # Get the whole number of seconds

    # If seconds reach 60 or more due to rounding, adjust the minutes and seconds accordingly
    if seconds >= 60:
        minutes += 1
        seconds = 0

    print(f"Duration: {minutes} minutes and {seconds} seconds")


    # Clear the contents of the file from last update
    with open('timeToUpdate.txt', 'w') as file:
        file.write('')


    # Save minutes and seconds to the file.
    with open('timeToUpdate.txt', 'w') as file:
        file.write(f'{minutes} minutes and {seconds} seconds')

    #Call sql_validate.py and pass the time taken as an argument.
    
    #try:
    #    subprocess.run(["python3", "/home/pi/satTrack/sql_validate.py", f"{int(minutes)}m {int(seconds)}s"])
    #except Exception as e:
    #    print("Error running sql_validate.py:", e)
