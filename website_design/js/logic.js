// function createmap(jobs) {

    // Create the tile layers that will be used for the map backgrounds
    //light layer



    var queryURL = "https://raw.githubusercontent.com/krashilili/Final-Project/master/cities_df3.csv";

    d3.csv(queryURL, function(data) {
        createFeatures(data.features);
    });


    function markerSize(job_count) {
        return job_count * 500;
    }

    function markerColor(job_count) {
        if (job_count > 200) {
            return "darkred";
        }
        if (job_count > 100) {
            return "red";
        }
        if (job_count > 50) {
            return "darkorange";
        }
        if (job_count > 10) {
            return "orange";
        }
        if (job_count > 5) {
            return "yellow";
        }
    }

    function createFeatures(jobdata) {
        function onEachFeature(feature, layer) {
            layer.bindPopup("<h3>"+feature.properties.place+"</h3><hr><p>"+
                new Date(feature.properties.time)+"</p><hr><p>"+
                "Magnitude:"+feature.properties.mag+"</p>");
        }
    
        function pointToLayer(feature, latlng) {
            return new L.circle(latlng,
            {radius: markerSize(feature.properties.mag),
            fillColor: markerColor(feature.properties.mag),
            fillOpacity: .8,
            color: "grey",
            weight: .5});
        }
    
       
    
        var earthquakes = L.geoJson(earthquakedata, {
            onEachFeature: onEachFeature,
            pointToLayer: pointToLayer
            
        });
    
        createmap(earthquakes);
    }


    var lightmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 18,
        id: "mapbox.light",
        accessToken: API_KEY
    });
        
    //street layer
    var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 18,
        id: "mapbox.streets",
        accessToken: API_KEY
    });

    //satellite layer
    var satellitemap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 18,
        id: "mapbox.satellite",
        accessToken: API_KEY
    });

    //dark layer
    var darkmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 18,
        id: "mapbox.dark",
        accessToken: API_KEY
    });

    var basemap = {
        "Street Map": streetmap,
        "Dark Map": darkmap,
        "Satellite": satellitemap,
        "Light Map": lightmap
    };

    //Create the map with the layers
    var myMap = L.map("map", {
        center: [39.82, -98.59],
        zoom: 4,
        layers: [darkmap]
    });

    L.control.layers(basemap).addTo(myMap);

        
//     };

// createmap;

// function openNav() {
//     document.getElementById("mySidenav").style.width = "250px";
//     document.getElementById("main").style.marginLeft = "250px";
//     document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
// }

// function closeNav() {
//     document.getElementById("mySidenav").style.width = "0";
//     document.getElementById("main").style.marginLeft= "0";
//     document.body.style.backgroundColor = "white";
