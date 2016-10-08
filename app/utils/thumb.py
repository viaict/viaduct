from PIL import Image, ImageChops
import app
import os


def thumb(url, size=(100, 100)):
    im_path = os.path.join(app.path, url.lstrip('/'))

    im_dir, im_name = os.path.split(im_path)

    im_title, im_ext = im_name.rsplit('.', 1)

    thmb_name = im_title + '-' + str(size[0]) + 'x' \
        + str(size[1]) + '.png'

    thmb_dir = os.path.join(im_dir, '.thumb')
    thmb_path = os.path.join(thmb_dir, thmb_name)

    if not os.path.exists(im_path):
        return url
    if not os.path.exists(thmb_dir):
        # TODO: Fix rights.
        os.mkdir(thmb_dir)
    if not os.path.exists(thmb_path):
        im = Image.open(im_path)
        im = im.convert('RGBA')

        if im.size[0] > im.size[1]:
            mod = float(size[0]) / im.size[0]
            x_off = 0
            y_off = int(((im.size[0] - im.size[1]) * mod) / 2)
        else:
            mod = float(size[1]) / im.size[1]
            x_off = int(((im.size[1] - im.size[0]) * mod) / 2)
            y_off = 0

        new_size = (int(im.size[0] * mod), int(im.size[1] * mod))
        im = im.resize(new_size)
        im = im.crop((0, 0, size[0], size[1]))

        im = ImageChops.offset(im, x_off, y_off)

        im.save(thmb_path)
        os.chmod(thmb_path, 0o644)

    slash = url.rindex('/')
    thmb_url = url[:slash] + '/.thumb/' + thmb_name

    return thmb_url
