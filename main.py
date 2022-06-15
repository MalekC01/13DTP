from flask import Flask, render_template, request, redirect
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config
import random

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Config)

#imports python files
import models
import forms
from image_exif import exif_for_image


#error messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images/uploads'


#home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    #choses random images in correct format to display on home screen
    pictures_for_slideshow = models.Photo.query.filter_by(orientation="Landscape").all()
    images_id_slides = [(str(id.id), id.url) for id in pictures_for_slideshow]
    random_index = random.sample(images_id_slides, 3)


    return render_template('home.html', title="Home", random_index=random_index)

#sends error redirects to error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

#page for all ncea images
@app.route('/ncea', methods=['GET', 'POST'])
def ncea():
    return render_template('ncea.html')

#all image to do with level 2 ncea
@app.route('/level_2', methods=['GET', 'POST'])
def level_2():
    all_level_2_images = models.Photo.query.filter_by(ncea=2).all()
    level_2 = [(str(images.id), images.url) for images in all_level_2_images]
    return render_template('level_2.html', level_2=level_2)

#all images to do with level 3 ncea
@app.route('/level_3', methods=['GET', 'POST'])
def level_3():
    all_level_3_images = models.Photo.query.filter_by(ncea=3).all()
    level_3 = [(str(images.id), images.url) for images in all_level_3_images]
    
    return render_template('level_3.html', level_3=level_3)

#gallery queriies to display images
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():

    display_all = True
    form = forms.Filter_images()
    #queries database for all current tags, returns so can dusplay for filtering
    all_tags = models.Tags.query.all()
    tags_for_filter = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.options.choices = tags_for_filter

    #queries for all images in database and returns with url so src can display in html
    url_of_all_images = models.Photo.query.all()
    id_url = [(str(url.id), url.url, url.orientation) for url in url_of_all_images]
    
    #shuffles list indexes so each time page is refreshed order of images will change
    random.shuffle(id_url)
    
    if request.method=='GET':  # did the browser ask to see the page
        return render_template('gallery.html', id_url=id_url, form=form, display_all=display_all)
    else:  # its a POST, the user clicked SUBMIT
        print("post")
        if form.options.data == None:
            return redirect("gallery.html")
        else:
            image_url = None
            display_all = False
 
            #takes all tags selected in filter form and queries for the ids
            tags_to_search = []
            for tag_ids in form.options.data:
                chosen_tags = models.Tags.query.filter_by(id=tag_ids).all()
                filtered_images = [(str(tag.id)) for tag in chosen_tags]
                tags_to_search.append(filtered_images)
            
            #uses tag ids to then find the images that contain that tag
            photo_ids = []
            for tag_id in tags_to_search[:len(tags_to_search)][0]:
                search_for_photo_id = models.Photo_tag.query.filter_by(tid=tag_id).all()
                image_id = [(str(image_id.pid)) for image_id in search_for_photo_id]
                photo_ids.append(image_id)
            
            #query format
            photo_ids = photo_ids[0]
    
            #uses all image ids for tags selected then get url so can be displayed
            urls = []
            for data in photo_ids:
                search_for_photo_url = models.Photo.query.filter_by(id=data).all()
                image_url = [(str(url_and_id.id),url_and_id.url) for url_and_id in search_for_photo_url]
                urls.append(image_url)
            #randomises order to be displayed
            random.shuffle(urls)

            return render_template('gallery.html', form=form, image_url=urls, display_all=display_all)



@app.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    #queries image selected to retireve
    image_data = models.Photo.query.filter_by(id=id).all()
    info_of_image = [(str(info.id), info.url, info.orientation) for info in image_data]
    data_for_image = exif_for_image(info_of_image)

    #used so can change depedniding orrientation of image
    if info_of_image[0][2] == "Portrait":
        format_of_image = "Portrait"
    else:
        format_of_image = "Landscape"

    #queries database for all tags linked with selected
    tags_for_image = models.Photo_tag.query.filter_by(pid=id).all()
    tags_of_image = [(tags.tid) for tags in tags_for_image]

    list_of_tags = []
    for all_tags in tags_of_image:
        tags_id_image = models.Tags.query.filter_by(id=all_tags).all()
        tags_name = [(tags_name.tag_name) for tags_name in tags_id_image]
        list_of_tags.append(tags_name)


    return render_template('photo.html', title="Info", info_of_image=info_of_image, data_for_image=data_for_image, tags_of_image=tags_of_image, list_of_tags=list_of_tags, format_of_image=format_of_image)

#add new images to databsae
@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    form = forms.Add_Photo()

    #query database for all tags
    all_tags = models.Tags.query.all()
    tags_for_form = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.tags.choices = tags_for_form

    #query database for all previous locations
    all_locations = models.Locations.query.all()
    locations_for_form = [(str(location.id), location.location_name) for location in all_locations]
    form.locations.choices = locations_for_form



    if request.method=='GET':  # did the browser ask to see the page
        return render_template('add.html', form=form)
    else:  # its a POST, ie: the user clicked SUBMIT
        if form.validate_on_submit():
            #uplaoding image to local files
            uploaded_file = request.files['display-image']
            filename = uploaded_file.filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            photo_url = str( "uploads/" + filename)

            #check image hasnt already been uploaded
            check_duplicate_photo = models.Photo.query.filter_by(url=photo_url).all()
            duplicate_found = False

            #if no duplicate image has been found add to database
            if check_duplicate_photo == []:
                #Take ncea input from form and get ready to be inputted into database
                orientation = form.orientation.data

                #ncea data from form
                ncea_level = form.ncea.data
                if ncea_level == "Level 2":
                    ncea_level = "2"
                elif ncea_level == "Level 3":
                    ncea_level = "3"
                else:
                    ncea_level = "Not NCEA"

                #location data from form
                locations_chosen = form.locations.data
                new_location = form.new_location.data
                #if new location tag isnt empty add to database
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
                else:
                    location_id = form.locations.data

                #if new tag isnt empty add to database
                new_tag = form.new_tag.data
                if new_tag != '':
                    check_tag_duplicate = models.Tags.query.filter_by(tag_name=new_tag).all()
                    if check_tag_duplicate == []:
                        add_tag = models.Tags(tag_name=new_tag)
                        db.session.add(add_tag)
                        db.session.commit()

                #add image with all data from form and image file 
                add_photo_url = models.Photo(url=photo_url, location=location_id, ncea=ncea_level, orientation=orientation)
                db.session.add(add_photo_url)
                db.session.commit()

                #find image id within database after being commited so next query can be made
                find_photo_id = models.Photo.query.filter_by(url=photo_url).all()
                photo_id_list = [(str(photo.id)) for photo in find_photo_id]
                photo_id = photo_id_list[-1]
            
                #uses photo id from previous query as well as tag ids, adds to join table
                tags_chosen = form.tags.data
                find_tag_id = models.Tags.query.filter(models.Tags.id.in_(tags_chosen)).all()
                tag_id_list = [(str(tag.id)) for tag in find_tag_id]
                for tag in tag_id_list:
                    add_tag_and_photo = models.Photo_tag(pid=photo_id, tid=tag)
                    db.session.add(add_tag_and_photo)
                db.session.commit()
            else:
                duplicate_found = True
            return render_template('add.html', form=form, filename=filename, title="Add", duplicate_found=duplicate_found)
        return render_template('add.html', form=form, title="Add")

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)