import os
os.chdir("/home/ubuntu/ecen403/ecen403/sqlUpdateValidate")
import requests  # Connect to space-track.com
from scrapy import Selector  # Scrape the TLE.txt


def download_bulk_TLE(sess, headers, url):
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

    #Clear starlink file
    file_path = "tle/starlinkTLE.txt"
    with open(file_path, 'w') as file:
        pass  # This does nothing, but it ensures the file is truncated

    #Clear oneweb file
    file_path = "tle/onewebTLE.txt"
    with open(file_path, 'w') as file:
        pass  # This does nothing, but it ensures the file is truncated

    #Clear thorad file
    file_path = "tle/thoradTLE.txt"
    with open(file_path, 'w') as file:
        pass  # This does nothing, but it ensures the file is truncated
    while i < len(tle_lines):
        line = tle_lines[i]
        if line.startswith("0 TBA"):
            del tle_lines[i:i+3]  # Remove the current line and the two following lines
        elif "STARLINK" in line:
            starlink_block = "\n".join(tle_lines[i:i+3])
            if starlink_block.strip():  # Check if the block is not empty
                with open("tle/starlinkTLE.txt", "a") as starlink_file:
                    starlink_file.write(starlink_block + "\n")
            #del tle_lines[i:i+3]  # Remove the current line and the two following lines
            i += 1
        elif "ONEWEB" in line:
            oneweb_block = "\n".join(tle_lines[i:i+3]).strip()
            if oneweb_block.strip():  # Check if the block is not empty
                with open("tle/onewebTLE.txt", "a") as oneweb_file:
                    oneweb_file.write(oneweb_block + "\n")
            #del tle_lines[i:i+3]  # Remove the current line and the two following lines
            i += 1
        elif "THORAD" in line:
            thorad_block = "\n".join(tle_lines[i:i+3]).strip()
            if thorad_block.strip():  # Check if the block is not empty
                with open("tle/thoradTLE.txt", "a") as thorad_file:
                    thorad_file.write(thorad_block + "\n")
            #del tle_lines[i:i+3]  # Remove the current line and the two following lines
            i += 1
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
    return iter(modified_tle_content.split("\n"))  #return the lines


def download_LEO(sess, headers, url):
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
    file_path = os.path.join(folder_name, "LEOtle1.txt")

    # Write the modified content to the file
    with open(file_path, "w") as file:
        file.write(modified_tle_content)

    # opening and creating new .txt file
    with open("tle/LEOtle1.txt", 'r') as r, open('tle/LEOtle.txt', 'w') as o:
        for line in r:
            if line.strip():
                o.write(line)

    # Check if the file exists before attempting to delete
    if os.path.exists("tle/LEOtle1.txt"):
        # Delete the file
        os.remove("tle/LEOtle1.txt")
        print("File 'LEOtle1.txt' has been deleted.")
    else:
        print("File 'LEOtle1.txt' does not exist.")

    print("LEO TLE content has been saved to 'tle/LEOtle.txt'")
    return iter(modified_tle_content.split("\n"))  #return the lines    


def download_MEO(sess, headers, url):
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
    file_path = os.path.join(folder_name, "MEOtle1.txt")

    # Write the modified content to the file
    with open(file_path, "w") as file:
        file.write(modified_tle_content)

    # opening and creating new .txt file
    with open("tle/MEOtle1.txt", 'r') as r, open('tle/MEOtle.txt', 'w') as o:
        for line in r:
            if line.strip():
                o.write(line)

    # Check if the file exists before attempting to delete
    if os.path.exists("tle/MEOtle1.txt"):
        # Delete the file
        os.remove("tle/MEOtle1.txt")
        print("File 'MEOtle1.txt' has been deleted.")
    else:
        print("File 'MEOtle1.txt' does not exist.")

    print("MEO TLE content has been saved to 'tle/MEOtle.txt'")
    return iter(modified_tle_content.split("\n")) #return the lines    


def GET_starlink_lines():
    # Open the file for reading
    with open("tle/starlinkTLE.txt", "r") as file:
        # Read the lines from the file
        lines = file.readlines()

    # Filter out empty lines
    filtered_lines = [line.strip() for line in lines if line.strip()]

    # Create a line iterator
    line_iterator = iter(filtered_lines)
    return line_iterator

def GET_oneweb_lines():
    # Open the file for reading
    with open("tle/onewebTLE.txt", "r") as file:
        # Read the lines from the file
        lines = file.readlines()

    # Filter out empty lines
    filtered_lines = [line.strip() for line in lines if line.strip()]

    # Create a line iterator
    line_iterator = iter(filtered_lines)
    return line_iterator

def GET_thorad_lines():
    # Open the file for reading
    with open("tle/thoradTLE.txt", "r") as file:
        # Read the lines from the file
        lines = file.readlines()

    # Filter out empty lines
    filtered_lines = [line.strip() for line in lines if line.strip()]

    # Create a line iterator
    line_iterator = iter(filtered_lines)
    return line_iterator
