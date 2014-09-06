from flask.ext.login import current_user
from viaduct import application, db
from viaduct.models.page import PagePermission
from viaduct.models.user import User
from viaduct.models.challenge import Challenge, Submission, Competitor

from sqlalchemy import or_, and_
from flask import flash
import os
import fnmatch
import urllib
import hashlib
import datetime

from flask import render_template

from viaduct.models.group import Group
from viaduct.api.file import FileAPI

ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg'])
UPLOAD_DIR = 'viaduct/static/files/users/'


class ChallengeAPI:
    @staticmethod
    def create_challenge(name, description, hint, start_date, end_date,
                        parent_id, weight, type, answer):
        """
        Create a new challenge
        """
        new_challenge = Challenge(name, description, hint, start_date, end_date,
                            parent_id, weight, type, answer)
        db.session.add(new_challenge)
        db.session.commit()

        return "Succes, challenge with name '" + new_challenge.name +\
                "' created!"    

    @staticmethod
    def edit_challenge(id, name, description, hint, start_date, end_date,
                        parent_id, weight, type, answer):
        """
        Create a new challenge
        """
        challenge = ChallengeAPI.fetch_challenge(id)
        challenge.name = name
        challenge.description = description
        challenge.hint = hint
        challenge.start_date = start_date
        challenge.end_date = end_date
        challenge.parent_id = parent_id
        challenge.weight = weight
        challenge.type = type
        challenge.answer = answer
        db.session.add(challenge)
        db.session.commit()

        return "Succes, challenge with name '" + new_challenge.name +\
                "' edited!"


    @staticmethod
    def fetch_challenge(id):
        """
        Update a challenge, only give the id and new values that have to change.
        """
        challenge = Challenge.query.filter_by(id = id).first()
        return challenge

    @staticmethod
    def challenge_exists(name):
        """
        Update a challenge, only give the id and new values that have to change.
        """
        challenge = Challenge.query.filter_by(name = name).first()

        if challenge is None:
            return False
        else:
            return True

    @staticmethod
    def update_challenge(challenge):
        """
        Give the altered challenge object
        """
        db.session.add(challenge)
        db.session.commit()

    @staticmethod
    def create_submission(challenge_id=None, user_id=None,
                 submission=None, image_path=None):
        """
        Create a submission for a challenge and user
        """
        if ChallengeAPI.is_approved(challenge_id, user_id) or \
                not ChallengeAPI.is_open_challenge(challenge_id):
            return False

        challenge = ChallengeAPI.fetch_challenge(challenge_id)
        user = User.query.filter_by(id = user_id).first()
        # convert the name.
        new_submission = Submission(challenge_id,
                 challenge, user_id, user,
                 submission, image_path, approved=False)
        db.session.add(new_submission)
        db.session.commit()        

        return new_submission

    @staticmethod
    def can_auto_validate(challenge):
        """
        Check if a challenge can be auto validated. 

        """
        if challenge.type == 'Text':
            return True
        else:
            return False

    @staticmethod
    def validate_question(submission, challenge):
        """
        Check if a question is valid
        """
        if not ChallengeAPI.can_auto_validate(challenge):
            return 'Not validated'

        if submission.submission == challenge.answer:
            submission.approved = True
            ChallengeAPI.assign_points_to_user(challenge.weight, submission.user_id)
            db.session.add(submission)
            db.session.commit()
            return 'approved'
        else:
            return 'Bad answer'


    @staticmethod
    def fetch_unvalided_submissions(challenge_id):
        return Submission.query.filter_by(challenge_id = challenge_id).all()

    @staticmethod
    def fetch_all_challenges():
        # return Challenge.query.join(Submission).filter(Submission.user_id == current_user.id, Submission.approved == False)
        return Challenge.query.all()

    @staticmethod
    def fetch_all_challenges_user(user_id):
        subq = Challenge.query.join(Submission).filter(and_(Submission.user_id == user_id, Submission.approved == True))
        return Challenge.query.except_(subq).filter(and_(Challenge.start_date <=
                                     datetime.date.today(), Challenge.end_date >=
                                     datetime.date.today())).all()
    @staticmethod
    def fetch_all_approved_challenges_user(user_id):
        return Challenge.query.join(Submission).filter(Submission.user_id == user_id, Submission.approved == True)

    @staticmethod
    def is_open_challenge(challenge_id):
        challenge = Challenge.query.filter(and_(Challenge.start_date <=
                                     datetime.date.today(), Challenge.end_date >=
                                     datetime.date.today())).first()
        if challenge is None:
            return False
        else:
            return True

    @staticmethod
    def is_approved(challenge_id, user_id):
        submission = Submission.query.filter(and_(Submission.user_id == user_id, 
                                            Submission.challenge_id == challenge_id,
                                            Submission.approved == True)).first()

        if submission is None:
            return False
        else:
            return True


    @staticmethod
    def get_points(user_id):
        competitor = Competitor.query.filter(Competitor.user_id == user_id).first()

        if competitor is None:
            return None
        else:
            return competitor.points

    @staticmethod
    def assign_points_to_user(points, user_id): 
        competitor = Competitor.query.filter(Competitor.user_id == user_id).first()

        if competitor is None:
            competitor = Competitor(user_id)
            competitor.points = points
            db.session.add(competitor)
            db.session.commit()
        else:
            competitor.points = competitor.points + points
            db.session.add(competitor)
            db.session.commit()

    @staticmethod
    def get_ranking():
        competitors = Competitor.query.order_by(Competitor.points.desc()).all()
        return competitors