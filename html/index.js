  
function dartenbankBackend(url, $http) {
    if (url == undefined) {
	url = 'http://infsec.uni-trier.de/dartenbank';
    }

    var usualSuspects = Array();

    /* We do this synchronously, as it makes things easier. */
    var req = new XMLHttpRequest();
    req.open('GET', url + '/rpc/get-usual-suspects.php', false); 
    req.send(null);
    if(req.status == 200)
	usualSuspects = JSON.parse(req.responseText);

    return {
	hasChart: true,
	links: [
	    {'url': url, 'name': 'Dartenbank'},
	    {'url': url + '/input/', 'name': 'Input Results'}
	],

	chartdata: undefined,
	currentRanking: undefined,
	currentPlayersInChart: undefined,

	getChartRowFromRatings: function(tdate, ratings) {
	    var currentRow = [{v: tdate}];
	    for (var i = 0; i < this.currentPlayersInChart.length; i++) {
		var player = this.currentPlayersInChart[i];
		if (player in ratings) {
		    currentRow.push({v: Math.round(ratings[player])});
		} else {
		    currentRow.push({});
		}
	    };
	    return {c: currentRow};
	},

	updateChartRanking: function(ranking, cb) {
	    this.currentRanking = ranking;
	    this.calculateLatestChartRanking(cb);
	},

	calculateLatestChartRanking: function(cb) {
	    if (this.currentRanking == undefined || this.currentPlayers == undefined) {
		return;
	    }
	    this.chartdata.rows.pop();
	    var todaysRanking = eloEngine.calc(this.latestScores, this.currentRanking);
	    this.chartdata.rows.push(
		this.getChartRowFromRatings(
		    'today',
		    todaysRanking
		)
	    );
	    if(cb != undefined) {
		cb(this.chartdata);
	    }
	},

	
	getChartData: function(currentPlayers, cbSuccess, cbFail) {
	    var _ = this;
	    _.currentPlayers = currentPlayers;
	    
	    var playersInChart = $.merge([], usualSuspects);
	    $.each(currentPlayers, function (i, name) {
		if (playersInChart.indexOf(name) === -1) {
		    playersInChart.push(name);
		}
	    });
	    _.currentPlayersInChart = playersInChart;

	    $http.get(url + '/rpc/elo.php?count=30')
		.success(function(data) {
		    var chartdata = {
			'rows': Array(),
			'cols': [{
			    id: 'date',
			    label: 'Date',
			    type: 'string'
			}]
		    };

		    $.each(playersInChart, function (i, name) {
			chartdata.cols.push({
			    id: name,
			    label: name,
			    type: 'number'
			});
		    });
		    
		    $.each(data, function(date, scores) {
			chartdata.rows.push(
			    _.getChartRowFromRatings(
				date.split(' ')[0],
				scores
			    )
			);
			_.latestScores = scores;
		    });
		    chartdata.rows.push({}); // add empty element that will later be replaced by today's scores
		    _.chartdata = chartdata;
		    _.calculateLatestChartRanking();
		    cbSuccess(_.chartdata);
		})
		.error(function(xhr, status, error) {
		    cbFail(error);
		});
	},
	
	getAvailablePlayers: function(lastPlayers, cbSuccess, cbFail) {
	    $http.get(url + '/rpc/get-players.php')
		.success(function(data) {
		    $http.get(url + '/rpc/elo.php?count=1')
			.success(function(rankdata) {
			    
			    var availablePlayers = [];
			    var ranking = rankdata[Object.keys(rankdata)[0]];
			    $.each(data, function(name, games) {
				var rank = 1500;
				if (typeof(ranking[name]) != 'undefined') {
				    rank = ranking[name];
				}
				var selected = (
				    lastPlayers.indexOf(name) > -1) 
				    || (usualSuspects.indexOf(name) > -1);
				if (lastPlayers.indexOf(name) > -1) {
				    lastPlayers.splice(lastPlayers.indexOf(name), 1);
				}
				availablePlayers.push({
				    name: name, 
				    games: games, 
				    rank:rank, 
				    selected:selected
				});
			    });
			    $.each(lastPlayers, function(i, name) {
				availablePlayers.push({
				    name: name, 
				    games: 0, 
				    rank:1500, 
				    selected:true
				});
			    });
			    availablePlayers.sort(
				function(a,b){
				    return (b.name < a.name) ? 1 : (a.name == b.name)? 0 : -1
				});
			    
			    cbSuccess(availablePlayers);
			})
			.error(function(xhr, status, error) {
			    cbFail(error);
			});
		})
		.error(function(xhr, status, error) {
		    cbFail(error);
		});
	},
	submitResult: function(ranking) {
	    urlparam = encodeURIComponent(JSON.stringify(ranking));
	    window.open(url + '/input/remote-input.php?standings=' + urlparam);
	},
	sortPlayers: function(players) {
	    players.sort(function(a,b){return a.rank-b.rank});
	    return players;
	}	    
    }
}


function dummyBackend() {
    return {
	hasChart: false,
	links: [
	    {'url': 'http://example.com', 'name': 'Dummy Backend'}
	],
	
	getChartData: function(currentPlayers, cbSuccess, cbFail) {
	    cbSuccess(Array(), Array());
	},
	
	getAvailablePlayers: function(lastPlayers, cbSuccess, cbFail) {
	    cbSuccess(Array());
	},
	
	submitResult: null
    }
};

function offlineDartenbankBackend() {
    return {
	hasChart: false,
	links: [],
	
	getChartData: function(currentPlayers, cbSuccess, cbFail) {
	    cbSuccess(Array(), Array());
	},
	
	getAvailablePlayers: function(lastPlayers, cbSuccess, cbFail) {
	    var ap = [
		{ name: 'DF', rank: '1500', selected: true},
		{ name: 'RK', rank: '1600', selected: true},
		{ name: 'MID', rank: '1550', selected: false}	    
	    ];
	    
	    ap.sort(function(a,b){return a.rank-b.rank});
	    
	    cbSuccess(ap);
	},
	
	submitResult: null
    }
};


function fitText() {
    var divisors = [4, 6, 12, 18];
    //if ($(window).height() < $(window).width()) {
	for (var d in divisors) {
	    $( '.fit-height-body-' + divisors[d] ).each(function ( i, box ) {
		$(box).css('font-size', $(window).height()/divisors[d]);
	    });
	}
    //} else {
	for (var d in divisors) {
	    $( '.fit-width-body-' + divisors[d] ).each(function ( i, box ) {
		$(box).css('font-size', $(window).height()/divisors[d]);
	    });
	}
    //}
}

var eloEngine = new function(){
    var EloK = 16;
    var EloInitR = 1500;
    var LOSS = 0;
    var WON = 1;
    var DRAW = 0.5;

    function elo_exp (ra, rb) {
	return 1.0 / (1 + Math.pow(10, (rb-ra)/400.0));
    }

    function transform (ranking) {
	var game = {};
	$.each(ranking, function(index, info) {
	    var player = info['name'];
	    var against = {};
	    $.each(ranking, function(index2, info2) {
		var opponent = info2['name'];
		if (player === opponent) {
		    return;
		}
		if (info['rank'] == info2['rank']) {
		    against[opponent] = DRAW;
		} else if (info['rank'] < info2['rank']) {
		    against[opponent] = WON;
		} else {
		    against[opponent] = LOSS;
		}
	    });
	    game[player] = against;
	});
	return game;
    }

    function compute_ratings(old_ratings, game) {
	var new_ratings = $.extend(true, {}, old_ratings);
	$.each(game, function(playerA, results) {
	    var ra = (typeof(old_ratings[playerA]) === 'undefined')
		? EloInitR
		: old_ratings[playerA];
	    var sum = 0;
	    var exp_sum = 0;
	    $.each(results, function (playerB, result) {
		sum += result;
		var rb = (typeof(old_ratings[playerB]) === 'undefined') ? EloInitR : old_ratings[playerB];
		exp_sum += elo_exp(ra, rb);
	    });
	    var new_ra = ra + EloK * (sum - exp_sum);
	    new_ratings[playerA] = new_ra;
	});
	return new_ratings;
    }

    this.calc = function(old_ratings, ranking) {
	return compute_ratings(old_ratings, transform(ranking));
    }

};

function postxhr(data, onsuccess) {
    $.post('xhr', btoa(JSON.stringify(data))) // use base64 encoding due to some strange server bug
    .done(function(data) {
	d = JSON.parse(data);
	if (! d.success) {
	    console.error('Unable to execute command: ' + data);
	}
	if (onsuccess) {
	    onsuccess(d);
	}
    })
    .fail(function(xhr, text, error) {
	console.error('Unable to execute command: ' + text + ' - ' + error);
    });
}


function get(a, b) {
    if (typeof(a) === 'undefined') {
	return b;
    }
    return a;
}


$(window).resize(function() {
    fitText()
});

$(document).ready(function() {
    fitText()
});

angular.module('darts', ['googlechart', 'ui.sortable'])
.factory('DartState', function($rootScope) {
    var _ = {};
    _.backendWsUri = window.location.href.replace(/^http(s?:\/\/[^/]*)\/.*$/, 'ws$1/websocket');
    _.sock = new ReconnectingWebSocket(_.backendWsUri);
    var initialBroadcastSent = false;
    var state = {};
    var settings = {
	sound: 'espeak',
	inputDevice: '',
	logging: true
    };

    _.sock.onopen = function() {
	console.log("Connected to " + _.backendWsUri);
	_.sock.send("hello");
    }

    _.sock.onclose = function(e) {
	console.log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
	state.state = 'connlost';
	$rootScope.$broadcast('dartstate.state_updated');
	$rootScope.$broadcast('dartstate.connection_lost');
    }

    _.sock.onmessage = function(e) {
	var message = JSON.parse(e.data);
	if (message.type == 'state') {
	    state = $.extend(state, message.state);
	    $rootScope.$broadcast('dartstate.state_updated');
	    if (typeof(message.state.ranking) !== 'undefined') {
		$rootScope.$broadcast('dartstate.ranking_updated');
	    }

	    if (state.state == 'null') {
		$rootScope.$broadcast('dartstate.no_game');
	    }

	    if (!initialBroadcastSent) {
		$rootScope.$broadcast('dartstate.new_game_started');
		initialBroadcastSent = true;
	    }

	} else if (message.type == 'info') {
	    if (message.info == 'game_initialized') {
		$rootScope.$broadcast('dartstate.new_game_started');
		initialBroadcastSent = true;
	    }
	} else if (message.type == 'settings') {
	    settings = $.extend(settings, message.settings);
	    $rootScope.$broadcast('dartstate.settings_updated');
	} else if (message.type == 'version') {
	    if (_.serverID == undefined) {
		_.serverID = message.version;
	    } else {
		if (_.serverID != message.version) {
		    window.location.reload();
		}
	    }
	}
    }

    return {
	state: state,
	settings: settings
	};
})

.controller('DartCtrl', ['$scope', '$timeout', '$filter', '$http', 'DartState',  function ($scope, $timeout, $filter, $http, DartState) {
    $scope.state = {};
    $scope.availablePlayers = Array();
    $scope.playersInChart = Array();
    $scope.initialValue = 301;
    $scope.predicate = 'started';
    $scope.chartUpdating = false; // chart is being updated (show loader)
    $scope.oldChartData = false; // We use this to only update the chart when something has actually changed.
    $scope.debugging = false;
    $scope.debugDartValue = 'T20';
    $scope.serverID = null;
    $scope.isOfficialGame = true;
    $scope.sortablePlayers = Array();
    $scope.sortPlayerDialogMode = 'new'; // 'new' means a new game should be started afterwards; 'update' means that the current list of players is to be updated instead

    $scope.availableBackends = [
	{'id': 'dartenbank', 'name': 'Official InfSec Dartenbank', backend: dartenbankBackend('http://infsec.uni-trier.de/dartenbank', $http)},
	{'id': 'dartenbug', 'name': 'Inofficial Dartenbank', backend: dartenbankBackend('http://x.uni-trier.de/dartenbank', $http)},
	{'id': 'nobackend', 'name': 'No Backend', backend: dummyBackend()},
	{'id': 'offline', 'name': 'Offline Test Backend', backend: offlineDartenbankBackend()}
    ];
    $scope.selectedBackend = null;

    
    var history = {};
    history.type="LineChart";
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
        },
	containerId: "mychart"
    };

    $scope.chart = history;

    $scope.$on('dartstate.new_game_started', function() {
	console.log("new game started");
	$('a[href="#order"]').trigger('click');
    });
    
    $scope.$on('dartstate.ranking_updated', function() {
	$scope.updateChartRanking();
    });

    $scope.$on('dartstate.no_game', function() {
	console.log("no game running");
	$('a[href="#newgame"]').trigger('click');
    });

    $scope.$on('dartstate.settings_updated', function() {
	$scope.settings = DartState.settings;
	$scope.$apply();
    });
    
    $scope.$on('dartstate.state_updated', function() {
	$scope.state = DartState.state;
	$scope.$apply();
	fitText();
    });

    $scope.skipPlayer = function(player) {
	postxhr({
	    command: 'skip-player',
	    player: player
	});
    }

    // ********************************************************************************
    // Starting a new Game
    // ********************************************************************************
    
    $scope.newGame = function(updatePlayers) {
	$scope.sortablePlayers = [];
	for (p in $scope.availablePlayers) {
	    if ($scope.availablePlayers[p].selected) {
		$scope.sortablePlayers.push($scope.availablePlayers[p]);
	    }
	}
	if ($scope.sortablePlayers.length < 2) {
	    alert("Please select at least two players.");
	    return;
	}
	if ($scope.backend.sortPlayers != undefined) {
	    $scope.sortablePlayers = $scope.backend.sortPlayers($scope.sortablePlayers);
	}
	$scope.sortPlayerDialogMode = updatePlayers ? 'update' : 'new';
	$('#sortPlayerDialog').modal('show');
    };

    $scope.actualNewGame = function() {
	var players = [];
	for (var i = 0; i < $scope.sortablePlayers.length; i ++) {
	    players.push($scope.sortablePlayers[i].name);
	}
	if ($scope.sortPlayerDialogMode == 'new') {
	    postxhr({
		command: 'new-game',
		players: players,
		startvalue: $scope.initialValue,
		testgame: $scope.startTestGame ? true : false
	    });
	    if ($scope.startTestGame) {
		sessionStorage['lastPlayers'] = JSON.stringify(players);
	    }
	} else {
	    postxhr({
		command: 'update-players',
		players: players
	    });
	}
	$('#sortPlayerDialog').modal('hide');
    };

    // ********************************************************************************
    // Updating the Chart
    // ********************************************************************************
    
    $scope.updateChartFull = function() {
	if (!$scope.backend.hasChart || ! $scope.state.players) {
	    return;
	}
	$scope.chartUpdating = true;
	$scope.backend.updateChartRanking($scope.state.ranking);
	$scope.backend.getChartData($scope.state.players, function (chartData) {
	    $scope.chartUpdating = false;
	    $scope.chart.data = chartData;
	}, function(error) {
	    $scope.chartUpdating = false;
	    console.error("Error updating chart from Dartenbank: " + error);

	});
    };

    $scope.updateChartRanking = function() {
	if ($scope.backend == undefined || !$scope.backend.hasChart || ! $scope.chart.data.rows) {
	     return;
	}
	$scope.backend.updateChartRanking(
	    $scope.state.ranking,
	    function (newChartData) {
		$scope.chart.data = newChartData;
	    }
	);
    }

    // ********************************************************************************
    

    $scope.submitResult = function() {
	if (!$scope.backend.submitResult) {
	    return;
	}
	var ranking = {};
	$.each($scope.state.ranking, function (i, info) {
	    ranking[info['name']] = info['rank'] + 1;
	});
	$scope.backend.submitResult(ranking);
    }

    $scope.updateAvailablePlayers = function() {
	if ($scope.backend == undefined) {
	    return;
	}
	$scope.chartUpdating = true;
	
	var lastPlayers = [];
	if (sessionStorage.getItem('lastPlayers') !== null) {
	    lastPlayers = JSON.parse(sessionStorage['lastPlayers']);
	}
	$scope.backend.getAvailablePlayers(lastPlayers, function(availablePlayers) {
	    $scope.availablePlayers = availablePlayers;
	    $scope.chartUpdating = false;
	    //$scope.$apply();	
	}, function (){
	    $scope.chartUpdating = false;
	    //$scope.$apply();
	});

    };

    $scope.addPlayer = function() {
	if ($scope.newPlayerName.length < 2 || $scope.newPlayerName.length > 3) {
	    alert("Player name must have 2 or 3 characters.");
	    return;
	}
	var cont = true;
	$.each($scope.availablePlayers, function(i, data) {
	    if (data.name == $scope.newPlayerName) {
		alert("Player name already exists.");
		cont = false;
	    }
	});
	if (cont) {
	    $scope.availablePlayers.push({
		name: $scope.newPlayerName, 
		games: 0, 
		rank: 0, 
		selected: true
	    });
	}
	$scope.newPlayerName = undefined;
    };

    $scope.formatDart = function(d) {
	l = d.length-1;
	if (d.substr(d.length-1, 1) == 'i') {
	    l -= 1;
	}
	d = d.substr(1, l);
	return d;
    };
    $scope.formatDartClass = function(d) {
	var mult = 'single';
	if (d.substring(0, 1) == 'D') {
	    mult = 'double';
	} else if (d.substring(0, 1) == 'T') {
	    mult = 'triple';
	}
	return 'dart ' + mult;
    }

    $scope.startEditingDarts = function(p) {
	p.editingLastDarts = true;
	if (typeof(p.last_frame.darts) === 'undefined') {
	    p.lastDartsEdited = '';
	} else {
	    p.lastDartsEdited = p.last_frame.darts.join(' ');
	}
    }

    $scope.saveDarts = function(p) {
	if (typeof(p.lastDartsEdited) === 'undefined') {
	    p.editingLastDarts = false;
	    return;
	}
	var input = p.lastDartsEdited;
	if (! /^([SDT]?(1?[0-9]|20)i?( [SDT]?(1?[0-9]|20)i?){0,2})?$/.test(input)) {
	    alert('Please adhere to the following format: ^[SDT]?(1?[0-9]|20)i?( [SDT]?(1?[0-9]|20)i?){0,2}$');
	    return;
	}
	postxhr({
            command: 'change-last-round',
	    player: p.started,
	    old_darts: p.last_frame.darts,
	    new_darts: (input == '') ? [] : input.split(' ')
	}, function(data) {
	    p.editingLastDarts = false;
	});
    }

    $scope.abortEditingDarts = function(p) {
	p.editingLastDarts = false;
    }

    $scope.undoLastFrame = function(p) {
        if (confirm("Do you want to undo this player's last frame?")) {
	    postxhr({
                command: 'undo-last-frame',
	        player: p.started
	    }, function(data) {
	           p.editingLastDarts = false;
	       });
	}

    }


    
    $(document).ready(function() {
	$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
	    if (e.target.hash == '#stats') {
		$scope.$emit('resizeMsg');
		$scope.updateChartFull();
	    }

	    if (e.target.hash == '#newgame') {
		$scope.updateAvailablePlayers();
		$scope.$apply();
	    }
	});

	/*$.ajax('config')
	.done(function(data){
 
			   if ($scope.currentBackend) {
			       try{
				   $scope.currentBackend.close();
			       } catch(e) {
				   console.log("While closing the previous backend (this may be harmless):");
				   console.log(e):
			       }
			   }
	});*/

    });


    // Selecting the right backend
    

    function selectBackend(selectedId) {
	if ($scope.backend == undefined || $scope.backend.id != selectedId) {
	    for (var i = 0; i < $scope.availableBackends.length; i++) {
		if (selectedId == $scope.availableBackends[i].id) {
		    // backend has changed
		    $scope.backend = $scope.availableBackends[i].backend;
		    $scope.selectedBackend = selectedId;
		    $scope.updateAvailablePlayers();
		    localStorage['selectedBackend'] = selectedId;
		    return;
		}
	    }
	} else {
	    return;
	}
	console.log("Could not find id: " + selectedId);
	console.log("Trying now: " + $scope.availableBackends[0].id);
	selectBackend($scope.availableBackends[0].id);
    };

    if (localStorage['selectedBackend'] != undefined) {
	selectBackend(localStorage['selectedBackend']);
    } else {
	selectBackend($scope.availableBackends[0].id);
    }

    $scope.backendChanged = function () {
	selectBackend($scope.selectedBackend);
    };

    // For debugging...
    $scope.onKeypress = function(ev) {
	if (ev.which == 100) {
	    $scope.debugging = ! $scope.debugging;
	}
    }

    $scope.debugThrowDart = function() {
	postxhr({
	    command: 'debug-throw-dart',
	    dart: $scope.debugDartValue
	});
    }

    $scope.debugNextPlayer = function() {
	postxhr({
	    command: 'debug-next-player',
	    dart: $scope.debugDartValue
	});
    }

    $scope.applySettings = function () {
	postxhr({
	    command: 'apply-settings',
	    settings: $scope.settings
	});
    }

    $scope.debugPerformSelfUpdate = function () {
	postxhr({
	    command: 'perform-self-update'
	});
    }

    $scope.cancelGame = function () {
	postxhr({
	    command: 'cancel-game'
	});
    }

}]).directive("clickToEditDarts", function() {
    var editorTemplate = '<div class="click-to-edit">' +
	'<div ng-hide="view.editorEnabled">' +
	'{{value}} ' +
	'<a ng-click="enableEditor()"><i class="fa fa-edit"></i></a>' +
	'</div>' +
	'<div ng-show="view.editorEnabled">' +
	'<input ng-model="view.editableValue" class="form-control">' +
	'<a href="#" ng-click="save()"><i class="fa fa-check"></i></a>' +
	'<a ng-click="disableEditor()"><i class="fa fa-times"></i></a>.' +
	'</div>' +
	'</div>';

    return {
	restrict: "A",
	replace: true,
	template: editorTemplate,
	scope: {
	    value: "=clickToEdit",
	    player: "=clickToEditPlayer",
	},
	controller: function($scope) {
	    $scope.view = {
		editableValue: $scope.value,
		editorEnabled: false
	    };

	    $scope.enableEditor = function() {
		$scope.view.editorEnabled = true;
		$scope.view.editableValue = $scope.flattenDarts($scope.value);
	    };

	    $scope.flattenDarts = function(darts) {
		return darts.join(' ');
	    }

	    /*$scope.saveDarts = function(input) {
		if (! /^[SDT]?(1?[0-9]|20)( [SDT]?(1?[0-9]|20)){0,2}$/.test(input)) {
		    return false;
		}
		postxhr({
		    command: 'change-last-round',
		    player: $scope.player,
		    new_darts: input.replace(/ /g, ','));
		       });
		return true;
	    }*/

	    $scope.disableEditor = function() {
		$scope.view.editorEnabled = false;
	    };

	    $scope.save = function() {
		$scope.saveDarts($scope.view.editableValue);
		//if (res) {
		//    $scope.value = $scope.view.editableValue;
		$scope.disableEditor();
	    };
	}
    };
});
