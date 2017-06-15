from flask import Blueprint, request, render_template, redirect, url_for,\
    flash, Response, render_template_string
from flask_babel import _
from app import db
from app.forms.newsletter import NewsletterForm
from app.models.newsletter import Newsletter

blueprint = Blueprint('newsletter', __name__, url_prefix='/newsletter')


@blueprint.route('/', methods=['GET'])
def all():
    newsletters = Newsletter.query.all()
    return render_template('newsletter/view.htm', newsletters=newsletters)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:newsletter_id>/', methods=['GET', 'POST'])
def edit(newsletter_id=None):
    # TODO check for admin
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
    # TODO check for admin

    # TODO make this its own template
    if request.method == 'GET':
        return render_template_string('''
            {% extends "content.htm" %}

            {% block content %}
            <h1>{{ _('Delete') }}</h1>
            <h2>{{ _('Are you sure you want to delete this entry?') }}</h2>
            <form method="POST">
                <input type="submit" class="btn btn-danger"
                       value="{{ _('Yes') }}">

                <a href="{{ url_for('.all') }}" class="btn btn-primary">
                    {{ _('No') }}
                </a>
            </form>
            {% endblock %}
        ''')

    newsletter = Newsletter.query.get_or_404(newsletter_id)
    db.session.delete(newsletter)
    db.session.commit()

    return redirect(url_for('.all'))


@blueprint.route('/<int:newsletter_id>/activities/', methods=['GET'])
def activities_xml(newsletter_id):
    newsletter = Newsletter.query.get_or_404(newsletter_id)
    headers = {'Content-disposition': 'attachment; filename=activities.xml'}
    return Response(render_template('newsletter/activities.xml',
                                    items=newsletter.activities),
                    mimetype='text/xml', headers=headers)


@blueprint.route('/<int:newsletter_id>/news/', methods=['GET'])
def news_xml(newsletter_id):
    newsletter = Newsletter.query.get_or_404(newsletter_id)
    headers = {'Content-disposition': 'attachment; filename=news.xml'}
    return Response(render_template('newsletter/news.xml',
                                    items=newsletter.news_items),
                    mimetype='text/xml', headers=headers)
