from PIL import Image
import viaduct
import os


def thumb(url, size=(100, 100)):
    im_path = os.path.join(viaduct.path, url.lstrip('/'))

    im_dir, im_name = os.path.split(im_path)

    im_title, im_ext = im_name.rsplit('.', 1)

    thmb_name = im_title + '-' + str(size[0]) + 'x' \
        + str(size[1]) + '.' + im_ext

    thmb_dir = os.path.join(im_dir, '.thumb')
    thmb_path = os.path.join(thmb_dir, thmb_name)

    if not os.path.exists(im_path):
        return url
    if not os.path.exists(thmb_dir):
        # TODO: Fix rights.
        os.mkdir(thmb_dir)
    if not os.path.exists(thmb_path):
        im = Image.open(im_path)
        im.thumbnail(size)
        im.save(thmb_path)

    slash = url.rindex('/')
    thmb_url = url[:slash] + '/.thumb/' + thmb_name

    return thmb_url
