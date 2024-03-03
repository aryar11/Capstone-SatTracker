# For measuring script execution time
import time
start_time = time.time()

import numpy as np

# For reading NetCDF data
from netCDF4 import Dataset #Network Common Data Form, needed to read the mesh file

# For creating 3D plots
import plotly.graph_objs as go
from plotly.offline import plot

# For parsing TLE set and calc. satellite position
from skyfield.api import load, EarthSatellite

#for API request for validation
import requests
import json
import boto3
#For geolocation
import googlemaps
gmaps = googlemaps.Client(key='AIzaSyDylyC2otrMcdv4i7BGajUbetqbS0-k1ho')



# Define the Satellite class 
class Satellite:
    def __init__(self, name, TLE1, TLE2): #Can break it up into the name and TLE Lines
        self.name = name
        self.TLE1 = TLE1
        self.TLE2 = TLE2
        self.ts=load.timescale()  # Loading time scale for posiion computation
        self.sat = EarthSatellite(TLE1, TLE2, name)  # Initialize EarthSatellite object with TLE data

    def update_position(self):
        t = self.ts.now()  # Get current time
        subpoint = self.sat.at(t).subpoint() #Subpoint it the point directl under the sat
        self.latitude = subpoint.latitude.degrees  # Get the latitude of the subpoint
        self.longitude = subpoint.longitude.degrees  # Get the longitude of the subpoint
        self.altitude = subpoint.elevation.km  # Get the altitude of the satellite above the Earth
        
        #"A": Main payload or primary mission.
        #"B": First secondary payload or the first object associated with the main payload, such as a booster or debris.
        #"C": Second secondary payload or object, and so on.

    def get_position(self):
        self.update_position()  # Update the satellite's position
        return self.longitude, self.latitude, self.altitude # Return the updated position


#Function to get the position data for all satellites and map them to 3D coordinates on the sphere
def satellite_positions_on_sphere(satellites):
    
    max_altitude_for_plotting = 1000 #Need a max alt for plotting. if something is really far out, if zooms out the graph

    for satellite in satellites:
        satellite.update_position()  # Update each satellite's position

    lats = [sat.latitude for sat in satellites]  # Collect lat, lon and alt 
    lons = [sat.longitude for sat in satellites]  
    alts = [sat.altitude for sat in satellites]  
    alts_capped = [min(alt, max_altitude_for_plotting) for alt in alts]  # Apply the cap to altitudes for plotting
    names = [sat.name for sat in satellites] 

    xs, ys, zs = mapping_map_to_sphere(lons, lats, alts_capped)  # Map lon, lat, alt to 3D coordinates with capped altitudes
    
    ratio = 1.3 - np.array(alts_capped)*2e-4
    xs_3d = xs * ratio
    ys_3d = ys * ratio
    zs_3d = zs * ratio

    # Create a list of text strings to be displayed when hovering over the sat
    # Use zip to concant and do one sat per line
    # This is a f string 
    hovertext = [f"{name}<br>Lat: {lat:.2f} Degrees, Lon: {lon:.2f} Degrees, <br>Alt: {alt:.2f} km" for name, lat, lon, alt in zip(names, lats, lons, alts)]   # Use original alts here
  
    
    # Create a dict to hold data for sat location
    #scatter3d is best
    sat_sphere = dict(
        type='scatter3d',
        mode='markers',
        x=xs_3d,
        y=ys_3d,
        z=zs_3d,
        marker=dict(
            size=3,
            color=sat_colors),
        
        text=hovertext,  # Assign hover text
        hoverinfo='text',
        name="Satellites"
    )

    return sat_sphere  # Return the scatter3d data for the satellite markers



def get_user_location():
    # Get geolocation info
    geolocation_result = gmaps.geolocate()

    # Extract latitude and longitude
    if 'location' in geolocation_result:
        return geolocation_result['location']['lat'], geolocation_result['location']['lng']
    else:
        raise Exception("Unable to retrieve user's location.") #if no connectipn or incorrect format, flag

        
#Haverine Formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
    return distance



def closest_satellite(satellites, user_latitude, user_longitude):
    closest_distance = float('inf') #set at infinity
    closest_satellite = None

    for satellite in satellites:
        satellite.update_position()
        satellite_latitude = satellite.latitude
        satellite_longitude = satellite.longitude
        
        # Calculate the distance between the user and the current satellite
        distance = calculate_distance(user_latitude, user_longitude, satellite_latitude, satellite_longitude)

        # Update the closest satellite if the current one is closer
        if distance < closest_distance:
            closest_distance = distance
            closest_satellite = satellite
            
    
    return closest_satellite

# Function to read ETOPO1 topographic data, select a specific region, and prepare the data for 3D plotting
def Etopo(lon_area, lat_area, resolution):
    # Input: resolution, lon_area, lat_area
    # Output: Mesh type longitude, latitude, and topography data
    
    # Read NetCDF data
    data = Dataset("ETOPO1_Ice_g_gdal.grd", "r") #This data set contains gridded dataset covering the globe. Each grid includes
    #Elevation, longitude and latitude. Can combine every grid for the globe
  
    # Get data from the set and store it
    lon_range = data.variables['x_range'][:] #Get lon data from the set and store it
    lat_range = data.variables['y_range'][:]
    topo_range = data.variables['z_range'][:] #Elevation range for the set
    spacing = data.variables['spacing'][:] #Spacing between the grids
    dimension = data.variables['dimension'][:] #Number of points in the dataset
    z = data.variables['z'][:] #Actual elevation of the grid points
    lon_num = dimension[0] #1st dimmensions of mesh grid 
    lat_num = dimension[1]
    
    # Need to store the lon, lat data with the spacing now
    lon_input = np.zeros(lon_num); lat_input = np.zeros(lat_num)
    for i in range(lon_num):
        lon_input[i] = lon_range[0] + i * spacing[0]
    for i in range(lat_num):
        lat_input[i] = lat_range[0] + i * spacing[1]

    # Create 2D array of lon and lat with the spacing for the plot
    lon, lat = np.meshgrid(lon_input, lat_input) #np.meshgrid takes two arrays and combines them 
    
    # Convert 2D array from 1D array for z value
    topo = np.reshape(z, (lat_num, lon_num)) #Reshapes the elevation using the dimensions for lon and lat arrays so everthing is the same size
    
    # Skip the data for resolution, don't need everypoint. Everypoint makes my computer crash
    if ((resolution < spacing[0]) | (resolution < spacing[1])):
        print('Set the highest resolution')
    else:
        skip = int(resolution/spacing[0])
        lon = lon[::skip,::skip]
        lat = lat[::skip,::skip]
        topo = topo[::skip,::skip]
    
    topo = topo[::-1] #Conventional matrix 0,0 and geographic 0,0 are differently indexed, bottom and top left corner
    
    # Select the range of map
    range1 = np.where((lon>=lon_area[0]) & (lon<=lon_area[1]))  #This gets the range of lon, lat and alt that fall within the limits of the globe 
    lon = lon[range1]; lat = lat[range1]; topo = topo[range1]
    range2 = np.where((lat>=lat_area[0]) & (lat<=lat_area[1]))
    lon = lon[range2]; lat = lat[range2]; topo = topo[range2]
    
    # Convert 2D again because the process above gives 1d arrays
    lon_num = len(np.unique(lon))
    lat_num = len(np.unique(lat))
    lon = np.reshape(lon, (lat_num, lon_num))
    lat = np.reshape(lat, (lat_num, lon_num))
    topo = np.reshape(topo, (lat_num, lon_num))
    
    return lon, lat, topo  # Return the mesh grid data for lon, lat, topo

# Function to convert degrees to radians
def degree2radians(degree):
  return degree*np.pi/180  # Convert degrees to radians
  
# Function to map lon, lat, alt to 3D coordinates on a sphere, radius is a scaling factor
################################################################################################################
############################################Check different radius for "Lift" above earth"

def mapping_map_to_sphere(lon, lat, alt, radius=1.01):  
    lon = np.array(lon, dtype=np.float64)
    lat = np.array(lat, dtype=np.float64)
    alt = np.array(alt, dtype=np.float64) / 36000  #Change this for lift
    lon = degree2radians(lon)
    lat = degree2radians(lat)
    
    # Adjust scaling factor here, also for lift 
    #####333Do not remove, will not work without
    scaling_factor = 0.05
    xs = (radius + alt * scaling_factor) * np.cos(lon) * np.cos(lat)  
    ys = (radius + alt * scaling_factor) * np.sin(lon) * np.cos(lat)  
    zs = (radius + alt * scaling_factor) * np.sin(lat)  
    
    return xs, ys, zs 

# Import topography data
# Select the area
#  DO NOT CHANGE THE RESOLUTION, CRASHES COMPUTER
resolution = 0.8
lon_area = [-180., 180.]
lat_area = [-90., 90.]
# Get mesh-shape topography data
lon_topo, lat_topo, topo = Etopo(lon_area, lat_area, resolution)
xs, ys, zs = mapping_map_to_sphere(lon_topo, lat_topo, np.zeros_like(lon_topo))  # Map topographic data to 3D coordinates
Ctopo = [[0, 'rgb(0, 0, 70)'],[0.2, 'rgb(0,90,150)'], 
          [0.4, 'rgb(150,180,230)'], [0.5, 'rgb(210,230,250)'],
          [0.50001, 'rgb(0,120,0)'], [0.57, 'rgb(220,180,130)'], 
          [0.65, 'rgb(120,100,0)'], [0.75, 'rgb(80,70,0)'], 
          [0.9, 'rgb(200,200,200)'], [1.0, 'rgb(255,255,255)']]  # Define color scale for elevation layout
cmin = -8000  # Min height for color scale
cmax = 8000  # Max height for color scale

# Create a dict to hold the surface data for the topography
topo_sphere=dict(type='surface',
  x=xs,
  y=ys,
  z=zs,
hoverinfo = 'none',
  colorscale=Ctopo,
  surfacecolor=topo,
  cmin=cmin,
  cmax=cmax,
    showscale=True,  
    colorbar=dict(   # Customizing the color bar
        title='Altitude (m)',  # title
        titlefont=dict(color='white'),  
        tickfont=dict(color='white')   # Ticks need to be white,background is black
    )
)
# Define axis style for 3D plot
noaxis=dict(
    showbackground=False,
    showgrid=False,
    showline=False,
    showticklabels=False,
    ticks='',
    title='',
    zeroline=False,
    showspikes=False,  # Disable spikelines, play around with these more
)

titlecolor = 'white'
bgcolor = 'black'


# Define layout for the plot
layout = go.Layout(
    autosize=True,
    width=1650,
    height=800,
    title='Satellite Locations Around the Globe',
    titlefont=dict(family='Courier New', color=titlecolor),
    showlegend=False,
    scene=dict(
        xaxis=noaxis,
        yaxis=noaxis,
        zaxis=noaxis,
        aspectmode='manual',
        aspectratio=go.layout.scene.Aspectratio(
            x=1.7, y=1.7, z=1.7),
    ),
    paper_bgcolor=bgcolor,
    plot_bgcolor=bgcolor
)


# Read satellite TLE data from file
satellites = []
with open('sqlUpdateValidate/tle/starlinkTLE.txt', 'r') as f:
    lines = f.readlines()
    for i in range(0, len(lines), 3):
        name = lines[i].strip()[1:]
        TLE1 = lines[i+1].strip()[1:]
        TLE2 = lines[i+2].strip()[1:]
        satellites.append(Satellite(name, TLE1, TLE2))  # Initialize Satellite objects and add them to the list

# User Info         
user_latitude, user_longitude = get_user_location()
user_alt = 10000

# Convert to 3D coordinates
user_x, user_y, user_z = mapping_map_to_sphere([user_longitude], [user_latitude], [user_alt])

# Create hover text
user_hovertext = f"User Location<br>Lat: {user_latitude:.2f} Degrees   Lon: {user_longitude:.2f} Degrees"

# Create scatter3d marker for the user's location
user_location_marker = dict(
    type='scatter3d',
    mode='markers',
    x=user_x,
    y=user_y,
    z=user_z,
    marker=dict(
        size=3,
        color='yellow'
    ),
    text=user_hovertext,  # Assign hover text
    hoverinfo='text',
    name="User Location"
)

closest_sat = closest_satellite(satellites, user_latitude, user_longitude)

# Satellite colors and titles
positive_altitude_satellites = [sat for sat in satellites if sat.altitude >= 0]
# Define a color for each satellite based on the conditions
sat_colors = []
legend_text = "Legend:<br>ISS  <span style='color:rgb(100,255,100)'>&#11044;</span><br>Closest Satellite: <span style='color:rgb(252,6,252)'>&#11044;</span><br>Others: <span style='color:rgb(255,0,0)'>&#11044;</span><br>User Location: <span style='color:yellow'>&#11044;</span>"

for sat in positive_altitude_satellites:
    if "ISS (ZARYA)" in sat.name:
        if sat.name == closest_sat.name:
            sat_colors.append('rgb(255,255,255)')  # White for ISS when it's the closest
            print("ISS (Zarya) is the closest satellite.")
            legend_text = "Legend:<br>ISS  <span style='color:rgb(255,255,255)'>&#11044;</span><br>Closest Satellite: <span style='color:rgb(255,255,255)'>&#11044;</span><br>Others: <span style='color:rgb(255,0,0)'>&#11044;</span><br>User Location: <span style='color:yellow'>&#11044;</span>"
        else:
            sat_colors.append('rgb(100,255,100)')  # Green for ISS when it's not the closest
    elif sat == closest_sat:
        sat_colors.append('rgb(252,5,252)')  # Orange for the closest satellite
    else:
        sat_colors.append('rgb(255,0,0)')  # Red for all other satellites

# Get scatter3d data for satellite markers
sat_sphere = satellite_positions_on_sphere(positive_altitude_satellites)

# Plot the Data
fig = go.Figure(data=[topo_sphere, sat_sphere, user_location_marker], layout=layout)

# Add custom layout for the legend
fig.add_annotation(
    x=0,
    y=0,
    xref="paper",
    yref="paper",
    showarrow=False,
    text=legend_text,
    font=dict(color="white")
)


plot(fig, validate=False, filename='SphericalTopography.html', auto_open=True)
#####Importing to bucket######
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIA2GBQBRJE53N4XPM3',
    aws_secret_access_key='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'
)
bucket_name = "visualizationoutput"
html_file_path = "https://visualizationoutput.s3.us-east-2.amazonaws.com/SphericalTopography.html"

#upload the HTML to S3 aws
s3.upload_file('SphericalTopography.html', bucket_name, 'SphericalTopography.html')



#Get total time
end_time = time.time()
execution_time = end_time - start_time  
print("The script took", execution_time, "seconds to run.")
#Validation for Location
#Compare known satellite to external data
target_satellite_name = "KITSAT 3" 
found_satellite = None

for satellite in satellites: #Find satellite
    if target_satellite_name in satellite.name:
        found_satellite = satellite
        break

if found_satellite is not None: #If found, return the location data
    found_satellite.get_position()
    print(f"My Data KAZSAT 3 Longitude: {found_satellite.longitude:.4f} degrees, Latitude: {found_satellite.latitude:.4f} degrees, Altitude: {found_satellite.altitude:.2f} km")

else:
    print(f"Satellite '{target_satellite_name}' not found in the data.")
    

#Your License Key is 7FQ6D4-KLTBTM-WNN6EL-52WD
#Json = java opbejct notation, translate it into python

import requests

def get_satellite_positions(norad_id, observer_lat, observer_lng, observer_alt, seconds, api_key):
    url = f"https://api.n2yo.com/rest/v1/satellite/positions/{norad_id}/{observer_lat}/{observer_lng}/{observer_alt}/{seconds}?apiKey={api_key}"

    response = requests.get(url)  # Send the GET request

    if response.status_code == 200:
        data = response.json()
        positions = data['positions']
        if positions:
            first_pos = positions[0]
            latitude = first_pos['satlatitude']
            longitude = first_pos['satlongitude']
            altitude = first_pos['sataltitude']
            print("NY20 KAZSAT 3 Longitude:", longitude, "degrees, Latitude:", latitude, "degrees, Altitude:", altitude, "km")
    else:
        print('Request failed with status code', response.status_code)


api_key = '7FQ6D4-KLTBTM-WNN6EL-52WD'
norad_id =  25756# International Space Station is 25544
observer_lat = 30.65
observer_lng = -96.37
observer_alt = 0
seconds = 1  

get_satellite_positions(norad_id, observer_lat, observer_lng, observer_alt, seconds, api_key)



user_latitude, user_longitude = get_user_location()
print(f"User Latitude: {user_latitude}, User Longitude: {user_longitude}")




