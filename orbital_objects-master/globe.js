/**
 * dat.globe Javascript WebGL Globe Toolkit
 * http://dataarts.github.com/dat.globe
 *
 * Copyright 2011 Data Arts Team, Google Creative Lab
 *
 * Licensed under the Apache License, Version 2.0 (the 'License');
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 */

var DAT = DAT || {};

var GLOBE_RADIUS = 75;
var satelliteCubes = [];
let lastClickedSatellite = null; 
var closestSatellitesIndices = [];
var userLocationMarker;

let userLat;
let userLon;


DAT.Globe = function(container, colorFn) {

  colorFn = colorFn || function(x) {
    var normalC = x / 100000
    var c = new THREE.Color();
    c.setHSL( ( 0.6 - ( normalC * 0.5 ) ), 1.0, 0.5 );
    console.log(c.getHex());
    return c;
  };

  var Shaders = {
    'earth' : {
      uniforms: {
        'texture': { type: 't', value: null }
      },
      vertexShader: [
        'varying vec3 vNormal;',
        'varying vec2 vUv;',
        'void main() {',
          'gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );',
          'vNormal = normalize( normalMatrix * normal );',
          'vUv = uv;',
        '}'
      ].join('\n'),
      fragmentShader: [
        'uniform sampler2D texture;',
        'varying vec3 vNormal;',
        'varying vec2 vUv;',
        'void main() {',
          'vec3 diffuse = texture2D( texture, vUv ).xyz;',
          'float intensity = 1.05 - dot( vNormal, vec3( 0.0, 0.0, 1.0 ) );',
          'vec3 atmosphere = vec3( 1.0, 1.0, 1.0 ) * pow( intensity, 3.0 );',
          'gl_FragColor = vec4( diffuse + atmosphere, 1.0 );',
        '}'
      ].join('\n')
    },
    'atmosphere' : {
      uniforms: {},
      vertexShader: [
        'varying vec3 vNormal;',
        'void main() {',
          'vNormal = normalize( normalMatrix * normal );',
          'gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );',
        '}'
      ].join('\n'),
      fragmentShader: [
        'varying vec3 vNormal;',
        'void main() {',
          'float intensity = pow( 0.8 - dot( vNormal, vec3( 0, 0, 1.0 ) ), 12.0 );',
          'gl_FragColor = vec4( 1.0, 1.0, 1.0, 1.0 ) * intensity;',
        '}'
      ].join('\n')
    }
  };

  var camera, scene, renderer, w, h;
  var mesh, atmosphere, point;

  var overRenderer;

  var imgDir = '';

  var curZoomSpeed = 0;
  var zoomSpeed = 50;

  var mouse = { x: 0, y: 0 }, mouseOnDown = { x: 0, y: 0 };
  var rotation = { x: 0, y: 0 },
      target = { x: Math.PI*3/2, y: Math.PI / 6.0 },
      targetOnDown = { x: 0, y: 0 };

  var distance = 100000, distanceTarget = 100000;
  var padding = 40;
  var PI_HALF = Math.PI / 2;

  function init() {

    container.style.color = '#fff';
    container.style.font = '13px/20px Arial, sans-serif';

    var shader, uniforms, material;
    w = container.offsetWidth || window.innerWidth;
    h = container.offsetHeight || window.innerHeight;

    camera = new THREE.PerspectiveCamera(30, w / h, 1, 10000);
    camera.position.z = distance;

    scene = new THREE.Scene();

    var geometry = new THREE.SphereGeometry(GLOBE_RADIUS, 40, 30);

    shader = Shaders['earth'];
    uniforms = THREE.UniformsUtils.clone(shader.uniforms);

    uniforms['texture'].value = THREE.ImageUtils.loadTexture(imgDir+'earth.jpg');

    material = new THREE.ShaderMaterial({

          uniforms: uniforms,
          vertexShader: shader.vertexShader,
          fragmentShader: shader.fragmentShader

        });

    mesh = new THREE.Mesh(geometry, material);
    mesh.rotation.y = Math.PI;
    scene.add(mesh);

    shader = Shaders['atmosphere'];
    uniforms = THREE.UniformsUtils.clone(shader.uniforms);

    material = new THREE.ShaderMaterial({

          uniforms: uniforms,
          vertexShader: shader.vertexShader,
          fragmentShader: shader.fragmentShader,
          side: THREE.BackSide,
          blending: THREE.AdditiveBlending,
          transparent: true

        });

    mesh = new THREE.Mesh(geometry, material);
    mesh.scale.set( 1.1, 1.1, 1.1 );
    scene.add(mesh);

    geometry = new THREE.CubeGeometry(0.75, 0.75, 1);
    geometry.applyMatrix(new THREE.Matrix4().makeTranslation(0,0,-0.5));

    point = new THREE.Mesh(geometry);
//    point = new THREE.ParticleSystem(geometry);

    renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setSize(w, h);

    renderer.domElement.style.position = 'absolute';

    container.appendChild(renderer.domElement);

    container.addEventListener('mousedown', onMouseDown, false);

    container.addEventListener('mousewheel', onMouseWheel, false);

    document.addEventListener('keydown', onDocumentKeyDown, false);

    window.addEventListener('resize', onWindowResize, false);

    container.addEventListener('mouseover', function() {
      overRenderer = true;
    }, false);

    container.addEventListener('mouseout', function() {
      overRenderer = false;
    }, false);
  }

  addData = function(data, opts) {
    var lat, lng, size, color, i, step, colorFnWrapper;

    opts.format = opts.format || 'magnitude'; // other option is 'legend'
    console.log(opts.format);
    if (opts.format === 'magnitude') {
      step = 4;
      colorFnWrapper = function(data, i) { return colorFn(data[i+2]); }
    } else if (opts.format === 'legend') {
      step = 5;
      colorFnWrapper = function(data, i) { return colorFn(data[i+3]); }
    } else {
      throw('error: format not supported: '+opts.format);
    }

    var subgeo = new THREE.Geometry();

    var min_size = 10000000000;
    var max_size = 0;

    for (i = 0; i < data.length; i += step) {
      lat = data[i];
      lng = data[i + 1];
      color = colorFnWrapper(data,i+2);
      size = data[i + 2];
      size = size / 30;// size = size *GLOBE_RADIUS;
      addPoint(lat, lng, size, color, subgeo);

      min_size = Math.min(min_size, size);
      max_size = Math.max(max_size, size);
    }

    console.log(min_size);
    console.log(max_size);

    this._baseGeometry = subgeo;
  };

  function createPoints() {
    if (this._baseGeometry !== undefined) {
      this.points = new THREE.Mesh(this._baseGeometry, new THREE.MeshBasicMaterial({
        color: 0xffffff,
        vertexColors: THREE.FaceColors,
        morphTargets: false
      }));

      scene.add(this.points);
    }
  }

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
    cube.scale.set(2, 2, 2);  // Scale the cube
    cube.lookAt(mesh.position); // Make the cube look at the mesh (globe center)
    cube.updateMatrix();
  
    scene.add(cube);  // Add the cube to the scene
    satelliteCubes.push(cube); // Add the cube to the satelliteCubes array
  }
  
  

  function updateSatelliteDetails(satelliteIndex) {
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
    }
  }


// Add an event listener for mouse clicks on the container
container.addEventListener('click', onClick, false);

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

  var intersects = raycaster.intersectObjects(satelliteCubes); // Check for intersection with all cubes in satelliteCubes array
  console.log("Intersections found:", intersects.length);

  if (intersects.length > 0) {
    var clickedCube = intersects[0].object;
    var satelliteIndex = satelliteCubes.indexOf(clickedCube); // Determine the index of the clicked satellite

    // Always revert the color of the last clicked satellite to its original state before processing the new click
    if (lastClickedSatellite) {
      if (closestSatellitesIndices.includes(satelliteCubes.indexOf(lastClickedSatellite))) {
        lastClickedSatellite.material.color.set(0x00ff00); // Reset to green if it's a closest satellite
      } else {
        lastClickedSatellite.material.color.set(0xffffff); // Reset to white otherwise
      }
    }

    // Check if the clicked satellite is one of the ten closest satellites
    if (closestSatellitesIndices.includes(satelliteIndex)) {
      clickedCube.material.color.set(0xff0000); // Set to red
      lastClickedSatellite = clickedCube;
    } else {
      // If the clicked object is not one of the ten closest satellites
      clickedCube.material.color.set(0xff0000); // Set to red
      lastClickedSatellite = clickedCube;
    }

    // Update the UI with the clicked satellite's details
    updateSatelliteDetails(satelliteIndex);
  }
}

function plotUserLocation(lat, lon) {
  // Remove the existing marker if it exists
  if (userLocationMarker) {
    scene.remove(userLocationMarker);
    userLocationMarker = null;
  }

  // Load the star texture with transparency
  var texture = new THREE.TextureLoader().load('star-removebg-preview.png'); // Ensure 'star.png' is in the correct directory
  var material = new THREE.SpriteMaterial({ 
    map: texture, 
    color: 0xffff00, // Yellow color
    depthTest: false, // This will make the sprite always render on top
    transparent: true // Use the alpha channel for transparency
  });

  // Create the sprite with the material
  userLocationMarker = new THREE.Sprite(material);

  // Convert lat/lon to spherical coordinates
  var phi = (90 - lat) * Math.PI / 180;
  var theta = (180 - lon) * Math.PI / 180;
  var r = GLOBE_RADIUS;

  // Position the sprite slightly above the globe surface to prevent z-fighting
  userLocationMarker.position.x = (r + 0.1) * Math.sin(phi) * Math.cos(theta);
  userLocationMarker.position.y = (r + 0.1) * Math.cos(phi);
  userLocationMarker.position.z = (r + 0.1) * Math.sin(phi) * Math.sin(theta);

  // Adjust the size of the sprite as needed
  userLocationMarker.scale.set(7, 7, 7); // Adjust the size as needed

  // Add the sprite to the scene
  scene.add(userLocationMarker);
}




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
              plotUserLocation(userLat, userLon)


              console.log('Latitude:', latitude, 'Longitude:', longitude);
              

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



function getCurrentLocation() {
  console.log('Getting current location...');  // Logging the start of getting the location

  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
          var latitude = position.coords.latitude;
          var longitude = position.coords.longitude;

          userLat = latitude;
          userLon = longitude;
          plotUserLocation(userLat, userLon)

          console.log('Latitude:', latitude, 'Longitude:', longitude); 
           // Logging the current latitude and longitude

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

function findClosestSatellites(userLat, userLon, satellitesData) {
  let closestSatellites = [];
  for (let i = 0; i < satellitesData.length; i += 4) {
      let satelliteLat = parseFloat(satellitesData[i]);
      let satelliteLon = parseFloat(satellitesData[i + 1]);
      
      let distance = haversineDistance(userLat, userLon, satelliteLat, satelliteLon);

      let satellite = {
          name: satellitesData[i + 3] || "Unnamed satellite", 
          latitude: satelliteLat,
          longitude: satelliteLon,
          altitude: parseFloat(satellitesData[i + 2]),
          distance: distance
      };
      
      closestSatellites.push(satellite);
  }
  
  // Sort the satellites by distance and return the top 10
  return closestSatellites.sort((a, b) => a.distance - b.distance).slice(0, 10);
}



function computeClosestSatellite() {
  console.log("computeClosestSatellite called");
  console.log("User Latitude:", userLat);
  console.log("User Longitude:", userLon);
  console.log("Satellites Data:", window.data);

  if (userLat && userLon && window.data) {
    let closestSatellites = findClosestSatellites(userLat, userLon, window.data);
    console.log(closestSatellites);
    if (closestSatellites && closestSatellites.length > 0) {
        console.log("The closest satellite is:", closestSatellites[0].name);

        // Clear the global closestSatellitesIndices array
        closestSatellitesIndices.length = 0;

        for (let i = 0; i < satelliteCubes.length; i++) {
            // Check if the satellite at this index is one of the closest
            if (closestSatellites.some(sat => sat.name === window.data[i * 4 + 3])) {
                satelliteCubes[i].material.color.set(0x00ff00);  // Set color to green
                closestSatellitesIndices.push(i);  // Store the index in the global array
            }
        }
    



          // Existing code for updating the DOM
          let tbody = document.getElementById('topSatellitesList');
          tbody.innerHTML = '';
          closestSatellites.forEach(sat => {
              let row = tbody.insertRow();
              let cell1 = row.insertCell(0);
              let cell2 = row.insertCell(1);
              cell1.textContent = "Name:";
              cell2.textContent = sat.name;
          });
      } else {
          console.log("Couldn't find close satellites.");
      }
  }
}

function toggleCollapse() {
  const tbody = document.getElementById('topSatellitesList');
  if (tbody.style.display === "none" || tbody.style.display === "") {
      tbody.style.display = "table-row-group"; // or "block"
  } else {
      tbody.style.display = "none";
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Get the search input element
  var searchInput = document.getElementById('satelliteSearch');

  // Function to handle the search input event
  function handleSearchInput(event) {
    var searchQuery = event.target.value;  // Get the current value of the search input
    if (searchQuery.length > 0) {
      var results = filterSatellites(searchQuery);  // Filter satellites based on the search query
      displaySearchResults(results);  // Display the search results
    } else {
      displaySearchResults([]);  // If the query is empty, clear the results
    }
  }

  // Attach the event listener to the search input
  searchInput.addEventListener('keyup', handleSearchInput);
});

function filterSatellites(searchQuery) {
  var results = [];
  for (var i = 0; i < window.data.length; i += 4) {
    var satelliteName = window.data[i + 3];
    if (satelliteName.toLowerCase().includes(searchQuery.toLowerCase())) {
      results.push({name: satelliteName, index: i / 4});
      if (results.length >= 5) {
        break;
      }
    }
  }
  return results;
}

function displaySearchResults(results) {
  var searchResults = document.getElementById('searchResults');
  searchResults.innerHTML = '';
  results.forEach(function(result) {
    var li = document.createElement('li');
    li.textContent = result.name;
    li.addEventListener('click', function() {
      // Before updating details, change the previously clicked satellite to its original color
      if (lastClickedSatellite) {
        if (closestSatellitesIndices.includes(satelliteCubes.indexOf(lastClickedSatellite))) {
          lastClickedSatellite.material.color.set(0x00ff00); // Closest satellite color
        } else {
          lastClickedSatellite.material.color.set(0xffffff); // Default satellite color
        }
      }
      // Now highlight the new clicked satellite and update details
      highlightClickedSatellite(result.index); // Highlight the new clicked satellite
      updateSatelliteDetails(result.index); // Update the UI when a search result is clicked
    });
    searchResults.appendChild(li);
  });
  searchResults.style.display = results.length ? 'block' : 'none';
}

// The highlightClickedSatellite function
function highlightClickedSatellite(satelliteIndex) {
  // Get the satellite cube using the index
  var clickedCube = satelliteCubes[satelliteIndex];
  if (clickedCube) {
    clickedCube.material.color.set(0xff0000); // Set to red to highlight the clicked satellite
    lastClickedSatellite = clickedCube; // Keep track of the last clicked satellite
  } else {
    console.error("Could not find a satellite cube at the provided index:", satelliteIndex);
  }
}






document.getElementById("collapseButton").addEventListener("click", toggleCollapse);


document.addEventListener('DOMContentLoaded', function() {
  // Bind geocodeAddress to the relevant button
  document.getElementById('addressButton').addEventListener('click', geocodeAddress);
  
  // Bind getCurrentLocation to the relevant button
  document.getElementById('locationButton').addEventListener('click', getCurrentLocation);

  // Bind computeClosestSatellite to the "Find Closest Satellite" button
  document.getElementById("closestSatelliteButton").addEventListener("click", computeClosestSatellite);
  
  // Bind onSatelliteClick to the container (assuming it's the WebGL rendering area)
  var globeContainer = document.getElementById('container');
  globeContainer.addEventListener('click', onClick);
});


  function onMouseDown(event) {
    event.preventDefault();

    container.addEventListener('mousemove', onMouseMove, false);
    container.addEventListener('mouseup', onMouseUp, false);
    container.addEventListener('mouseout', onMouseOut, false);

    mouseOnDown.x = - event.clientX;
    mouseOnDown.y = event.clientY;

    targetOnDown.x = target.x;
    targetOnDown.y = target.y;

    container.style.cursor = 'move';
  }

  function onMouseMove(event) {
    mouse.x = - event.clientX;
    mouse.y = event.clientY;

    var zoomDamp = distance/1000;

    target.x = targetOnDown.x + (mouse.x - mouseOnDown.x) * 0.005 * zoomDamp;
    target.y = targetOnDown.y + (mouse.y - mouseOnDown.y) * 0.005 * zoomDamp;

    target.y = target.y > PI_HALF ? PI_HALF : target.y;
    target.y = target.y < - PI_HALF ? - PI_HALF : target.y;
  }

  function onMouseUp(event) {
    container.removeEventListener('mousemove', onMouseMove, false);
    container.removeEventListener('mouseup', onMouseUp, false);
    container.removeEventListener('mouseout', onMouseOut, false);
    container.style.cursor = 'auto';
  }

  function onMouseOut(event) {
    container.removeEventListener('mousemove', onMouseMove, false);
    container.removeEventListener('mouseup', onMouseUp, false);
    container.removeEventListener('mouseout', onMouseOut, false);
  }

  function onMouseWheel(event) {
    event.preventDefault();
    if (overRenderer) {
      zoom(event.wheelDeltaY * 0.3);
    }
    return false;
  }

  function onDocumentKeyDown(event) {
    switch (event.keyCode) {
      case 38:
        zoom(100);
        event.preventDefault();
        break;
      case 40:
        zoom(-100);
        event.preventDefault();
        break;
    }
  }

  function onWindowResize( event ) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
  }

  function zoom(delta) {
    distanceTarget -= delta;
    distanceTarget = distanceTarget > 2000 ? 2000 : distanceTarget;
    distanceTarget = distanceTarget < 350 ? 350 : distanceTarget;
  }

  function animate() {
    requestAnimationFrame(animate);
    render();
  }

  function render() {
    zoom(curZoomSpeed);

    rotation.x += (target.x - rotation.x) * 0.1;
    rotation.y += (target.y - rotation.y) * 0.1;
    distance += (distanceTarget - distance) * 0.3;

    camera.position.x = distance * Math.sin(rotation.x) * Math.cos(rotation.y);
    camera.position.y = distance * Math.sin(rotation.y);
    camera.position.z = distance * Math.cos(rotation.x) * Math.cos(rotation.y);

    camera.lookAt(mesh.position);

    renderer.render(scene, camera);
  }

  init();
  this.animate = animate;


  this.__defineGetter__('time', function() {
    return this._time || 0;
  });

  this.__defineSetter__('time', function(t) {
    var validMorphs = [];
    var morphDict = this.points.morphTargetDictionary;
    for(var k in morphDict) {
      if(k.indexOf('morphPadding') < 0) {
        validMorphs.push(morphDict[k]);
      }
    }
    validMorphs.sort();
    var l = validMorphs.length-1;
    var scaledt = t*l+1;
    var index = Math.floor(scaledt);
    for (i=0;i<validMorphs.length;i++) {
      this.points.morphTargetInfluences[validMorphs[i]] = 0;
    }
    var lastIndex = index - 1;
    var leftover = scaledt - index;
    if (lastIndex >= 0) {
      this.points.morphTargetInfluences[lastIndex] = 1 - leftover;
    }
    this.points.morphTargetInfluences[index] = leftover;
    this._time = t;
  });

  this.addData = addData;
  this.createPoints = createPoints;
  this.renderer = renderer;
  this.scene = scene;

  return this;

};
