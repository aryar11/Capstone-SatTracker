import pyodbc
import requests  # Connect to space-track.com
from scrapy import Selector  # Scrape the TLE.txt
import os  # To access and write to the tle folder
import datetime #To time script



def main():
    os.chdir("/home/pi/satTrack")  #Change working directory to current folder

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

    #######Download TLE########
    print("Downloading 3le")
    url = "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le"

    
    r = sess.get(url, headers={"User-Agent": headers.get("User-Agent")})
    if r.status_code == requests.codes.ok:
        print("Request successful")
    else:
        print(f"Request failed with status code {r.status_code}")

    # Store the TLEs content in a variable
    tle_content = r.content

    # Remove all lines starting from the first line that starts with "0 TBA"
    tle_lines = tle_content.decode().split("\n")
    i = 0
    while i < len(tle_lines):
        if tle_lines[i].startswith("0 TBA"):
            del tle_lines[i:i+3]  # Remove the current line and the two following lines
        else:
            i += 1

    # Join the modified lines to form the new content
    modified_tle_content = "\n".join(tle_lines)

    ####################################
    #######Save TLE text file###########
    ####################################

    # Specify the folder name
    folder_name = "tle"

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    # Define the file path inside the folder
    file_path = os.path.join(folder_name, "tle1.txt")

    # Write the modified content to the file
    with open(file_path, "w") as file:
        file.write(modified_tle_content)



    # opening and creating new .txt file
    with open("tle/tle1.txt", 'r') as r, open('tle/tle.txt', 'w') as o:
        for line in r:
        
            if line.strip():
                o.write(line)

    # Check if the file exists before attempting to delete
    if os.path.exists("tle/tle1.txt"):
        # Delete the file
        os.remove("tle/tle1.txt")
        print("File 'tle1.txt' has been deleted.")
    else:
        print("File 'tle1.txt' does not exist.")

    print("TLE content has been saved to 'tle/tle.txt'")


    # Split the content into lines
    tle_lines = modified_tle_content.split("\n")

    # Create an iterator to iterate over the lines for the for loop in the connection part of the code
    line_iterator = iter(tle_lines)

    ######################################
    ###########Import to SQL##############
    ######################################
    # Connection string
    server = 'satellitetrack.database.windows.net'
    database = 'satellite-track-website'
    username = 'CloudSA007076c9'
    password = 'SatTrack2023!'
    driver = 'FreeTDS'  # Make sure the driver is installed

    # Establish connection
    conn_str = f"DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password};TDS_Version=8.0;"
    conn = pyodbc.connect(conn_str)

    # Create a cursor
    cursor = conn.cursor()

    ####Clearing table####
    try:
        # Execute the query
        print("Clearing table")
        cursor.execute("DELETE FROM dbo.tle")
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
        query = "INSERT INTO dbo.tle (satName, satCat, intlDesignator, elSetEpoch, firstTimeDeriv, secondTimeDeriv, bDragTerm, elSetType, elementNum, orbitInclination, rightAscending, eccentricity, perigee, anomaly, meanMotion, satOrder) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
    with open('/home/pi/satTrack/timeToUpdate.txt', 'w') as file:
        file.write('')


    # Save minutes and seconds to the file.
    with open('/home/pi/satTrack/timeToUpdate.txt', 'w') as file:
        file.write(f'{minutes} minutes and {seconds} seconds')

    #Call sql_validate.py and pass the time taken as an argument.
    
    #try:
    #    subprocess.run(["python3", "/home/pi/satTrack/sql_validate.py", f"{int(minutes)}m {int(seconds)}s"])
    #except Exception as e:
    #    print("Error running sql_validate.py:", e)