from flask.ext.login import current_user
from viaduct import application, db
from viaduct.models.page import PagePermission
from viaduct.models.user import User
from viaduct.models.challenge import Challenge, Submission
from flask import flash
import os
import fnmatch
import urllib
import hashlib

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

        return new_challenge.name


    @staticmethod
    def fetch_challenge(id):
        """
        Update a challenge, only give the id and new values that have to change.
        """
        challenge = Challenge.query.filter_by(id = id).first()
        return challenge

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
            db.session.add(challenge)
            db.session.commit()
            return 'Approved'
        else:
            return 'Bad answer'


    @staticmethod
    def fetch_unvalided_submissions(challenge_id):
        return Submission.query.filter_by(challenge_id = challenge_id).all()

    @staticmethod
    def fetch_all_challenges():
        return Challenge.query.all()

    @staticmethod
    def is_open_challenge(challenge_id):
        challenge = Challenge.filter(and_(Challenge.start_date <
                                     datetime.utcnow(), Challenge.end_date >
                                     datetime.utcnow())).first()
        if challenge is not None:
            return True
        else:
            return False