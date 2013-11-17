

function fitText() {
  var divisors = [4, 12, 18];
  for (var d in divisors) {
    $( '.fit-height-body-' + divisors[d] ).each(function ( i, box ) {
      $(box).css('font-size', $(window).height()/divisors[d]);
    });
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
    var wsuri = "ws://localhost:9000";
    if ("WebSocket" in window) {
      sock = new WebSocket(wsuri);
    } else if ("MozWebSocket" in window) {
      sock = new MozWebSocket(wsuri);
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
      $scope.state.state = 'connlost';
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