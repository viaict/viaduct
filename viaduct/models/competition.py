from viaduct import db
from viaduct.models import BaseEntity


user_team = db.Table(
    'competition_user_team',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('competition_team.id'))
)


class Relation(db.Model):
    __tablename__ = 'ladder_team_rel'

    ladder_id = db.Column(db.Integer, db.ForeignKey('competition_ladder.id'),
                          primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('competition_team.id'),
                        primary_key=True)
    rating = db.Column(db.Integer)
    team = db.relationship("Team", backref="relation")


class Ladder(db.Model, BaseEntity):
    __tablename__ = 'competition_ladder'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    teams = db.relationship("Relation", backref="ladder")

    def __init__(self, name):
        self.name = name

    def has_team(self, team):
        if not team:
            return False
        else:
            return self.teams.filter(Relation.team_id == team.id).count() > 0

    def add_team(self, team):
        if not self.has_team(team):
            r = Relation(rating=1200)
            r.team = team
            self.teams.append(r)

            return self

    def remove_team(self, team):
        # not yet done
        return self

    def get_teams(self):
        return self.teams


class Team(db.Model, BaseEntity):
    __tablename__ = 'competition_team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    total_rating = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', secondary=user_team,
                            backref=db.backref('teams', lazy='dynamic'),
                            lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def has_user(self, user):
        if not user:
            return False
        else:
            return self.users.filter(user_team.c.user_id == user.id)\
                .count() > 0

    def add_user(self, user):
        if not self.has_user(user):
            self.users.append(user)

            return self

    def delete_user(self, user):
        if self.has_user(user):
            self.users.remove(user)

    def get_users(self):
        return self.users
