import os
from exif import Image
import pathlib


def exif_for_image(image_data):
    try:
        # takes initial adress from name
        file_name = image_data.url[8:]

        path = pathlib.Path(file_name).parent.absolute()

        with open(str(path) + "/static/images/" + str(image_data.url), "rb") as photo_file:
            photo = Image(photo_file)

        image_tag_list = dir(photo)

        # gathers data about image and adds to dictionary
        data = {}
        data['focal_length'] = photo.focal_length
        data['date'] = photo.datetime[:10]
        data['exposure_time'] = round(photo.exposure_time, 4)
        data['aperture'] = photo.f_number

        return data
    except BaseException:
        data = None
        return data
