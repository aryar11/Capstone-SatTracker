function addPoint(lat, lng, size, color, subgeo) {
  var phi = (90 - lat) * Math.PI / 180;
  var theta = (180 - lng) * Math.PI / 180;
  var r = ((1 + (size / 100.0)) * GLOBE_RADIUS);

  // Create a cube for this point
  var geometry = new THREE.BoxGeometry(1, 1, 1);
  var material = new THREE.MeshBasicMaterial({ color: color }); // Use the given color
  var cube = new THREE.Mesh(geometry, material);

  cube.position.x = r * Math.sin(phi) * Math.cos(theta);
  cube.position.y = r * Math.cos(phi);
  cube.position.z = r * Math.sin(phi) * Math.sin(theta);
  cube.scale.set(4, 4, 4);  // Scale the cube
  cube.lookAt(mesh.position); // Make the cube look at the mesh (globe center)
  cube.updateMatrix();

  scene.add(cube);  // Add the cube to the scene
  satelliteCubes.push(cube); // Add the cube to the satelliteCubes array

  
  // THREE.GeometryUtils.merge(subgeo, point);
}






//////////////////////////////////////Look Here////////////////////////////////////////////
//in order for this function to work, you need to add this line to the top of globe.js: var satelliteCubes = [];
//and also this line: let lastClickedSatellite = null; 
