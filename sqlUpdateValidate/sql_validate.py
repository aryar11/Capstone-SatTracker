import pyodbc
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import sys
import os
def sendEmail(message):
    #To and from email addresses
    from_address = "satellitetrackstatus@gmail.com"
    to_addresses = ["aryarahmanian@tamu.edu","stuartk01@tamu.edu", "kholley@tamu.edu"]

    # Create message container 
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "SatTrack SQL Update"
    msg['From'] = from_address
    msg['To'] = ','.join(to_addresses)

    # Create the message (HTML).
    html = message

    # Record the MIME type - text/html.
    part1 = MIMEText(html, 'html')

    # Attach parts into message container
    msg.attach(part1)

    # Credentials
    username = "satellitetrackstatus@gmail.com"
    password = 'igoybdtrrzztdfkk'

    # Sending the email
    ## note - this smtp config worked for me, I found it googling around, you may have to tweak the # (587) to get yours to work
    server = smtplib.SMTP('smtp.gmail.com', 587) 
    server.ehlo()
    server.starttls()
    server.login(username,password)  
    server.sendmail(from_address, to_addresses, msg.as_string())  
    server.quit()


def main(duration):
    os.chdir("/home/pi/satTrack/") #Change directory when running on Rasp Pi
    # SQL Connection string
    server = 'satellitetrack.database.windows.net'
    database = 'satellite-track-website'
    username = 'CloudSA007076c9'
    password = 'SatTrack2023!'
    driver = 'FreeTDS'  # Make sure the driver is installed

    # Establish connection to SQL
    conn_str = f"DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password};TDS_Version=8.0;"
    conn = pyodbc.connect(conn_str) 

    # Create a cursor
    cursor = conn.cursor()

    # execute your query
    cursor.execute("WITH CTE AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY satOrder ORDER BY (SELECT NULL)) AS rn FROM [dbo].[tle] ) SELECT * FROM CTE WHERE rn = 1; ")
      
    # fetch all the matching rows 
    result = cursor.fetchall()

    badActorSatellites = []
    notEqual = False
    # Create a line iterator to read the file
    with open("/home/pi/satTrack/tle/tle.txt", "r") as file:

        # Loop through every three lines
        for (line1, line2, line3), row in zip(zip(file, file, file), result):
            ######Line Processing and Grouping into lines of 3######
            line1 = line1.strip()
            line2 = line2.strip()
            line3 = line3.strip()
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

            #Put all values in a list to place into SQL
            values = [satCat, intlDesignator, float(elSetEpoch), float(firstTimeDeriv), secondTimeDeriv, bDragTerm, int(elSetType), int(elementNum), float(orbitInclination), float(rightAscending), int(eccentricity), float(perigee), float(anomaly), float(meanMotion), satName]
            values[3] = float(format(values[3], ".3e")) #Round off firstTimeDeriv since SQL rounds and creates mismatches

            row[3] =  float(format(values[3], ".3e"))
            row_without_last = row[:-2]

            if all(val1 == val2 for val1, val2 in zip(values, row_without_last)):
                continue
            else:
                print(f"{satName} is not equal")

                badActorSatellites.append(satName)
                notEqual = True

    cursor.close()
    conn.close()

    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("Emailing...")
    
    #Read the time saved from sql_update to timeToUpdate
    with open('/home/pi/satTrack/timeToUpdate.txt', 'r') as file:
        duration_line = file.readline().strip()

    
    
    ######Send Email depend on successful SQL table upload########
    if notEqual:
        message = f"Good Morning, it's {dt_string}. The SatTrack SQL update seemed to have a few incorrect uploads. Time to complete: " +  duration_line  + " Here they are: \n \n"
        message += f"{badActorSatellites[0]}\n"
        for satellite in badActorSatellites[1:]:
            message += f", {satellite}\n"
        sendEmail(message)
    else:
        message = f"Good Morning, it's {dt_string}. The SatTrack SQL update went as planned with no incorrect uploads. Time to complete: " +  duration_line  + " Have a good day!"
        sendEmail(message)

if __name__ == "__main__":
    print("In sql_validate")
    #if len(sys.argv) < 2:
     #   print("Usage: python sql_validate.py <duration>")
     #   sys.exit(1)

    #duration = sys.argv[1]

    # use the 'duration' variable from sql_update
    #print("Duration from parent script:", duration)

    #main(duration)
    main(0)