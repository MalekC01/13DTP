from flask import Flask, render_template, request, redirect, session, flash
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, update, delete
from config import Config
import random


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, session_options={"expire_on_commit": False, "autoflush": False})


#imports python files
import models
import forms
from image_exif import exif_for_image


#error messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'passoword'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images/uploads'


#Logs out after 5 mins 
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=5)


#sends error redirects to error page
@app.errorhandler(404)
def page_not_found(e):
    logged_in = check_logged_in()
    return render_template('error.html', logged_in=logged_in), 404

#home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    logged_in = check_logged_in()
    #choses random images in correct format to display on home screen
    pictures_for_slideshow = models.Photo.query.filter_by(orientation="Landscape").all()
    images_id_slides = [(str(id.id), id.url) for id in pictures_for_slideshow]
    try:
        random_index = random.sample(images_id_slides, 3)
    except:
        random_index = None
    return render_template('home.html', title="Home", random_index=random_index, logged_in=logged_in)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method=='GET':  # did the browser ask to see the page
        return render_template('login.html', form=form)
    else:
        username = form.username.data
        check_username_exists = models.Users.query.filter_by(username=username.lower()).first()
        if check_username_exists != None:
            if str(form.password.data) == str(check_username_exists.password):
                session['username'] = form.username.data
                return redirect('/')
            else:
                # wrong password
                flash("Password is incorrect try again!")  
        else:
            # username doen't exist
            flash("Username is incorrect try again!")  
        return render_template('login.html', form=form)

#<a href="/photo/{{level_2_images[0].id}}"><img src="/static/images/{{level_2_images[0].url}}"></a>
def check_logged_in():
    if 'username' in session:
        return True
    return False

#page for all ncea images
@app.route('/ncea', methods=['GET', 'POST'])
def ncea():
    logged_in = check_logged_in()
    level_2_images = models.Photo.query.filter_by(ncea=2, orientation="Portrait").all()
    level_3_images = models.Photo.query.filter_by(ncea=3, orientation="Portrait").all()
    return render_template('ncea.html', logged_in=logged_in, level_2_images=level_2_images, level_3_images=level_3_images)

#all image to do with level 2 ncea
@app.route("/level/<int:ncea>", methods=['GET', 'POST'])
def image_ncea_level(ncea):
    logged_in = check_logged_in()
    all_chosen_level_photos = models.Photo.query.filter_by(ncea=ncea).all()
    return render_template('ncea_level.html', all_chosen_level_photos=all_chosen_level_photos, logged_in=logged_in)


#gallery queriies to display images
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    logged_in = check_logged_in()
    display_all = True
    form = forms.Filter_images()
    
    #queries database for all current tags, returns so can dusplay for filtering
    all_tags = models.Tag.query.all()
    tags_for_filter_buttons = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.options.choices = tags_for_filter_buttons

    #queries for all images in database and returns with url so src can display in html
    url_of_all_images = models.Photo.query.all()
    
    #shuffles list indexes so each time page is refreshed order of images will change
    id_url = [(str(url.id), url.url, url.orientation) for url in url_of_all_images]
    random.shuffle(id_url)
    
    if request.method=='GET':  # did the browser ask to see the page
        return render_template('gallery.html', id_url=id_url, form=form, display_all=display_all, logged_in=logged_in, url_of_all_images=url_of_all_images)
    else:  # its a POST, the user clicked SUBMIT
        if form.options.data == None:
            return redirect("/gallery")
        else:
            image_url = None
            display_all = False
 
            #takes all tags selected in filter form and queries for the ids
            tags_to_search = []
            for tag_ids in form.options.data:
                chosen_tags = models.Tag.query.filter_by(id=tag_ids).all()
                for tag_ids in chosen_tags:
                    tags_to_search.append(tag_ids.id)
            
            # #uses tag ids to then find the images that contain that tag
            # photo_ids = []
            # for tag_id in tags_to_search[:len(tags_to_search)][0]:
            #     search_for_photo_id = models.Photo.query.filter_by(tid=tag_id).all()
            #     print(search_for_photo_id)
            #     #image_id = [(str(image_id.pid)) for image_id in search_for_photo_id]
            #     photo_ids.append(search_for_photo_id.id)

            photo_ids = []
            #print(tags_to_search)
            for tag in tags_to_search:
                search_tags = models.Tag.query.filter_by(id=tag).first()
                for each_tag in search_tags.photos:
                    photo_ids.append(int(each_tag.id))
                    

            #uses all image ids for tags selected then get url so can be displayed
            urls = []
            for image_id in photo_ids:
                print(image_id)
                search_for_photo_url = models.Photo.query.filter_by(id=image_id).first()
                urls.append((search_for_photo_url.id, search_for_photo_url.url))
            #randomises order to be displayed
            random.shuffle(urls)

            return render_template('gallery.html', form=form, image_url=urls, display_all=display_all, logged_in=logged_in, url_of_all_images=url_of_all_images)



@app.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    form = forms.EditPhotoInfo()
    logged_in = check_logged_in()

    photo = models.Photo.query.filter_by(id=id).first_or_404()
    exif_data = exif_for_image(photo)

    all_tags = models.Tag.query.all()
    form.tags.choices = [(tag_name.id, str(tag_name.tag_name)) for tag_name in all_tags]

    # tag_ids = []
    # for tag in photo.tags:
    #     tag_ids.append(tag.id)
    # form.tags.default = tag_ids
    # form.ncea.default = str(photo.ncea)
    # print(photo.ncea)
    # form.locations.default = str(photo.location)
    # form.orientation.default = photo.orientation
    # form.process()

    list_of_locations = models.Location.query.all()
    form.locations.choices = [(location_name.id, str(location_name.location_name)) for location_name in list_of_locations] 

    if request.method=='GET':

        return render_template('photo.html', title="Info", form=form, photo=photo, exif_data=exif_data, logged_in=logged_in)

    else:
    
        has_data = True


        if form.tags.data == [] and form.new_tag.data == "":
            flash("Tags field left empty!")
            has_data = False
        if form.orientation.data == None:
            flash("Orientation field left empty!")
            has_data = False
        if form.ncea.data == None:
            flash("Ncea field left empty!")
            has_data = False
        if form.locations.data == None and form.new_location.data == "":
            flash("Locations field left empty!")
            has_data = False



        if has_data:
            #ncea data from form
            ncea_level = form.ncea.data
            if ncea_level == "Level 2":
                ncea_level = "2"
            elif ncea_level == "Level 3":
                ncea_level = "3"
            else:
                ncea_level = "Not NCEA"


            #if new tag isnt empty add to database
            new_tag = form.new_tag.data
            found_new_tag_ids = []
            if new_tag != '':
                tags_formated = []
                print(form.tags.data)
                tags_formated = new_tag.split(", ")
            
                found_new_tag_ids = []
                for duplicate in tags_formated:
                    check_tag_duplicate = models.Tag.query.filter_by(tag_name=duplicate).all()
                    if check_tag_duplicate == []:
                        add_tag = models.Tag(tag_name=duplicate)
                        db.session.add(add_tag)
                        db.session.commit()

                        find_new_tag_id = models.Tag.query.filter_by(tag_name=duplicate).all()
                        found_new_tag_ids += find_new_tag_id
                        found_new_tag_ids = [(str(tag.id)) for tag in found_new_tag_ids]
                    else:
                        flash("Duplicate tag found please select or try again!")

            #update query
            photo = models.Photo.query.filter_by(id=id).first()

            #if no new location has been added
            if form.new_location.data != "":
                try:
                    check_location_duplicate = models.Location.query.filter_by(location_name=form.new_location.data).first_or_404()
                except:
                    add_location = models.Location(location_name=form.new_location.data)
                    db.session.add(add_location)
                    db.session.commit()

                    find_id_of_new_location = models.Location.query.filter_by(location_name=form.new_location.data).first_or_404()
                    photo.location = []
                    photo.location = int(find_id_of_new_location.id)
                    db.session.commit()
            else:
                photo.location = form.locations.data
                db.session.commit()

            photo.orientation = form.orientation.data  
            photo.ncea = ncea_level
            photo.tags = []
            db.session.merge(photo)
            db.session.commit()

            list_of_tags = form.tags.data + found_new_tag_ids

            for tag in list_of_tags:
                add_tag = models.Tag.query.filter_by(id=int(tag)).first()
                photo.tags.append(add_tag)
            db.session.merge(photo)
            db.session.commit()

        


    return redirect(str("/photo/") + str(id))
    # return render_template('photo.html', title="Info", logged_in=logged_in, info_of_image=info_of_image, data_for_image=data_for_image, tags_of_image=tags_of_image, list_of_tags=list_of_tags, format_of_image=format_of_image, form=form)

#add new images to databsae
@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    logged_in = check_logged_in()
    if not logged_in:
        return redirect('/')
    
    form = forms.Add_Photo()

    #query database for all tags
    all_tags = models.Tag.query.all()
    tags_for_form = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.tags.choices = tags_for_form

    #query database for all previous locations
    all_locations = models.Location.query.all()
    locations_for_form = [(str(location.id), location.location_name) for location in all_locations]
    form.locations.choices = locations_for_form

    if request.method=='GET':  # did the browser ask to see the page
        return render_template('add.html', logged_in=logged_in, form=form)
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
                new_location = form.new_location.data

                #if new location tag isnt empty add to database
                if new_location != '':
                    #change to if any instead of querying all
                    check_location_duplicate = models.Locations.query.filter_by(location_name=new_location).all()
                    if check_location_duplicate == []:
                        add_location = models.Locations(location_name=new_location)
                        db.session.add(add_location)
                        db.session.commit()
                    else:
                        flash("New location added is a dupliacte try again!")
                    find_location_id = models.Locations.query.filter_by(location_name=new_location).all()
                    location_id_list = [(str(location.id)) for location in find_location_id]
                    location_id = location_id_list[0]

                else:
                    location_id = form.locations.data

                #if new tag isnt empty add to database
                found_new_tag_ids = []
                new_tag = form.new_tag.data
                if new_tag != '':
                    tags_formated = []
                    tags_formated = new_tag.split(", ")
                    
                    
                    for duplicate in tags_formated:
                        check_tag_duplicate = models.Tag.query.filter_by(tag_name=duplicate).all()
                        if check_tag_duplicate == []:
                            add_tag = models.Tag(tag_name=duplicate)
                            db.session.add(add_tag)
                            db.session.commit()
                            find_new_tag_id = models.Tag.query.filter_by(tag_name=duplicate).all()
                            found_new_tag_ids += find_new_tag_id
                            found_new_tag_ids = [(str(tag.id)) for tag in found_new_tag_ids]
                        else:
                            flash("The new tag to be added is a dupliacte try again!")
                            

                #add image with all data from form and image file 
                add_photo_url = models.Photo(url=photo_url, location=location_id, ncea=ncea_level, orientation=orientation)
                db.session.add(add_photo_url)
                db.session.commit()

                #find image id within database after being commited so next query can be made
                find_photo_id = models.Photo.query.filter_by(url=photo_url).first()
            
                #uses photo id from previous query as well as tag ids, adds to join table
                tag_id_list = form.tags.data + found_new_tag_ids
                print("tags to add to image: " + str(tag_id_list))
                
                for tag in form.tags.data:
                    add_tag = models.Tag.query.filter_by(id=int(tag)).first()
                    photo.tags.append(add_tag)
                    db.session.merge(photo)
                    db.session.commit()

                #errors
                if form.tags.data == None:
                    flash("Tags section left empty fill all sections to proccede!")
                if form.locations == None:
                    flash("Locations section left empty fill all sections to proccede!")

                
            else:
                duplicate_found = True
                flash("This image is a duplicate find a new one or try again!")
            return render_template('add.html', logged_in=logged_in, form=form, filename=filename, title="Add", duplicate_found=duplicate_found)
        return render_template('add.html', logged_in=logged_in, form=form, title="Add")

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)