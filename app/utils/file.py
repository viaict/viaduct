import difflib
import fnmatch
import os

from flask import flash
from flask_babel import lazy_gettext as _
from werkzeug.utils import secure_filename

from app import app, db
from app.models.file import File

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_DIR = app.config['UPLOAD_DIR']


# Check if the extension is allowed. Set image to True to allow only image-
# extensions
def file_allowed_extension(filename, image=False):
    if filename == '':
        return False

    split = filename.rsplit('.', 1)

    if image and split[1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
        return False

    if not image and split[1].lower() not in ALLOWED_EXTENSIONS:
        return False

    return True


# Upload a file. You can specify a directory, whether or not the file is
# supposed to be an image (for extension checking) and if the name needs to
# be forced to be a certain value (used for avatars)
def file_upload(f, directory=UPLOAD_DIR, image=False, filename=None):
    """
    Save a file onto the file system.

    :param f: FileStorage object retrieved from the
    :param directory: Save file in this directory
    :param image: Require file to be an image.
    :param filename: Save file using this filename, ignore FileStorage name
    :return:
    """
    if not filename:
        filename = f.filename
        forced_name = False
    else:
        forced_name = True

    # Check if the file is allowed.
    if not file_allowed_extension(filename, image):
        flash(_("%s is not an allowed file type." % filename), 'danger')
        return

    # Convert the name.
    filename = secure_filename(filename)

    # check if the file exists if we force a filename
    if forced_name and file_exists(filename, directory):
        flash(_('An error occurred while uploading the file'),
              'danger')
        return

    # Add numbers for duplicate filenames.
    filename_root, filename_ext = os.path.splitext(filename)
    counter = 1
    while file_exists(filename, directory):
        filename = '%s_%d.%s' % (filename_root, counter, filename_ext)
        counter += 1

    # Save file.
    path = os.path.join(os.getcwd(), directory, filename)
    f.save(path)
    os.chmod(path, 0o644)

    # Add to database if needed
    new_file = File(filename)
    if directory == UPLOAD_DIR:
        db.session.add(new_file)
        db.session.commit()

    # if new_file:
    #     flash(_('File created successfully'), 'success')

    else:
        flash(_('An error occurred while uploading ' + filename),
              'danger')

    return new_file


# Check if a file exists in a certain optional directory
def file_exists(filename, directory=UPLOAD_DIR):
    path = os.path.join(os.getcwd(), directory, filename)
    return os.path.exists(path)


# Check if a file meeting a certain pattern exists in an optional directory
def file_exists_pattern(pattern, directory=UPLOAD_DIR):
    for file in os.listdir(directory):
        if fnmatch.fnmatch(file, pattern):
            return file
    return False


# Find files in de databases for a certain query
def file_search(query):
    files = File.query.all()
    filenames = [f.name for f in files]
    results = difflib.get_close_matches(query, filenames, 10, 0.0)

    return results


# Remove a file from an optional directory and from the database if this
# directory is the default directory
def file_remove(filename, directory=UPLOAD_DIR):
    try:
        os.remove(os.path.join(directory, filename))

        # Remove from database if necessary
        if directory == UPLOAD_DIR:
            db_entry = File.query.filter(File.name == filename)
            if db_entry.count() > 0:
                db_entry.delete()

    except OSError:
        print(_('Cannot remove file, it does not exist') + ": " + filename)


# Remove files meeting a certain pattern from a directory and from the
# database if we want to remove them from the default directory
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
