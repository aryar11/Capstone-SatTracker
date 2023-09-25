#imports

from flask import Flask, render_template, redirect, url_for, send_from_directory
import os

import numpy as np
import os 
# For reading NetCDF data
from netCDF4 import Dataset #Network Common Data Form, needed to read the mesh file

# For creating 3D plots
import plotly.graph_objs as go
from plotly.offline import plot

# For parsing TLE set and calc. satellite position
from skyfield.api import load, EarthSatellite


#For geolocation
import googlemaps
gmaps = googlemaps.Client(key='AIzaSyDylyC2otrMcdv4i7BGajUbetqbS0-k1ho')



# Initialize the Flask app
app = Flask(__name__)

# Initialize any necessary classes or helper functions
# E.g., your Satellite class, mapping_map_to_sphere, get_user_location, closest_satellite, etc.

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
        
        

    def get_position(self):
        self.update_position()  # Update the satellite's position
        return self.longitude, self.latitude, self.altitude # Return the updated position

def satellite_positions_on_sphere(satellites, sat_colors):
    
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


def degree2radians(degree):
  return degree*np.pi/180  # Convert degrees to radians

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





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    return generate_plot()


@app.route('/generate_plot')
def generate_plot():

    resolution = 0.8
    lon_area = [-180., 180.]
    lat_area = [-90., 90.]
    lon_topo, lat_topo, topo = Etopo(lon_area, lat_area, resolution)
    xs, ys, zs = mapping_map_to_sphere(lon_topo, lat_topo, np.zeros_like(lon_topo))
    
    Ctopo = [[0, 'rgb(0, 0, 70)'],[0.2, 'rgb(0,90,150)'], 
              [0.4, 'rgb(150,180,230)'], [0.5, 'rgb(210,230,250)'],
              [0.50001, 'rgb(0,120,0)'], [0.57, 'rgb(220,180,130)'], 
              [0.65, 'rgb(120,100,0)'], [0.75, 'rgb(80,70,0)'], 
              [0.9, 'rgb(200,200,200)'], [1.0, 'rgb(255,255,255)']]
    
    cmin = -8000  
    cmax = 8000  
    
    topo_sphere = dict(
        type='surface',
        x=xs,
        y=ys,
        z=zs,
        hoverinfo = 'none',
        colorscale=Ctopo,
        surfacecolor=topo,
        cmin=cmin,
        cmax=cmax,
        showscale=True,  
        colorbar=dict(
            title='Altitude (m)',
            titlefont=dict(color='white'),
            tickfont=dict(color='white')
        )
    )
    
    noaxis = dict(
        showbackground=False,
        showgrid=False,
        showline=False,
        showticklabels=False,
        ticks='',
        title='',
        zeroline=False,
        showspikes=False,
    )
    
    titlecolor = 'white'
    bgcolor = 'black'
    
    layout = go.Layout(
        autosize=True,
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
    with open('Sat_Data.txt', 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 3):
            name = lines[i].strip()[1:]
            TLE1 = lines[i+1].strip()[1:]
            TLE2 = lines[i+2].strip()[1:]
            satellites.append(Satellite(name, TLE1, TLE2))

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
    sat_sphere = satellite_positions_on_sphere(positive_altitude_satellites, sat_colors)

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

    # Determine the directory of the currently running script (app.py)
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Create a path to the 'templates' directory (for easier Flask rendering)
    output_file_path = os.path.join(current_directory, 'generated', 'SatGlobe.html')


    plot(fig, validate=False, filename=output_file_path, auto_open=False)

    return redirect(url_for('view_plot'))


@app.route('/view_plot')
def view_plot():
    return send_from_directory('generated', 'SatGlobe.html')


if __name__ == "__main__":
    app.run(debug=True)
