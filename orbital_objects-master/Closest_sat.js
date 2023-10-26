function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the Earth in kilometers
  let dLat = toRad(lat2 - lat1);
  let dLon = toRad(lon2 - lon1);
  let a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
          Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
          Math.sin(dLon / 2) * Math.sin(dLon / 2);
  let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // Distance in kilometers
}

function toRad(value) {
  return value * Math.PI / 180;
}

function findClosestSatellite(userLat, userLon, satellitesData) {
  let closestSatellite = null;
  let minDistance = Number.MAX_VALUE;

  for (let i = 0; i < satellitesData.length; i += 4) {
      let satelliteLat = parseFloat(satellitesData[i]);
      let satelliteLon = parseFloat(satellitesData[i + 1]);
      
      let distance = haversineDistance(userLat, userLon, satelliteLat, satelliteLon);

      if (distance < minDistance) {
          minDistance = distance;
          closestSatellite = {
              name: satellitesData[i + 3] || "Unnamed satellite", 
              latitude: satelliteLat,
              longitude: satelliteLon,
              altitude: parseFloat(satellitesData[i + 2]),
              distance: minDistance
          };
      }
  }
  return closestSatellite;
}


function computeClosestSatellite() {
  console.log("computeClosestSatellite called");
  console.log("User Latitude:", userLat);
  console.log("User Longitude:", userLon);
  console.log("Satellites Data:", window.data);

  if (userLat && userLon && window.data) {
      let closest = findClosestSatellite(userLat, userLon, window.data);
      if (closest) {
          console.log("The closest satellite is:", closest.name);
          // Update the satellite data table with the closest satellite's data
          document.getElementById('satLatValue').textContent = closest.latitude.toFixed(3) + '°';
          document.getElementById('satLonValue').textContent = closest.longitude.toFixed(3) + '°';
          document.getElementById('satAltValue').textContent = closest.altitude.toFixed(3) + ' KM';
          document.getElementById('satNameValue').textContent = closest.name;
      } else {
          console.log("Couldn't find a close satellite.");
      }
  }
}
