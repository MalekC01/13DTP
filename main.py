from flask import Flask, render_template, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config
import random

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Config)

import models
import forms
from image_exif import exif_for_image


#error messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images/uploads'

# {% for picture in files %}
#     <img src="{{ url_for(path, filename=picture) }}">
# {% endfor %} 


#https://www.freecodecamp.org/news/how-to-create-an-image-gallery-with-css-grid-e0f0fd666a5c/
#home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    pictures_for_slideshow = models.Photo.query.filter_by(orientation="Landscape").all()
    print("slideshow: " + str(pictures_for_slideshow))
    images_id_slides = [(str(id.id), id.url) for id in pictures_for_slideshow]
    print(images_id_slides)

    random_index = random.sample(images_id_slides, 3)
    print(random_index)

    return render_template('home.html', title="Home", random_index=random_index)



@app.route('/gallery', methods=['GET', 'POST'])
def gallery():

    url_of_all_images = models.Photo.query.all()
    print("raw: " + str(url_of_all_images))
    id_url = [(str(url.id), url.url, url.orientation) for url in url_of_all_images]
    random.shuffle(id_url)
    print("before: " + str(id_url))

    picture_format_options = ["grid-item--width2", "grid-item--width3"]

    with_format = [width_type + (random.choice(picture_format_options),) for width_type in id_url]
    print("with format: " + str(with_format))


    return render_template('gallery.html', id_url=with_format)


@app.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    image_data = models.Photo.query.filter_by(id=id).all()
    info_of_image = [(str(info.id), info.url, info.orientation) for info in image_data]
    print(info_of_image)

    data_for_image = exif_for_image(info_of_image)

    if info_of_image[0][2] == "Portrait":
        format_of_image = "Portrait"
    else:
        format_of_image = "Landscape"

    tags_for_image = models.Photo_tag.query.filter_by(pid=id).all()
    print("tags: " + str(tags_for_image))
    tags_of_image = [(tags.tid) for tags in tags_for_image]
    print("All ids: " + str(tags_of_image))

    list_of_tags = []
    for all_tags in tags_of_image:
        tags_id_image = models.Tags.query.filter_by(id=all_tags).all()
        tags_name = [(tags_name.tag_name) for tags_name in tags_id_image]
        list_of_tags.append(tags_name)
        print("All tags: " + str(tags_name))
    print(list_of_tags)

    return render_template('photo.html', title="Info", info_of_image=info_of_image, data_for_image=data_for_image, tags_of_image=tags_of_image, list_of_tags=list_of_tags, format_of_image=format_of_image)

#returns on all pages
# @app.contect_processor()
# def contect_processor():


@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    form = forms.Add_Photo()
    #query database for all tags
    all_tags = models.Tags.query.all()
    tags_for_form = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.tags.choices = tags_for_form
    print(form.tags.choices)

    #query database for all previous locations
    all_locations = models.Locations.query.all()
    locations_for_form = [(str(location.id), location.location_name) for location in all_locations]
    form.locations.choices = locations_for_form
    print(form.locations.choices)


    if request.method=='GET':  # did the browser ask to see the page
        return render_template('add.html', form=form)
    else:  # its a POST, ie: the user clicked SUBMIT
        print("submission")
        print(form.tags.data)
        if form.validate_on_submit():

            print("Form Submitted")

            uploaded_file = request.files['display-image']
            filename = uploaded_file.filename
            print("filename: " + str(filename))
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            photo_url = str( "uploads/" + filename)



            check_duplicate_photo = models.Photo.query.filter_by(url=photo_url).all()
            print("checkduplicate: " + str(check_duplicate_photo))
            duplicate_found = False

            if check_duplicate_photo == []:
                #Take ncea input from form and get ready to be inputted into database
                orientation = form.orientation.data
                print("orientation: " + str(orientation))

                ncea_level = form.ncea.data
                if ncea_level == "Level 1":
                    ncea_level = "1"
                elif ncea_level == "Level 2":
                    ncea_level = "2"
                else:
                    ncea_level = "Not NCEA"
                print("NCEA LEVEL: " + str(ncea_level))

                locations_chosen = form.locations.data
                print("locations chosen: " + str(locations_chosen))

            
                new_location = form.new_location.data
                print("New location: " + str(new_location))
                if new_location != '':
                    #change to if any instead of querying all
                    check_location_duplicate = models.Locations.query.filter_by(location_name=new_location).all()
                    if check_location_duplicate == []:
                        add_location = models.Locations(location_name=new_location)
                        db.session.add(add_location)
                        db.session.commit()
                    find_location_id = models.Locations.query.filter_by(location_name=new_location).all()
                    location_id_list = [(str(location.id)) for location in find_location_id]
                    location_id = location_id_list[0]
                    print(location_id)
                else:
                    location_id = form.locations.data


                new_tag = form.new_tag.data
                if new_tag != '':
                    print("Checking new tag")
                    check_tag_duplicate = models.Tags.query.filter_by(tag_name=new_tag).all()
                    print(check_tag_duplicate)
                    if check_tag_duplicate == []:
                        add_tag = models.Tags(tag_name=new_tag)
                        db.session.add(add_tag)
                        db.session.commit()


                add_photo_url = models.Photo(url=photo_url, location=location_id, ncea=ncea_level, orientation=orientation)
                db.session.add(add_photo_url)
                db.session.commit()

                find_photo_id = models.Photo.query.filter_by(url=photo_url).all()
                photo_id_list = [(str(photo.id)) for photo in find_photo_id]
                photo_id = photo_id_list[-1]
            

                tags_chosen = form.tags.data
                print(tags_chosen)

                find_tag_id = models.Tags.query.filter(models.Tags.id.in_(tags_chosen)).all()
                tag_id_list = [(str(tag.id)) for tag in find_tag_id]
            
                    
                for tag in tag_id_list:
                    add_tag_and_photo = models.Photo_tag(pid=photo_id, tid=tag)
                    db.session.add(add_tag_and_photo)
        
                
                db.session.commit()
            else:
                print("Photo already in database.")
                duplicate_found = True


            return render_template('add.html', form=form, filename=filename, title="Add", duplicate_found=duplicate_found)

        return render_template('add.html', form=form, title="Add")

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)