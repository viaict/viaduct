import datetime

from viaduct import db
from viaduct.models import Group


page_ancestor = db.Table('page_ancestor',
    db.Column('page_id', db.Integer, db.ForeignKey('page.id')),
    db.Column('ancestor_id', db.Integer, db.ForeignKey('page.id'))
)

class Page(db.Model):
    __tablename__ = 'page'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    path = db.Column(db.String(256), unique=True)
    needs_payed = db.Column(db.Boolean)

    parent = db.relationship('Page',
            remote_side=id,
            backref=db.backref('children', lazy='dynamic'))
    ancestors = db.relationship('Page', secondary=page_ancestor,
        primaryjoin=id==page_ancestor.c.page_id,
        secondaryjoin=id==page_ancestor.c.ancestor_id,
        backref=db.backref('descendants', lazy='dynamic'), lazy='dynamic')
    revisions = db.relationship('PageRevision', backref='page', lazy='dynamic')

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return '<Page(%s, "%s")>' % (self.id, self.path)

    @staticmethod
    def get_by_path(path):
        return Page.query.filter(Page.path==path).first()

    def has_revisions(self):
        return self.revisions.count() > 0

    def can_read(self, user):
        if(PagePermission.get_user_rights(user, self.id) > 0):
            return True
        else:
            return False

    def can_write(self, user):
        if(PagePermission.get_user_rights(user, self.id) > 1):
            return True
        else:
            return False

    def get_newest_revision(self):
        return self.revisions.order_by(PageRevision.timestamp.desc()).first()

class PageRevision(db.Model):
    __tablename__ = 'page_revision'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    filter_html = db.Column(db.Boolean)
    content = db.Column(db.Text)
    comment = db.Column(db.String(1024))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    # Allow a form to be added to a page
    form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))

    author = db.relationship('User', backref=db.backref('page_edits',
        lazy='dynamic'))

    def __init__(self, page, author, title, content, comment="", filter_html=True,
            timestamp=datetime.datetime.utcnow(), form_id=None):
        self.title = title
        self.content = content
        self.comment = comment
        self.filter_html = filter_html
        self.user_id = author.id if author != None else -1
        self.page_id = page.id
        self.timestamp = timestamp
        self.form_id   = form_id

class PagePermission(db.Model):
    __tablename__ = 'page_permission'

    id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.Integer)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    page = db.relationship('Page', backref=db.backref('permissions',
                           lazy='dynamic'))

    def __init__(self, group_id, page_id, permission=0):
        self.permission = permission
        self.group_id = group_id
        self.page_id = page_id

    @staticmethod
    def get_user_rights(user, page_id):
        rights = 0

        if not user or not user.is_active():
            groups = [Group.query.filter(Group.name=='all').first()]
        else:
            groups = user.groups.all()

        page = Page.query.filter(Page.id==page_id).first()

        if page:
            for group in groups:
                if group.name == 'administrators':
                    return 2

                permissions = PagePermission.query.filter(PagePermission.page_id==page.id,
                    PagePermission.group_id==group.id).first()
                if permissions:
                    if (permissions.permission >= 2) :
                        return permissions.permission

                    if (permissions.permission > rights):
                        rights = permissions.permission

        return rights

    def set_permission(self, permission):
        self.permission = permission
