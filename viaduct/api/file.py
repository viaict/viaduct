from flask import flash
from werkzeug import secure_filename
import os
import difflib
from viaduct.models.file import File
from viaduct import app, db

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_DIR = app.config['UPLOAD_DIR']


class FileAPI:
    '''
    API for files.
    '''

    @staticmethod
    def upload(f):
        filename = f.filename

        # Check if the file is allowed.
        if '.' not in filename or \
                not filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            flash('Bestandstype is niet toegestaan.', 'danger')
            return

        # Convert the name.
        filename = secure_filename(filename)

        # Add numbers for duplicate filenames.
        filename_noext, filename_ext = FileAPI.split_name(filename)
        counter = 1
        while FileAPI.exists(filename):
            filename = '%s_%d.%s' % (filename_noext, counter, filename_ext)
            counter += 1

        # Save file.
        path = os.path.join(os.getcwd(), UPLOAD_DIR, filename)
        f.save(path)

        # Add to database.
        new_file = File(filename)
        db.session.add(new_file)
        db.session.commit()

        if new_file:
            flash('Het bestand is succesvol geupload onder de naam '
                  '<em>%s</em>' % (new_file.name))
        else:
            flash('Er is iets misgegaan, waarschuw de ICT-commissie', 'danger')

        return new_file

    @staticmethod
    def exists(filename, upload_dir=None):
        if not upload_dir:
            upload_dir = UPLOAD_DIR
        path = os.path.join(os.getcwd(), upload_dir, filename)
        return os.path.exists(path)

    @staticmethod
    def split_name(filename):
        filename_split = filename.rsplit('.', 1)
        filename_noext = filename_split[0]
        filename_ext = filename_split[1]

        return filename_noext, filename_ext

    @staticmethod
    def search(query):
        files = File.query.all()
        filenames = [f.name for f in files]
        results = difflib.get_close_matches(query, filenames, 10, 0.0)

        return results
