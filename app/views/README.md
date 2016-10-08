# Views
## Coding conventions

 - The naming of the blueprint must be equal to the basename of the file:
    `blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')` is in
    `pimpy.py`.
 - Views that show data of non-open modules should always check `can_read`
     permission.
 - Views never use extended logic. It processes incoming data from forms or JSON
     and generates output data. Extended logic should always go into util.
 - Often create and edit functions for forms can be combined, please do so and
     name it `def edit():`, so that the URL can be generated using, for example:
     `url_for('user.edit')` for the create view and `url_for('module.edit',
     user_id=69')` for editing user with id 69.

        @blueprint.route('/users/create/', methods=['GET', 'POST'])
        @blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
        def edit(user_id=None):

 - Always put a docstring on a view, explaining the usage of view.

## Documentation
More about views: [http://flask.pocoo.org/docs/](http://flask.pocoo.org/docs/)

Here are the entry points of the site. Lets take a look at Pimpy:

	blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')

This means the blueprints name is pimpy. This is important for the routes and
the permissions:

	@blueprint.route('/minutes/', methods=['GET', 'POST'])
	@blueprint.route('/minutes/<group_id>', methods=['GET', 'POST'])
    @some_other_decorator
	def view_minutes(group_id='all'):
        """Generate a list of minutes (for a group)."""
		if not ModuleAPI.can_read('pimpy'):
			return abort(403)
		return PimpyAPI.get_minutes(group_id)

When someone visits a page the url is parsed to see if a route can be found.
If a route can be found, then the function of that route is called. Such a
function should render a page or forward to another page.

In this case `svia.nl/pimpy/minutes` or `svia.nl/pimpy/minutes/1` will
both work. In the second case an argument can be parsed from the url (we do not
want to work with get variables etc), this value will be stored in the keyword
argument `group_id`.

This function should then render a page from templates and supply the template
with structured data. Views should first structure the data so the templates
can easily render the data. Views does not have to do this itself, it can also
make use of an utility function from `app/utils/*.py`. Whenever the data is
reused in different locations/functions, do create a utils function!

Our current system works in such a manner that the permissions are checked in
all view functions. This is what the `ModuleAPI` does. Our example function uses
the `PimpyAPI` to render a page. An example of how a template can be called:

	render_template('pimpy/add_task.htm', group=group,
			group_id=group_id, type='tasks', form=form)

The keyword arguments `group`, `group_id`, `type` and `form`, used in the
`render template` function are variables that are available in the template that
is being rendered.

