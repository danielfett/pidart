

function fitText() {
    var divisors = [4, 6, 12, 18];
    if ($(window).height() < $(window).width()) {
	for (var d in divisors) {
	    $( '.fit-height-body-' + divisors[d] ).each(function ( i, box ) {
		$(box).css('font-size', $(window).height()/divisors[d]);
	    });
	}
    } else {
	for (var d in divisors) {
	    $( '.fit-width-body-' + divisors[d] ).each(function ( i, box ) {
		$(box).css('font-size', $(window).height()/divisors[d]);
	    });
	}
    }
}

$(window).resize(function() {
    fitText()
});

$(document).ready(function() {
    fitText()
});

angular.module('darts', ['googlechart']).controller('DartCtrl', function ($scope) {
    $scope.state = {};
    
    var history = {};
    history.type="LineChart";
//    history.displayed = false;
    history.cssStyle = "height: 500px; width: 100%;";
    history.data = {};
    history.options = {
        "isStacked": "false",
        "fill": 20,
        "displayExactValues": false,
        "vAxis": {
            "title": "ELO points", "gridlines": {"count": 5}
        },
        "hAxis": {
            "title": "Date"
        }
    };

    $scope.chart = history;

    $scope.chartReady = function () {
        fixGoogleChartsBarsBootstrap();
    }

    function fixGoogleChartsBarsBootstrap() {
        // Google charts uses <img height="12px">, which is incompatible with Twitter
        // * bootstrap in responsive mode, which inserts a css rule for: img { height: auto; }.
        // *
        // * The fix is to use inline style width attributes, ie <img style="height: 12px;">.
        // * BUT we can't change the way Google Charts renders its bars. Nor can we change
        // * the Twitter bootstrap CSS and remain future proof.
        // *
        // * Instead, this function can be called after a Google charts render to "fix" the
        // * issue by setting the style attributes dynamically.

        $(".google-visualization-table-table img[width]").each(function (index, img) {
            $(img).css("width", $(img).attr("width")).css("height", $(img).attr("height"));
        });
    };
    
    $(document).ready(function() {
	var wsuri = window.location.href.replace(/^http(s?:\/\/.*):\d+\/.*$/, 'ws$1:9000/');
	if ("WebSocket" in window) {
	    sock = new ReconnectingWebSocket(wsuri);
	} else {
	    console.error("Browser does not support WebSocket!");
	    window.location = "http://autobahn.ws/unsupportedbrowser";
	    return;
	}
	
	sock.onopen = function() {
	    console.log("Connected to " + wsuri);
	}
	
	sock.onclose = function(e) {
	    console.log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
	    sock = null;
	    if ($scope.state.state != 'gameover') {
		$scope.state.state = 'connlost';
	    }
	    $scope.$apply();
	    fitText();
	}
	
	sock.onmessage = function(e) {
	    console.log("Got message: " + e.data);
	    $scope.state = $.extend($scope.state, JSON.parse(e.data));
	    $scope.updateChart();
	    $scope.$apply();
	    fitText();
	}
    });

    $scope.updateChart = function() {
	$.ajax('http://infsec.uni-trier.de/dartenbank/rpc/elo.php?count=30', {
	    dataType: 'JSON'
	})
	    .done(function(data) {
		console.log("Updating chart.");
		$scope.chart.data.cols = [];
		$scope.chart.data.rows = [];
		$scope.chart.data.cols.push({
		    id: 'date', 
		    label: 'Date', 
		    type: 'string'
		});
		for (var i = 0; i < $scope.state.players.length; i++) {
		    $scope.chart.data.cols.push({
			id: $scope.state.players[i], 
			label: $scope.state.players[i], 
			type: 'number'
		    });
		}
		console.debug($scope.chart.data.cols);
		for (var date in data) {
		    var currentRow = [{v: date.split(' ')[0]}];
		    for (var i = 0; i < $scope.state.players.length; i++) {
			if ($scope.state.players[i] in data[date]) {
			    currentRow.push({v: Math.round(data[date][$scope.state.players[i]])});
			}
		    }
		    $scope.chart.data.rows.push({c: currentRow});
		}
		console.debug($scope.chart.data.rows);
	    });
    };
    
    $('#refresh').click(function() {
	$scope.updateChart();
    });
});
