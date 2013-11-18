

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

function DartCtrl($scope) {
  $scope.state = {};

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
      $scope.$apply();
      fitText();
    }
  });
}