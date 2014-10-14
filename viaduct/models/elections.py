from viaduct import db
from viaduct.models import BaseEntity, User


class Nominee(db.Model, BaseEntity):
    __tablename__ = 'dvhj_nominee'

    prints = ('id', 'name')

    name = db.Column(db.String(256))

    def __init__(self, name=None):
        self.name = name

    def nominate(self, user):
        if not user.has_payed:
            raise Exception('Je moet betaald lid zijn om een docent te '
                            'nomineren')

        if user.nominations.count() >= Nomination.MAX_PER_USER:
            raise Exception('Je mag maar %d docenten per persoon nomineren' %
                            (Nomination.MAX_PER_USER))

        if user.nominations.filter(Nomination.nominee_id == self.id).first():
            raise Exception('Je mag een docent maar een keer nomineren.')

        nomination = Nomination(self, user)
        db.session.add(nomination)
        db.session.commit()

        return nomination


class Nomination(db.Model, BaseEntity):
    __tablename__ = 'dvhj_nomination'

    MAX_PER_USER = 4

    nominee_id = db.Column(db.Integer, db.ForeignKey('dvhj_nominee.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified = db.Column(db.Boolean)

    nominee = db.relationship(Nominee, backref=db.backref('nominations',
                                                          lazy='dynamic'))
    user = db.relationship(User, backref=db.backref('nominations',
                                                    lazy='dynamic'))

    def __init__(self, nominee=None, user=None):
        self.nominee = nominee
        self.user = user
        self.verified = False
