from app import db, get_locale
from app.models import Page, Activity, BaseEntity


from flask.ext.babel import lazy_gettext as _

""" Meta tags for pages, activities and modules for SEO 
    Please use with the provided SEO API.
    @author Bram van den Akker
"""
class SEO(db.Model, BaseEntity):
    __tablename__ = 'seo'

    nl_title = db.Column(db.Text)
    en_title = db.Column(db.Text)
    nl_description = db.Column(db.Text)
    en_description = db.Column(db.Text)
    nl_tags = db.Column(db.Text)
    en_tags = db.Column(db.Text)

    # Necessary page columns.
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    page = db.relationship(
        'Page', backref=db.backref('seo', lazy='dynamic'))

    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))

    activity = db.relationship(
        'Activity', backref=db.backref('seo', lazy='dynamic'))

    url = db.Column(db.Text)

    def __init__(self, page=None, page_id=None, activity=None, activity_id=None, 
                 url=None, nl_title='', en_title='', 
                 nl_description='', en_description='',
                 nl_tags='', en_tags=''):
        self.page = page
        self.activity = activity
        self.activity_id = activity_id
        self.url = url

        self.nl_description = nl_description
        self.en_description = en_description
        self.nl_title = nl_title
        self.en_title = en_title
        self.nl_tags = nl_tags
        self.en_tags = en_tags

    @staticmethod
    def get_by_activity(activity_id):
        return SEO.query.filter(SEO.activity_id == activity_id).first()

    @staticmethod
    def get_by_page(page_id):
        return SEO.query.filter(SEO.page_id == page_id).first()

    @staticmethod
    def get_by_url(url):
        return SEO.query.filter(SEO.url == url).first()