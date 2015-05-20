L.mapbox.accessToken = 'pk.eyJ1IjoiamNtZW5jaGF2ZXoiLCJhIjoiM1NqakVJNCJ9.xrJj65p6RUBEYW7iu9NHxg';

var southWest = L.latLng(5.62, 116.87),
    northEast = L.latLng(19.68, 128.44),
    bounds = L.latLngBounds(southWest, northEast);

var map = L.mapbox.map('map', 'jcmenchavez.lmih4k88', {
    maxBounds: bounds,
    minZoom: 6
});

var iconPos = L.mapbox.marker.icon({
    'marker-symbol': 'heart',
});
var iconNeg = L.mapbox.marker.icon({
    'marker-symbol': 'star'
});

var featureGroup = L.featureGroup().addTo(map);

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

var circles = [];
var markers = new L.MarkerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return new L.DivIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-medium',
            iconSize: new L.Point(40, 40)
        });
    }
});

setInterval(function() {
    $.ajax({
        url: '/retrieve',
        method: 'GET',
        success: function(data) {
            data = JSON.parse(data);
            for (var i = 0; i < data.length; i++) {
                var tweet = data[i];

                if (tweet['sentiment'] === 'tourism') { //TEMPORARY FOR TESTING. should be: positive
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

                marker.bindPopup(tweet['text']);
                markers.addLayer(marker);
            }
            map.addLayer(markers);
            updateCircles();
        }
    });
}, 1000);

var allClusters = {};
var circles = [];
var flag = false;

map.on('zoomend', updateCircles);

var findClusters = function(cluster, clusters) {
    if (!cluster) {
        return;
    }
    if (clusters[cluster._zoom]) {
        clusters[cluster._zoom].push(cluster);
    } else {
        clusters[cluster._zoom] = [cluster];
    }
    if (cluster._childClusters.length > 0) {
        for (var i = 0; i < cluster._childClusters.length; i++) {
            findClusters(cluster._childClusters[i], clusters);
        }
    } else {
        return;
    }
};

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

var getCircleRadius = function(markers, maxRadius) {
    var posNegCount = getPosNegCount(markers);
    var posCount = posNegCount['posCount'];
    var negCount = posNegCount['negCount'];

    var total = posCount + negCount;
    var posRadius = (posCount / total) * maxRadius;
    var negRadius = (negCount / total) * maxRadius;
    return {'posRadius': posRadius, 'negRadius': negRadius};
};

function updateCircles() {
    top_cluster = markers._topClusterLevel;
    findClusters(top_cluster, allClusters);

    for (var i = 0; i < circles.length; i++) {
        map.removeLayer(circles[i]);
    }
    circles = [];
    var clusters = allClusters[map.getZoom()] || [];
    for (var i = 0; i < clusters.length; i++) {
        var cluster = clusters[i];
        var childMarkers = cluster.getAllChildMarkers();
        var circleRadius = getCircleRadius(childMarkers, 50);
        
        var posCircle = L.circleMarker(cluster._latlng, circle_options_pos);
        posCircle.setRadius(circleRadius['posRadius']);
        map.addLayer(posCircle);
        circles.push(posCircle);

        var negCircle = L.circleMarker(cluster._latlng, circle_options_neg);
        negCircle.setRadius(circleRadius['negRadius']);
        map.addLayer(negCircle);
        circles.push(negCircle);
    };
}