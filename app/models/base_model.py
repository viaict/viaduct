"""Extra functionality that is used by all models. It extends db.Model with
extra functions."""

from app import db
from app.utils.serialize_sqla import serialize_sqla
from datetime import datetime
import dateutil.parser


class BaseEntity(object):
    __table_args__ = {'sqlite_autoincrement': True}

    # Columns (in order) to be printed when an instance of the object is
    # printed
    prints = ('id',)

    # Columns to be shown when the to_dict function is used. This should only
    # be changed when certain values should not be shown in the dictionary.
    # Relationships should be added when a relationship is supposed to be in
    # the dictionary as well.
    json_excludes = tuple()
    jsons = None
    json_relationships = None
    json_relationship_ids = tuple()

    # Columns that every model needs
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, default=datetime.now,
                         onupdate=datetime.now)

    # Get all entries.
    @classmethod
    def get_all(cls):
        return cls.query.all()

    # Get entry by id.
    @classmethod
    def by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    # Remove entry by id.
    @classmethod
    def remove_by_id(cls, _id):
        entry = cls.by_id(_id)

        if entry is None:
            return

        db.session.delete(entry)
        db.session.commit()

    # Get entries by id list.
    @classmethod
    def by_ids(cls, ids):
        try:
            return db.session.query(cls).filter(cls.id.in_(ids)).all()
        except:
            return []

    # Function used by print to print a model at server side.
    # It uses the prints attribute from the object to determine what values to
    # print. This attribute is the id of the object by default.
    def __repr__(self):
        first = True
        string = '<%s(' % (type(self).__name__)

        for attr in self.prints:
            if not first:
                string += ', '
            string += '"%s"' % (getattr(self, attr))
            first = False

        string += ')>'

        return string

    # Functionality after this point is a bit hard to understand. Just read the
    # function comments and that should be enough.

    # Function to convert a sqlalchemy object instance to a dictionary. This is
    # needed for json serialization of an object. The jsons attribute is used
    # to determine what values to serialize (password hashes and such should
    # not in there)
    def to_dict(self, exclude=True, **kwargs):
        attrs = {}

        if not self.jsons or not exclude:
            if exclude:
                jsons = (column.name for column in self.__table__.columns if
                         column.name not in self.json_excludes)
            else:
                jsons = (column.name for column in self.__table__.columns)
        else:
            jsons = self.jsons

        for column in jsons:
            value = serialize_sqla(getattr(self, column), **kwargs)
            attrs[column] = value

        if self.json_relationships:
            for rel in self.json_relationships:
                attrs[rel] = serialize_sqla(getattr(self, rel).all(), **kwargs)

        for rel in self.json_relationship_ids:
            attrs[rel] = tuple(a[0] for a in getattr(self, rel).values('id'))

        return attrs

    # Function that automatically parses a dictionary to the model. It will
    # change the the entry that it finds with the id. All other key value pairs
    # will be parsed to column value pairs. The entry will also be saved.
    @classmethod
    def merge_dict(cls, obj, relationships={}):

        # Get the correct entry from the database
        if 'id' in obj and obj['id']:
            entry = cls.by_id(obj['id'])
            if not entry:
                return None

        # If the dict doesn't contain id it means the entry does not exist yet
        else:
            entry = cls()

        # Remove id, created and modified, since those are things you want to
        # automaticaly update
        obj.pop('id', None)
        obj.pop('created', None)
        obj.pop('modified', None)

        column_names = tuple(column.name for column in cls.__table__.columns)

        # Update all values from the dict that exist as a column or a
        # relationship
        for key, value in list(obj.items()):
            if key in column_names:
                columntype = str(cls.__table__.columns[key].type)
                if columntype == 'DATE' and value is not None:
                    if isinstance(value, str):
                        value = dateutil.parser.parse(value)
                elif columntype == 'TIME' and value is not None:
                    if isinstance(value, str):
                        value = dateutil.parser.parse(value).time()

                setattr(entry, key, value)

            elif key in relationships:
                setattr(entry, key, relationships[key].by_ids(value))

        db.session.add(entry)
        db.session.commit()
        return entry

    # For future proofing use new_dict when creating new entries, so it could
    # become a separate function if needed
    new_dict = merge_dict
