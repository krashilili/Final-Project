// Store our API endpoint inside queryUrl
// Getting data of all M2.5+ earthquakes from the past week
var queryUrl = "https://raw.githubusercontent.com/krashilili/Final-Project/master/flask_app/data/city_jobs_2.geojson";

// Perform a GET request to the query URL
d3.json(queryUrl, function(data) {
  // Once we get a response, send the data.features object to the createFeatures function
  createFeatures(data.features);
});

function createFeatures(earthquakeData) {

  // Print earthquake data
  console.log(earthquakeData);

  // Create LatLng from the array
  // JSON.parse(earthquakeData)

  // Define a function we want to run once for each feature in the features array
  // Give each feature a popup describing the place and time of the earthquake
  // function onEachFeature(feature, layer) {
  //   layer.bindPopup("<h3>" + feature.properties.place +
  //     "</h3><hr><p>" + new Date(feature.properties.time) + "</p>");
  // }

  // // Create function to dynamically style circle colors
  // function getColor(d) {
  //   return d < 3  ? '#98ff6e' :
  //         d < 4  ? '#FFFF00' :
  //         d < 5  ? '#FFA500' :
  //         d < 6  ? '#ff0000' :
  //                   '#f08b5c';
  

  // Create a GeoJSON layer containing the features array on the earthquakeData object
  // Run the onEachFeature function once for each piece of data in the array
  var earthquakes = L.geoJSON(earthquakeData, {
    //onEachFeature: onEachFeature,
    pointToLayer: function (feature, coordinates) {


      
      // Create circle markers
//   var geojsonMarkerOptions = {
//     radius: 5*feature.properties.mag,
//     fillColor: getColor(feature.properties.mag),
//     color: "#000",
//     weight: 1,
//     opacity: 1,
//     fillOpacity: 0.8
// };

      return L.circleMarker(coordinates);
    }
  });

  // Sending our earthquakes layer to the createMap function
  createMap(earthquakes);

};

function createMap(earthquakes) {

  // Define streetmap layer
  var streetmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: API_KEY
  });

  // Define a baseMaps object to hold our base layers
  var baseMaps = {
    "Street Map": streetmap,
  };

  // Create overlay object to hold our overlay layer
  var overlayMaps = {
    Earthquakes: earthquakes
  };

  // Create our map, giving it the streetmap and earthquakes layers to display on load
  var myMap = L.map("map", {
    center: [
      37.09, -95.71
    ],
    zoom: 5,
    layers: [streetmap, earthquakes]
  });

  // Create a layer control
  // Pass in our baseMaps and overlayMaps
  // Add the layer control to the map
  L.control.layers(baseMaps, overlayMaps, {
    collapsed: false
  }).addTo(myMap);

  function getColor(d) {
    return d < 2 ? '#42f4d9' : 
          d < 3  ? '#98ff6e' :
          d < 4  ? '#FFFF00' :
          d < 5  ? '#ef771c' :
          d < 6  ? '#ab1313' :
                    '#7e0b0b';
  }

  // Create a legend to display information about our map
  var legend = L.control({position: 'bottomright'});

  legend.onAdd = function (map) {
  
      var div = L.DomUtil.create('div', 'info legend'),
      grades = [0, 1, 2, 3, 4, 5];

      div.innerHTML+='<h4>Magnitude</h4><hr>'
  
      // loop through our density intervals and generate a label with a colored square for each interval
      for (var i = 0; i < grades.length; i++) {
          div.innerHTML +=
              '<i style="background:' + getColor(grades[i] + 1) + '">&nbsp&nbsp&nbsp&nbsp</i> ' +
              grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
  }
  
  return div;
  };
  
  legend.addTo(myMap);
}
