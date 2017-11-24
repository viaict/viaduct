from app.forms import SeoForm

from app import db
from app.utils.module import ModuleAPI
from app.utils.seo import get_seo, get_resources
from app.models.seo import SEO


from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request
from flask_babel import _  # gettext


blueprint = Blueprint('seo', __name__, url_prefix='/seo')


@blueprint.route('/edit', methods=['GET', 'POST'])
@blueprint.route('/edit/', methods=['GET', 'POST'])
def edit_seo():
    # TODO CHANGE THIS TO SEO
    if not ModuleAPI.can_write('seo'):
        return abort(403)

    module = request.args['module']
    path = request.args['path']

    seo = get_seo(module, path)

    # Retrieve form info.
    form = SeoForm(request.form, obj=seo)

    # On Seo submit (edit or create)
    if form.validate_on_submit():
        if seo:
            # Edit the seo entry
            seo.nl_title = form.nl_title.data.strip()
            seo.en_title = form.en_title.data.strip()
            seo.nl_description = form.nl_description.data.strip()
            seo.en_description = form.en_description.data.strip()
            seo.nl_tags = form.nl_tags.data.strip()
            seo.en_tags = form.en_tags.data.strip()

            db.session.add(seo)
            db.session.commit()
        if not seo:
            # Get seo resources to indentify the seo in the database.
            res = get_resources(module, path)

            # Create the new seo entry
            seo = SEO(res['page'],
                      res['page_id'],
                      res['activity'],
                      res['activity_id'],
                      res['url'],
                      form.nl_title.data.strip(),
                      form.en_title.data.strip(),
                      form.nl_description.data.strip(),
                      form.en_description.data.strip(),
                      form.nl_tags.data.strip(),
                      form.en_tags.data.strip())

            db.session.add(seo)
            db.session.commit()

        flash(_('The seo settings have been saved'), 'success')

        # redirect newly created page
        return redirect(url_for('page.get_page', path=path))

    return render_template('seo/edit.htm', form=form)
