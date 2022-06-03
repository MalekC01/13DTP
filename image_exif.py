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

from exif import Image

def exif_for_image(info_of_image):
    with open("/Users/malekconnor/Desktop/13DTP/static/images/" + str(info_of_image[0][1]), "rb") as photo_file:
        photo = Image(photo_file)

    image_tag_list = dir(photo)

    focal_length = photo.focal_length
    date = photo.datetime
    exposure = photo.exposure_time
    f_stop = photo.f_number

    data = [focal_length, date, exposure, f_stop]

    return data