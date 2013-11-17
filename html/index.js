

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