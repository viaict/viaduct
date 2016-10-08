### Templates:
Check jinja: [http://jinja.pocoo.org/docs/templates/](http://jinja.pocoo.org/docs/templates/)

In the templates folder are htm files with in-line python code. Don't use the
.html extension.

Templates can make use of custom filters, which are located in the
`app/utils/template_filters.py`.

Templates can make calls to `utils` as well. This can be useful to fill in
standard parts of the page, such as the menu. However to use these need to be
defined in the `app/__init__.py` file.
