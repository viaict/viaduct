from flask import flash
from werkzeug import secure_filename
import os
import difflib
import fnmatch
from app.models.file import File
from app import app, db
from flask_babel import lazy_gettext as _

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_DIR = app.config['UPLOAD_DIR']


def file_allowed_extension(filename, image=False):
    if filename == '':
        return False

    split = filename.rsplit('.', 1)

    if '.' in split[0]:
        return False

    if image and split[1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
        return False

    if not image and split[1].lower() not in ALLOWED_EXTENSIONS:
        return False

    return True


def file_upload(f, push_to_db=True, directory=None, image=False, 
                forced_name=None):
    if forced_name:
        filename = forced_name
    else:
        filename = f.filename

    # Check if an upload directory is provided
    if not directory:
        directory = UPLOAD_DIR

    # Check if the file is allowed.
    if not file_allowed_extension(filename, image):
        return

    # Convert the name.
    filename = secure_filename(filename)

    # check if the file exists if we force a filename
    if forced_name and file_exists(filename, directory):
        flash(_('An error occurred while uploading the file'),
              'danger')
        return

    # Add numbers for duplicate filenames.
    filename_noext, filename_ext = file_split_name(filename)
    counter = 1
    while file_exists(filename, directory):
        filename = '%s_%d.%s' % (filename_noext, counter, filename_ext)
        counter += 1
    
    # Save file.
    path = os.path.join(os.getcwd(), directory, filename)
    f.save(path)
    os.chmod(path, 0o644)

    # Add to database if needed
    new_file = File(filename)
    if push_to_db:
        db.session.add(new_file)
        db.session.commit()

    if new_file:
        flash(_('File created successfully'), 'success')

    else:
        flash(_('An error occurred while uploading the file'),
              'danger')

    return new_file


def file_exists(filename, directory=None):
    if not directory:
        directory = UPLOAD_DIR
    path = os.path.join(os.getcwd(), directory, filename)
    return os.path.exists(path)


def file_exists_pattern(pattern, directory=None):
    if not directory:
        directory = UPLOAD_DIR
    for file in os.listdir(directory):
        if fnmatch.fnmatch(file, pattern):
            return file
    return False


def file_split_name(filename):
    filename_split = filename.rsplit('.', 1)
    filename_noext = filename_split[0]
    filename_ext = filename_split[1]

    return filename_noext, filename_ext


def file_search(query):
    files = File.query.all()
    filenames = [f.name for f in files]
    results = difflib.get_close_matches(query, filenames, 10, 0.0)

    return results


def file_remove(filename, directory=None):
    if not directory:
        directory = UPLOAD_DIR
    try:
        os.remove(os.path.join(directory, filename))

        # Remove from database if necessary
        if directory == UPLOAD_DIR:
                db_entry = File.query.filter(File.name == filename)
                if db_entry.count() > 0:
                    db_entry.delete()

    except OSError:
        print(_('Cannot remove file, it does not exist') + ": " + filename)


def file_remove_pattern(pattern, directory=None):
    if not directory:
        directory = UPLOAD_DIR

    for file in os.listdir(directory):
        if fnmatch.fnmatch(file, pattern):

            # If our directory is equal to the upload directory, we check if
            # we need to remove the file name from the files table
            if directory == UPLOAD_DIR:
                db_entry = File.query.filter(File.name == file)
                if db_entry.count() > 0:
                    db_entry.delete()

            path = directory + file
            os.remove(path)
