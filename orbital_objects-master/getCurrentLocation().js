function getCurrentLocation() {
  console.log('Getting current location...');  // Logging the start of getting the location

  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
          var latitude = position.coords.latitude;
          var longitude = position.coords.longitude;

          userLat = latitude;
          userLon = longitude;

          console.log('Latitude:', latitude, 'Longitude:', longitude);  // Logging the current latitude and longitude

          // Updating the User Location table with the current latitude and longitude
          document.getElementById('userLatValue').textContent = latitude;
          document.getElementById('userLonValue').textContent = longitude;

      }, function() {
          console.error('Error getting location.');  // Logging any errors while getting location
          alert('Error getting location.');
      });
  } else {
      console.error('Your browser does not support geolocation.');  // Logging if geolocation is not supported
      alert('Your browser does not support geolocation.');
  }
}
