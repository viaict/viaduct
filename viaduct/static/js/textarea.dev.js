// Licensed "AS IF" by Fabien Tesselaar (June 7, 2012)
// Automatic textarea resizing
//  - Dependency = throttle (and assumes twitter bootstrap css)
$.fn.textarea = function() {
  return this.each(function() {
    var holder = $('<div class="span6"></div>')
      .css({'display':'none', 'text-align':'justify'})
      .appendTo('body');
      
    $(this)
      .after('<span id="scroll_me"><span>')
      .css('overflow', 'hidden')
      .keyup($.throttle(250, resize));
    
    function resize() {
      holder.html(
        this.value
          .replace(/</g, '&lt;')
          .replace(/\n/g, '<br>')
      );

      var current = $(this).height();
      var real    = holder.height()+5;
      
      if (current < real || real-20 < current)
        $(this).css('height', real).stop(true, true).animate({height:real+10}, 140);
    }
    
  });
};