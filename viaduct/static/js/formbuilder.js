// Author: Fabien Tesselaar (https://github.com/Tessmore/formbuilder)

$.fn.formbuilder = function() {  

	var info		 = $('<div class="alert alert-info"><b>Formulier commandos</b> Veldnaam | veldtype (textarea, radio, checkbox, select). Voor radio/checkbox/select moet je per optie "-" of "*" ervoor zetten.</div>');
  var textarea = $('<textarea name="origin" class="span6" style="min-height:200px" placeholder="Type hier je formulier commandos" />');
  var result   = $('<input type="hidden" name="html" />').hide();
  var form     = $('<form />');
  var group    = $('<div class="control-group" />');
  var controls = $('<div class="controls" />');
  var label    = $('<label class="control-label" />');
  
  var fields = {
    'text'     : $('<input type="text" name id>'),
    'radio'    : $('<div />'),
    'checkbox' : $('<div />'),
    'textarea' : $('<textarea name id />'),
    'select'   : $('<select name id></select>')
  };

  this
		.append(info)
    .append(textarea)
		.append('<h4>Voorbeeld van dit formulier</h4>')
    .append(form)
    .after(result); // contains the entire form

  textarea.on('keyup', function() {
    form.html(''); // Reset the control
    var lines = this.value.split("\n");
    
    for (var i=0; i < lines.length; i++) {
      if (lines[i].charAt(0) == '#') {
        form.append('<h3>' + lines[i].substring(1) + '</h3>');
        continue;
      }
      
      options = parseLine(lines[i]);
      type    = options.type || "text";
      
			/*
      if (type === "user") {
        lines[i] = '';
        lines.splice(i, 0, 'Student nr.', 'Email', 'Mobiel nr.');
        textarea.val(lines.join("\n"));
        break;
      }
			*/

      if (! options || !fields[type])
        continue;

      group
        .append(label.text(options.label))
        .append(
          controls.html(
            fields[type]
              .attr('name', options.name)
              .attr('id',   options.id)
         ));
      
      if (type === 'select' || type === 'radio' || type === 'checkbox') {
        fields[type].html(''); // Reset the list
        
        while (++i < lines.length && lines[i] && (lines[i].charAt(0) == '*' || lines[i].charAt(0) == '-')) {
          value = lines[i].substring(1);

          if (type === 'select')
            fields[type].append($('<option />').text(value));
          else
            fields[type].append(
              '<label class="checkbox">' +
                '<input type="' + type + '" name="' + (type === 'radio' ? options.name : value) + '" value="' + value + '"> ' + 
                value + 
              '</label>'
            );
        }
        
        i--; // Go back 1 step to parse the next element without #hashtag
      }
      
      group.clone().appendTo(form);
    }
    
    result.val('<div id="custom_form_data">' + form.html() + '</div>');
  });
  
  function parseLine(line) {
    var line = line.trim().split("|");
    var name = line[0];

    if (name == "") // Skip empty lines
      return false;
          
    var options = {
      label : name,
      name  : name.replace(/[ ]/g, '_')
    };
    
    if (line[1])
      options['type'] = line[1].replace(/[ ]/g, '');

    return options;
  }  
};
