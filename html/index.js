

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

var eloEngine = (function(){
    var EloK = 16;
    var EloInitR = 1500;
    var LOSS = 0;
    var WON = 1;
    var DRAW = 0.5;

    function elo_exp (ra, rb) {
	return 1.0 / (1 + Math.pow(10, (rb-ra)/400.0));
    }

    function transform (ranking) {
	var game = array();
	$.each(ranking, function(index, info) {
	    var player = info['name'];
	    var wonAgainst = array();
	    $.each(ranking, function(index2, info2) {
		var vs = info2['name'];
		if (player === opponent) {
		    return;
		}
		if (info['rank'] == info2['rank']) {
		    vs[opponent] = DRAW;
		} else if (info['rank'] < info2['rank']) {
		    vs[opponent] = WON;
		} else {
		    vs[opponent] = LOSS;
		}
	    });
	    game[player] = vs;
	});
	console.debug(game);
	return game;
    }

    function compute_ratings(old_ratings, game) {
	var new_ratings = old_ratings;
	$.each(game, function(playerA, results) {
	    var ra = (typeof(old_ratings[playerA]) === 'undefined')
		? EloInitR
		: old_ratings[playerA];
	    var sum = 0;
	    var exp_sum = 0;
	    $.each(results, function (playerB, result) {
		var sum += result;
		var rb = (typeof(old_ratings[playerB]) === 'undefined')
		    ? EloInitR
		    : old_ratings[playerB];
		exp_sum += elo_exp(ra, rb);
	    });
	    var new_ra = ra + EloK * (sum - exp_sum);
	    var new_ratings[playerA] = new_ra;
	});
	return new_ratings;
    }

    var calc = function(old_ratings, ranking) {
	return compute_ratings(old_ratings, transform(ranking));
    }

})();


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
	    var oldPlayers = typeof($scope.state.players) === 'undefined' ? null : $scope.state.players.join();
	    var newState = JSON.parse(e.data);
	    var newPlayers = typeof(newState.players) === 'undefined' ? null : newState.players.join();
	    $scope.state = $.extend($scope.state, newState);
	    if (oldPlayers != newPlayers) {
		$scope.updateChartFull();
	    } else if (typeof(newState.ranking) !== 'undefined') { 
		$scope.updateChartRanking();
	    }
	    $scope.$apply();
	    fitText();
	}
    });

    $scope.latestScores = {};

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
		$.each($scope.state.players, function (i, name) {
		    $scope.chart.data.cols.push({
			id: name, 
			label: name, 
			type: 'number'
		    });
		});
		
		$.each(data, function(date, scores) {
		    $scope.chart.data.rows.push(
			$scope.getChartRowFromRatings(
			    date.split(' ')[0], 
			    scores
			)
		    );
		    $scope.latestScores = scores;
		});
		$scope.chart.data.rows.push(
		    $scope.getChartRowFromRatings(
			'today', 
			eloEngine.calc(
			    $scope.latestScores, 
			    $scope.ranking
			)
		    )
		);
	    });
    };

    $scope.getChartRowFromRatings = function(date, ratings) {
	var currentRow = [{v: date}];
	$.each($scope.state.players, function(i, player) {
	    if (player in scores) {
		currentRow.push({v: Math.round(scores[player])});
	    }
	});
	return {c: currentRow};
    }
    
    $('#refresh').click(function() {
	$scope.updateChart();
    });
});
