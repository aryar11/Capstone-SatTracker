unction onClick(event) {
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

  var intersects = raycaster.intersectObject(globe.points);
 console.log("Intersections found:", intersects.length);


 if (intersects.length > 0) {
  var faceIndex = intersects[0].faceIndex; // This gets the face index
  console.log('Face Index:', faceIndex);

  // Calculate the satellite index based on faceIndex
  var satelliteIndex = Math.floor(faceIndex / 12);

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
    console.error("Invalid satellite index derived from faceIndex:", satelliteIndex);
    console.log(intersects[0].object); // Logs the entire object that was intersected

  }
}
}
