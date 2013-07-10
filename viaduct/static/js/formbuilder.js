// Author: Fabien Tesselaar (https://github.com/Tessmore/formbuilder)

$.fn.formbuilder = function() {

	var info = $('<div class="alert alert-info"><b>Formulier commandos</b> Naam | type ' + 
							 '(Waar de type een "textarea", "radio", "checkbox" of "select" is)' +
							 '<p>Radio, checkbox en select opties maak je aan door de regels met <b>"-"</b> te beginnen. <p>Verder zijn er een paar shortcut "types" ("weekend", "shirt"), om automatisch meerdere velden in één keer aan te maken. <p><b>Bijvoorbeeld:</b><br>Dieet | checkbox<br>- Vlees<br>- Vegetarisch<br>- Veganist' +
'</div>');
  var textarea = $('<textarea name="origin" class="span6" style="min-height:200px" placeholder="Type hier je formulier commandos" />');
  var result   = $('<input type="hidden" name="html" />').hide();
  var form     = $('<form />');
  var group    = $('<div class="control-group" />');
  var controls = $('<div class="controls" />');
  var label    = $('<label class="control-label" />');
  
  var fields = {
    'text'     : $('<input type="text" name>'),
    'radio'    : $('<div />'),
    'checkbox' : $('<div />'),
    'textarea' : $('<textarea name />'),
    'select'   : $('<select name />')
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

      if (lines[i].charAt(0) == '>') {
        form.append('<p>' + lines[i].substring(1));
        continue;
      }
      
      options = parseLine(lines[i]);
      type    = options.type || "text";

			if (type === "weekend") {
				lines[i] = '';
        lines.splice(i, 0, 
					'Dieet | checkbox', 
					'-Vegetarisch', 
					'-Veganistisch', 

					'shirt',
					'Telefoon nr. in geval van nood',
					'> Waar moeten we rekening mee houden',
					'Allergie/medicatie | textarea'
				);

        textarea.val(lines.join("\n"));
				textarea.trigger('keyup');
        break;
			}

			if (type === "shirt") {
				lines[i] = '';
        lines.splice(i, 0, '', 
					'Shirt maat | select',
					'-Small',
					'-Medium',
					'-Large'
				);

        textarea.val(lines.join("\n"));
				textarea.trigger('keyup');
        break;
			}

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
          value = strip_(lines[i]);

          if (type === 'select')
            fields[type].append($('<option />').text(value));
          else
            fields[type].append(
              '<label class="checkbox">' +
                '<input type="' + type + '" name="' + options.name + '[]" value="' + value + '"> ' + 
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
  
	function strip(str) {
		return str.replace(/[\+\*\-]/g, '');
	}

	function strip_(str) {
		return str.replace(/[\+\*\- ]/g, '');
	}

  function parseLine(line) {
    var line  = line.split("|");
    var label = strip(line[0]);
		var name  = $.trim(label).toLowerCase();

    if (label == "") // Skip empty lines
      return false;
          
    var options = {
      'label' : label,
      'name'  : name
    };
    
    if (line[1])
      options['type'] = strip_(line[1]);
		else if (options.name === 'weekend' || options.name === 'shirt')
			options['type'] = options.name;

    return options;
  }  
};
