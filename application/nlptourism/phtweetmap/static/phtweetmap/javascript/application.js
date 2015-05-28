/*
  code for the philippine map with tweets and clusters
*/

L.mapbox.accessToken = 'pk.eyJ1IjoiamNtZW5jaGF2ZXoiLCJhIjoiM1NqakVJNCJ9.xrJj65p6RUBEYW7iu9NHxg';

// get the bounds of the map, sets view to focus on the Philippines
var southWest = L.latLng(5.62, 116.87),
    northEast = L.latLng(19.68, 128.44),
    bounds = L.latLngBounds(southWest, northEast);

var map = L.mapbox.map('map', 'jcmenchavez.lmih4k88', {
    maxBounds: bounds,
    minZoom: 6
});

// set symbols for icons for positive and negative tweets
var iconPos = L.mapbox.marker.icon({
    'marker-symbol': 'heart', // modify symbol here
});
var iconNeg = L.mapbox.marker.icon({
    'marker-symbol': 'star' // modify symbol here
});

// create feature group
var featureGroup = L.featureGroup().addTo(map);

// create circles to surround clusters
var circle_options_pos = {
  stroke: false,
  fillColor: 'green',
  fillOpacity: 0.3
};

var circle_options_neg = {
  stroke: false,
  fillColor: 'red',
  fillOpacity: 0.3
};

// create marker cluster group
var circles = [];
var markers = new L.MarkerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        // creates the cluster
        return new L.DivIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-medium',
            iconSize: new L.Point(40, 40)
        });
    }
});

// updates every second to retrieve and add new tweets on the map
setInterval(function() {
    $.ajax({
        url: '/retrieve',
        method: 'GET',
        success: function(data) {
            data = JSON.parse(data);
            // loop through tweets
            for (var i = 0; i < data.length; i++) {
                var tweet = data[i];

                // retrieve tweet data, set icon accordingly
                if (tweet['sentiment'] === 'positive') {
                    var marker = L.marker(new L.LatLng(tweet['lat'], tweet['lng']), {
                        icon: iconPos,
                        title: tweet['text'],
                        sentiment: 'positive'
                    });
                } else {
                    var marker = L.marker(new L.LatLng(tweet['lat'], tweet['lng']), {
                        icon: iconNeg,
                        title: tweet['text'],
                        sentiment: 'negative'
                    });
                }

                // add actual tweet content (text) to the marker
                marker.bindPopup(tweet['text']);
                markers.addLayer(marker);
            }
            // add markers to the map
            map.addLayer(markers);
            // update the sentiment circles around the clusters upon zoom
            updateCircles();
        }
    });
}, 1000);

var allClusters = {};
var circles = [];
var flag = false;

// update the sentiment circles around the clusters upon zoom
map.on('zoomend', updateCircles);

// finds the child clusters of the given cluster
var findClusters = function(cluster, clusters) {
    if (!cluster) {
        return;
    }
    if (clusters[cluster._zoom]) {
        clusters[cluster._zoom].push(cluster);
    } else {
        clusters[cluster._zoom] = [cluster];
    }

    // call findClusters for each of the child clusters
    if (cluster._childClusters.length > 0) {
        for (var i = 0; i < cluster._childClusters.length; i++) {
            findClusters(cluster._childClusters[i], clusters);
        }
    } else {
        return;
    }
};

// given a cluster (markers), get the number of positive and negative points in the cluster
var getPosNegCount = function(markers) {
    var posCount = 0;
    var negCount = 0;
    for (var i = 0; i < markers.length; i++) {
        if (markers[i]['options']['sentiment'] == 'positive') {
            posCount++;
        } else {
            negCount++;
        }
    }
    return {'posCount': posCount, 'negCount': negCount};
};

// computes for the radius of the positive and negative circles
var getCircleRadius = function(markers, maxRadius) {
    // retrieve number of positive and negative points in the cluster
    var posNegCount = getPosNegCount(markers);
    var posCount = posNegCount['posCount'];
    var negCount = posNegCount['negCount'];

    var total = posCount + negCount;

    // set radius to be a percentage of the maximum radius depending on the counts
    var posRadius = (posCount / total) * maxRadius;
    var negRadius = (negCount / total) * maxRadius;
    return {'posRadius': posRadius, 'negRadius': negRadius};
};

// update the positive and negative sentiment circles
function updateCircles() {

    // retrieve the top cluster at the first zoom level (showing the entire map)
    top_cluster = markers._topClusterLevel;
    findClusters(top_cluster, allClusters);

    // remove circles previoiusly drawn on the map
    for (var i = 0; i < circles.length; i++) {
        map.removeLayer(circles[i]);
    }
    circles = [];

    // retrieve all clusters at the current zoom level
    var clusters = allClusters[map.getZoom()] || [];
    // loop through clusters
    for (var i = 0; i < clusters.length; i++) {
        var cluster = clusters[i];

        // retrieve child markers within the cluster
        var childMarkers = cluster.getAllChildMarkers();
        // obtain the radius of the sentiment circles
        var circleRadius = getCircleRadius(childMarkers, 50);
        
        // create positive (green) circle
        var posCircle = L.circleMarker(cluster._latlng, circle_options_pos);
        posCircle.setRadius(circleRadius['posRadius']);
        map.addLayer(posCircle);
        circles.push(posCircle);

        // create negative (red) circle
        var negCircle = L.circleMarker(cluster._latlng, circle_options_neg);
        negCircle.setRadius(circleRadius['negRadius']);
        map.addLayer(negCircle);
        circles.push(negCircle);
    };
}