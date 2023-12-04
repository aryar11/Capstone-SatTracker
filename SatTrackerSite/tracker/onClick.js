function onClick(event) {
  event.preventDefault();

  var raycaster = new THREE.Raycaster();
  var mouseVector = new THREE.Vector2(
      (event.clientX / window.innerWidth) * 2 - 1,
      -(event.clientY / window.innerHeight) * 2 + 1
  );

  raycaster.ray.origin.copy(camera.position);
  raycaster.ray.direction.set(mouseVector.x, mouseVector.y, 0.5)
      .unproject(camera)
      .sub(camera.position)
      .normalize();

  var intersects = raycaster.intersectObjects(satelliteCubes);  // Check for intersection with all cubes in satelliteCubes array
  console.log("Intersections found:", intersects.length);

  if (intersects.length > 0) {
    var clickedCube = intersects[0].object;

    // If there was a previously clicked satellite, revert its color
    if (lastClickedSatellite) {
      lastClickedSatellite.material.color.set(0xffffff); //the original color is white
    }

    // Change color of the clicked cube to red
    clickedCube.material.color.set(0xff0000);

    // Update the lastClickedSatellite reference
    lastClickedSatellite = clickedCube;

    var satelliteIndex = satelliteCubes.indexOf(clickedCube);  // Get the index of the clicked cube within the satelliteCubes array

    if (satelliteIndex * 4 + 3 < window.data.length) {
      var rawLat = parseFloat(window.data[satelliteIndex * 4]);
      var rawLng = parseFloat(window.data[satelliteIndex * 4 + 1]);
      var rawAlt = parseFloat(window.data[satelliteIndex * 4 + 2]);
      var name = window.data[satelliteIndex * 4 + 3] || "-";
      
      document.getElementById('latValue').textContent = rawLat.toFixed(3) + '°';
      document.getElementById('lngValue').textContent = rawLng.toFixed(3) + '°';
      document.getElementById('altValue').textContent = rawAlt.toFixed(3) + ' KM';
      document.getElementById('nameValue').textContent = name;
    } else {
      console.error("Invalid satellite index:", satelliteIndex);
      console.log(clickedCube); // Logs the entire clicked cube object
    }
  }
}
