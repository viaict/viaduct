from app import db
from app.models import BaseEntity, User


class Nominee(db.Model, BaseEntity):
    __tablename__ = 'dvhj_nominee'

    prints = ('id', 'name', 'valid')

    name = db.Column(db.String(256))
    valid = db.Column(db.Boolean)

    def __init__(self, name=None):
        self.name = name

    def nominate(self, user):
        if not user.has_paid:
            raise Exception('Je moet betaald lid zijn om een docent te '
                            'nomineren')

        nominee_ids = [n.nominee_id for n in user.nominations.all()]
        nomination_n = Nominee.query.filter(Nominee.id.in_(nominee_ids))\
            .filter(db.or_(Nominee.valid == None, Nominee.valid == 1))\
            .count()  # noqa
        if nomination_n >= Nomination.MAX_PER_USER:
            raise Exception('Je mag maar %d docenten per persoon nomineren' %
                            (Nomination.MAX_PER_USER))

        if user.nominations.filter(Nomination.nominee_id == self.id).first():
            raise Exception('Je mag een docent maar een keer nomineren.')

        nomination = Nomination(self, user)
        db.session.add(nomination)
        db.session.commit()

        return nomination

    def vote(self, user):
        if not user.has_paid:
            raise Exception('Je moet betaald lid zijn om te stemmen')

        if user.vote:
            vote = user.vote[0]
            vote.nominee = self
        else:
            vote = Vote(self, user)

        db.session.add(vote)
        db.session.commit()

        return vote


class Nomination(db.Model, BaseEntity):
    __tablename__ = 'dvhj_nomination'

    prints = ('id', 'nominee', 'user')

    MAX_PER_USER = 4

    nominee_id = db.Column(db.Integer, db.ForeignKey('dvhj_nominee.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    nominee = db.relationship(Nominee, backref=db.backref('nominations',
                                                          lazy='dynamic'))
    user = db.relationship(User, backref=db.backref('nominations',
                                                    lazy='dynamic'))

    def __init__(self, nominee=None, user=None):
        self.nominee = nominee
        self.user = user


class Vote(db.Model, BaseEntity):
    __tablename__ = 'dvhj_vote'

    prints = ('id', 'nominee', 'user')

    nominee_id = db.Column(db.Integer, db.ForeignKey('dvhj_nominee.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    nominee = db.relationship(Nominee, backref=db.backref('votes',
                                                          lazy='dynamic'))
    user = db.relationship(User, backref='vote')

    def __init__(self, nominee=None, user=None):
        self.nominee = nominee
        self.user = user
