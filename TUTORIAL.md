## Overview of viaduct

First of all there are several relevant folders:

- views
- models
- api
- templates

Except for template files in these folders should be named after the module.

I hope the general work flow will be clear after explaining what these folders
contain.

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
