

function fitText() {
  var divisors = [4, 12, 18];
  for (var d in divisors) {
    $( '.fit-height-body-' + divisors[d] ).each(function ( i, box ) {
      $(box).css( 'font-size', $(window).height()/divisors[d] );
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
  $scope.currentPlayer = 'AB';
  $scope.currentScore = '299';
  $scope.currentDarts = [{text: 'T20'}, {text: 'D1'}];
  $scope.hold = false;
  $scope.players = [
    {rank: 3, name: 'GH', lastround: 'T20 D3 S1', score: 199},
    {rank: 1, name: 'DH', lastround: 'S1 D3 S1', score: 0}
  ];

  window.setTimeout(function() { $scope.currentPlayer = '??'; $scope.$apply();}, 2000);
}