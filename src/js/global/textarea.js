// Licensed "AS IF" by Fabien Tesselaar (June 7, 2012)
// Automatic textarea resizing
//  - Dependency = throttle (and assumes twitter bootstrap css)
$.fn.flexible = function() {  
  return this.each(function() {
		$(this).addClass('span6');

    var holder = $('<div class="span6"></div>')
      .css({'display':'none'})
      .appendTo('body');
 
    $(this)
      .keyup($.throttle(20, resize));

    function resize() {
      holder.html(this.value.replace(/</g, '&lt;').replace(/\n/g, '<br>') + '<br><br>');
      $(this).css('height', holder.height());
    }
  });
};

$(document).ready(function() {
	// Initialize flexible textareas and include a keyup trigger
	// so it resizes on startup
	$('textarea').flexible().trigger('keyup');
});
