"""

add_width_and_height_to_db.py

Grabs width and height from actual image files for a .json database that is missing w/h.

TODO: this is a one-off script waiting to be cleaned up for more general use.

"""

#%% Imports and constants

import json
from PIL import Image
from megadetector.utils import ct_utils

datafile = '/datadrive/snapshotserengeti/databases/snapshotserengeti.json'
image_base = '/datadrive/snapshotserengeti/images/'

def main(): # noqa

    with open(datafile,'r') as f:
        data = json.load(f)

    for im in data['images']:
        if 'height' not in im:
            im_w, im_h = Image.open(image_base+im['file_name']).size
            im['height'] = im_h
            im['width'] = im_w

    ct_utils.write_json(datafile, data, indent=None)

if __name__ == '__main__':
    main()
