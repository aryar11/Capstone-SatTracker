document.addEventListener('DOMContentLoaded', function() {
  // Bind geocodeAddress to the relevant button
  document.getElementById('addressButton').addEventListener('click', geocodeAddress);
  
  // Bind getCurrentLocation to the relevant button
  document.getElementById('locationButton').addEventListener('click', getCurrentLocation);

  // Bind computeClosestSatellite to the "Find Closest Satellite" button
  document.getElementById("closestSatelliteButton").addEventListener("click", computeClosestSatellite);
  
  // Bind onSatelliteClick to the container (assuming it's the WebGL rendering area)
  var globeContainer = document.getElementById('container');
  globeContainer.addEventListener('click', onSatelliteClick);
});
