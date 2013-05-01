// Licensed "AS IF" by Fabien Tesselaar (June 7, 2012)
// Automatic textarea resizing
//  - Dependency = throttle (and assumes twitter bootstrap css)
$.fn.flexible = function() {  
  return this.each(function() {
    var holder = $('<div class="span6"></div>')
      .css({'display':'none'})
      .appendTo('body');
 
    $(this)
      .keyup($.throttle(40, resize))
      .resize(); // resize on startup
    
    function resize() {
      holder.html( '<br>' + this.value.replace(/</g, '&lt;').replace(/\n/g, '<br>') + '<br>');
      $(this).css('height', holder.height());
    }
  });
};
