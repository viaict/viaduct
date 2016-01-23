// Author: Fabien Tesselaar (https://github.com/Tessmore/formbuilder)

$.fn.formbuilder = function() {

  var info = $('<div class="alert alert-info"><a target="_blank" href="https://github.com/Tessmore/formbuilder">Tips en voorbeelden!</a></div>');
  var textarea = $('<textarea name="origin" class="form-control" style="min-height:200px" placeholder="Type hier je formulier commandos" />');
  var result   = $('<input type="hidden" name="html" />').hide();
  var form     = $('<form />');
  var group    = $('<div class="form-group" />');
  var label    = $('<label />');

  var fields = {
    'text'     : $('<input class="form-control" type="text" name>'),
    'radio'    : $('<div />'),
    'checkbox' : $('<div />'),
    'textarea' : $('<textarea class="form-control" name />'),
    'select'   : $('<select class="form-control" name />')
  };

  this
    .append(info)
    .append(textarea)
    .append('<div class="input-group">')
    .append('<h4>Voorbeeld van dit formulier</h4>')
    .append('</div>')
    .append(form)
    .after(result); // contains the entire form

  // Build the form on ENTER, losing focus or after certain periods of typing
  textarea.on('keyup change', function() {
    form.html(''); // Reset the form

    if (typeof this === "undefined") {
      return;
    }

    var lines = this.value.split("\n");

    for (var i=0, N=lines.length; i<N; i++) {
      // Skip empty lines
      if (lines[i].trim() === "") {
        // Multiple empty lines is whitespace
        if (i+1 < N && lines[i+1].trim() === "")
          form = appendText(form, '<br>');

        continue;
      }

      // Allow whitespacing
      if (lines[i].trim() === "---") {
        form = appendText(form, '<br>');
        continue;
      }

      /**
        Start checking for symbols
      */

      var firstChar = lines[i].charAt(0);

      // (sub) title
      if (firstChar === '#') {
        form = appendText(form, '<h3>' + lines[i].substring(1) + '</h3>');
        continue;
      }

      // Plain text / descriptions
      if (firstChar == '=') {
        form = appendText(form, '<p>' + lines[i].substring(1) + '</p>');
        continue;
      }

      // Label description
      if (firstChar == '>') {
        // Add description to recently added label
        form.find('label')
          .last()
          .after('<small>' + lines[i].substring(1) + '</small>');

        continue;
      }

      // Macro's
      if (startsWith(lines[i], "weekend*")) {
        lines.splice(i, 1,
          'Dieet | checkbox',
          '- Vegetarisch',
          '- Veganistisch',

          'shirt*',

          'Noodnummer*',
          '> Telefoon nummer in geval van nood',
          'Allergie/medicatie | textarea',
          '> Waar moeten we rekening mee houden'
        );

        textarea.val(lines.join("\n"));
        textarea.trigger('keyup');
        break;
      }

      if (startsWith(lines[i], "shirt*")) {
        lines.splice(i, 1,
          'Maat shirt* | select',
          '- Small',
          '- Medium',
          '- Large'
        );

        textarea.val(lines.join("\n"));
        textarea.trigger('keyup');
        break;
      }


      /**
        Check what type of field must be inserted
      */

      options = parseLine(lines[i]);

      group
        .attr('req', options.required)
        .append(label.text(options.label))
        .append(fields[options.type]
              .attr('name', options.name)
              .attr('id',   options.id)
         );

      if (options.type === 'select' || options.type === 'radio' || options.type === 'checkbox') {
        fields[options.type].html(''); // Reset the list

        while (++i < lines.length && lines[i] && (lines[i].charAt(0) == '*' || lines[i].charAt(0) == '-')) {
          value = ltrim(lines[i]);

          if (options.type === 'select')
            fields[options.type].append($('<option />').text(value));
          else {

            fields[options.type].append(
              '<div class="' + options.type + '">' +
              '<label>' +
                '<input type="' + options.type + '" name="' + options.name + '[]" value="' + value + '">' +
                value +
              '</label>'
            );
          }
        }

        i--; // Go back 1 step to parse the next element
      }

      group.clone().appendTo(form);
      group.empty();
    }

    result.val('<div id="custom_form_data">' + form.html() + '</div>');
  });

  function appendText(form, str) {
    if (form.children().length > 0)
      form.children().last().after(str);
    else
      form.prepend(str);

    return form;
  }

  function parseLine(line) {
    var line  = line.split("|");
    var label = line[0].trim();

    // Just take first 12 chars to avoid very long key names
    var name  = label.substring(0,12).replace(/[ ]/g, '_').toLowerCase();

    var options = {
      'label'    : label,
      'name'     : name,
      'type'     : "text",
      'required' : line[0].indexOf('*') > -1 ? "true" : "false"
    };

    if (line[1])
      options['type'] = guessType(line[1]);

    return options;
  }

  function guessType(str) {
    if (contains(str, "rad"))
      return "radio";
    else if (contains(str, "check"))
      return "checkbox"
    else if (contains(str, "sele"))
      return "select"
    else if (contains(str, "area"))
      return "textarea"
    else
      return "text";
  }

  function ltrim(str) {
    var temp = str.trim();

    if (startsWith(str, '-') || startsWith(str, '*'))
      temp = temp.substring(1).trim();

    return temp;
  }

  function contains(str, sub) {
    return str.indexOf(sub) > -1;
  }

  function startsWith(str, sub) {
    return str.substring(0, sub.length).trim().toLowerCase() === sub.toLowerCase();
  }
}
