## Overview of viaduct

First of all there are several relevant folders:

- views
- models
- api
- templates

Except for template files in these folders should be named after the module.

I hope the general work flow will be clear after explaining what these folders
contain.

### Templates:
In the templates folder are htm files with in-line python code.

Check jinja: [http://jinja.pocoo.org/docs/templates/](http://jinja.pocoo.org/docs/templates/)

Templates can make api calls as well. This can be useful to fill in standard
parts of the page, such as the menu.


### Models
Models have objects that are directly linked with database tables. Check the
tutorials here:
[http://pythonhosted.org/Flask-SQLAlchemy/](http://pythonhosted.org/Flask-SQLAlchemy/)

It basically allows you to create instances of table entries of the database.
Manipulating data is very easy with sqlalchemy.

### Utils
Utils contain function calls that can structure data and/or render templates.
You use the utils to render pages if the pages should be rendered on multiple
locations (you do not want to copy view functions but rather have the view
function use the util).
