from app import db
from app.models.user import User
import csv

with open('copernica.csv', 'r') as f:
    reader = csv.reader(f)
    users = list(reader)

    for user in users:
        User.query.filter(User.id == int(user[1]))\
            .update({User.copernica_id: int(user[0])})

    db.session.commit()
