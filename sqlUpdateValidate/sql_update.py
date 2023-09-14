import pyodbc
import requests  # Connect to space-track.com
from scrapy import Selector  # Scrape the TLE.txt
import os  # To access and write to the tle folder
import datetime #To time script
import tle_download

def importToSQL(line_iterator, tableName):
    # Connection string
    server = 'tcp:satellitetrack.database.windows.net,1433'
    database = 'satellite-track-website'
    username = 'CloudSA007076c9'
    password = 'SatTrack2023!'
    driver = '{ODBC Driver 17 for SQL Server}'  # Make sure the driver is installed

    # Establish connection
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    conn = pyodbc.connect(conn_str)

    # Create a cursor
    cursor = conn.cursor()

    ####Clearing table####
    try:
        # Execute the query
        print("Clearing table")
        cursor.execute("DELETE FROM " + tableName)
        conn.commit()

    except Exception as e:
        print("Error executing query:", e)


    values = []
    satOrder = 0
    # Loop through every three lines
    for line1, line2, line3 in zip(line_iterator, line_iterator, line_iterator):
        # Split line 1
        line1_split = line1.split()
        #get name
        satName = ' '.join(line1_split[1:])

        #split line 2
        line2_split = line2.split()
        #assign values
        satCat = line2_split[1]
        intlDesignator = line2_split[2]
        elSetEpoch = line2_split[3]
        firstTimeDeriv = line2_split[4]
        secondTimeDeriv = line2_split[5]
        bDragTerm  = line2_split[6]
        elSetType = line2_split[7]
        elementNum = line2_split[8]

        #split line 3
        line3_split = line3.split()
        #assign values in 3rd line
        orbitInclination = line3_split[2]
        rightAscending = line3_split[3]
        eccentricity = line3_split[4]
        perigee = line3_split[5]
        anomaly = line3_split[6]
        meanMotion = line3_split[7]

        values = [satName, satCat, intlDesignator, elSetEpoch, firstTimeDeriv, secondTimeDeriv, bDragTerm, elSetType, elementNum, orbitInclination, rightAscending, eccentricity, perigee, anomaly, meanMotion, satOrder]
        query = "INSERT INTO " + tableName + " (satName, satCat, intlDesignator, elSetEpoch, firstTimeDeriv, secondTimeDeriv, bDragTerm, elSetType, elementNum, orbitInclination, rightAscending, eccentricity, perigee, anomaly, meanMotion, satOrder) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        satOrder +=1
        try:
            # Execute the query
            print("executing: ", values[0])
            cursor.execute(query, values) 

        except Exception as e:
            print("Error executing query:", e)

    print("Commiting Inserts...")
    conn.commit()
    cursor.close()
    conn.close() 
    print("Done commiting")




def main():
    #os.chdir("/home/pi/satTrack")  #Change working directory to current folder

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
    importToSQL(bulk_TLE_lines, "dbo.tle")
    importToSQL(leo_TLE_lines, "dbo.LEO")
    #importToSQL(meo_TLE_lines, "dbo.MEO")   ##not yet a table
    importToSQL(starlink_TLE_lines, "dbo.starlink")
    importToSQL(thorad_TLE_lines, "dbo.thorad")
    importToSQL(oneweb_TLE_lines, "dbo.oneweb")
    
if __name__ == "__main__":
    #tore the start time just before updating sql
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