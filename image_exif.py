# from exif import Image

# def exif_for_image(info_of_image):
#     with open("/Users/malekconnor/Desktop/13DTP/static/image/uploads/_MG_3642.JPG", "rb") as photo_file:
#         photo = Image(photo_file)

#     image_tag_list = dir(photo)

#     print("Focal length: " + str(photo.focal_length))
#     print("Date taken: " + str(photo.datetime))
#     print("Shutter speed: " + str(photo.exposure_time))
#     print("Appeture: f/" + str(photo.f_number))

    
#     #"/static/image/" + str(info_of_image[0][1])
#"/Users/malekconnor/Desktop/13DTP/static/images/" + str(info_of_image[0][1])
import os
from exif import Image
import pathlib

def exif_for_image(info_of_image):
    print("before format: " + str(info_of_image))
    file_name = info_of_image[0][1][8:]
    print("File name: " + str(file_name))
    
    path = pathlib.Path(file_name).parent.absolute()
    print("path: " + str(path))
 
    with open(str(path) + "/static/images/" + str(info_of_image[0][1]), "rb") as photo_file:
        photo = Image(photo_file)
        print("Running image")

    image_tag_list = dir(photo)

    focal_length = photo.focal_length
    date = photo.datetime
    exposure = photo.exposure_time
    f_stop = photo.f_number
    print("Running data")
    data = [focal_length, date, exposure, f_stop]
    print(data)

    return data

