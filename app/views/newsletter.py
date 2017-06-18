from flask import Blueprint, request, render_template, redirect, url_for,\
    flash, Response, abort
from flask_babel import _

from app import app, db
from app.utils.module import ModuleAPI
from app.forms.newsletter import NewsletterForm
from app.models.newsletter import Newsletter

blueprint = Blueprint('newsletter', __name__, url_prefix='/newsletter')


@blueprint.route('/', methods=['GET'])
def all():
    if not ModuleAPI.can_read('newsletter'):
        return abort(403)

    newsletters = Newsletter.query.all()
    return render_template('newsletter/view.htm', newsletters=newsletters)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:newsletter_id>/', methods=['GET', 'POST'])
def edit(newsletter_id=None):
    if not ModuleAPI.can_write('newsletter'):
        return abort(403)

    if newsletter_id:
        newsletter = Newsletter.query.get_or_404(newsletter_id)
    else:
        newsletter = Newsletter()

    form = NewsletterForm(request.form, newsletter)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(newsletter)
        db.session.add(newsletter)
        db.session.commit()

        flash(_('Newsletter saved'), 'success')
        return redirect(url_for('.all'))

    return render_template('newsletter/edit.htm', newsletter=newsletter,
                           form=form)


@blueprint.route('/delete/<int:newsletter_id>/', methods=['GET', 'POST'])
def delete(newsletter_id):
    if not ModuleAPI.can_write('newsletter'):
        return abort(403)

    if request.method == 'GET':
        return render_template('newsletter/confirm.htm')

    newsletter = Newsletter.query.get_or_404(newsletter_id)
    db.session.delete(newsletter)
    db.session.commit()

    return redirect(url_for('.all'))


def correct_token_provided():
    token = request.args.get('auth_token')
    return app.config['COPERNICA_NEWSLETTER_TOKEN'] == token


def get_newsletter(newsletter_id=None):
    if newsletter_id:
        return Newsletter.query.get_or_404(newsletter_id)
    else:
        return Newsletter.query.order_by(Newsletter.id.desc()).first()


@blueprint.route('/<int:newsletter_id>/activities/', methods=['GET'])
@blueprint.route('/latest/activities/', methods=['GET'])
def activities_xml(newsletter_id=None):
    if not ModuleAPI.can_read('newsletter') and not correct_token_provided():
        return abort(403)

    newsletter = get_newsletter(newsletter_id)
    return Response(render_template('newsletter/activities.xml',
                                    items=newsletter.activities),
                    mimetype='text/xml')


@blueprint.route('/<int:newsletter_id>/news/', methods=['GET'])
@blueprint.route('/latest/news/', methods=['GET'])
def news_xml(newsletter_id=None):
    if not ModuleAPI.can_read('newsletter') and not correct_token_provided():
        return abort(403)

    newsletter = get_newsletter(newsletter_id)
    return Response(render_template('newsletter/news.xml',
                                    items=newsletter.news_items),
                    mimetype='text/xml')
