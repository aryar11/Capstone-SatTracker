function geocodeAddress() {
  var address = document.getElementById('address').value;
  console.log('Geocoding address:', address);  // Logging the address being geocoded

  var url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;

  fetch(url)
      .then(response => response.json())
      .then(data => {
          if (data && data.length) {
              var latitude = parseFloat(data[0].lat);
              var longitude = parseFloat(data[0].lon);

              userLat = latitude;
              userLon = longitude;

              console.log('Latitude:', latitude, 'Longitude:', longitude);  // Logging the resulting latitude and longitude

              // Updating the User Location table with the fetched latitude and longitude
              document.getElementById('userLatValue').textContent = latitude;
              document.getElementById('userLonValue').textContent = longitude;

          } else {
              console.log('Address not found.');  // Logging if address isn't found
              alert('Address not found.');
          }
      })
      .catch(error => {
          console.error('Error geocoding address:', error);  // Logging any errors during geocoding
          alert('Error geocoding address.');
      });
}
