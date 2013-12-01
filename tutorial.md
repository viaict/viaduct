## Overview of viaduct  

First of all there are several relevant folders:  
* views  
* models  
* api  
* templates  

Except for template files in these folders should be named after the module.

I hope the general work flow will be clear after explaining what these folders
contain.

### Views  
More about views: http://flask.pocoo.org/docs/


Here are the entry points of the site. Lets take a look at Pimpy:  

blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')

This means the blueprints name is pimpy. This is important for the routes and
the permissions:  

@blueprint.route('/minutes/', methods=['GET', 'POST'])
@blueprint.route('/minutes/<group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
	if not GroupPermissionAPI.can_read('pimpy'):
		return abort(403)
	return PimpyAPI.get_minutes(group_id)

When someone visits the page the url is parsed to see if a route can be found,
if a route can be found that the function of that route is called. Such a
function should render a page or forward to the 403 page.  

In this case www.svia.nl/pimpy/minutes or www.svia.nl/pimpy/1 will both work. In
the second case an argument can be parsed from the url (we do not want
to work with get variables etc), this value will be stored in the key word
argument.  

Such a function should then render a page from templates and supply the template
with structured data. So views should first structure the data so the templates
can easily render the data. Views does not have to do this itself, it can also
make use of an api (in case the required data is also used elsewhere).

Our current system works in such a manner that the permissions are checked in
all view functions. This is what the GroupPermissionAPI does. Our example
function uses the PimpyAPI to render a page. An example of how a template can be
called:

render_template('pimpy/add_task.htm', group=group,
		group_id=group_id, type='tasks', form=form)

group, group_id, type and form are variables that can be used in the templates.

### Templates:  
In the templates folder are htm files with in line python code. 

Check jinja: http://jinja.pocoo.org/docs/templates/

Templates can make api calls as well. This can be useful to fill in standard
parts of the page, such as the menu.


### Models  
Models have objects that are directly linked with database tables. Check the
tutorials here:  
http://pythonhosted.org/Flask-SQLAlchemy/

It basically allows you to create instances of table entries of the database.
Manipulating data is very easy with sqlalchemy.

### API  
API contains function calls that can structure data and/or render templates. You
use the api to render pages if the pages should be rendered on multiple
locations (you do not want to copy view functions but rather have the view
function use the api).  
