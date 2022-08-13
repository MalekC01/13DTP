from flask import Flask, render_template, request, redirect, session
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, update, delete
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
WTF_CSRF_SECRET_KEY = 'passoword'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images/uploads'


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
    random_index = random.sample(images_id_slides, 3)
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
        check_username_exists = models.Users.query.filter_by(username=form.username.data).first()
        if check_username_exists != None:
            if form.password.data == check_username_exists.password:
                session['username'] = form.username.data
                return redirect('/')
            else:
                # wrong passwork
                pass
        else:
            # username doen't exist
            pass
        
        return render_template('login.html', form=form)


def check_logged_in():
    if 'username' in session:
        return True
    return False

#page for all ncea images
@app.route('/ncea', methods=['GET', 'POST'])
def ncea():
    logged_in = check_logged_in()
    return render_template('ncea.html', logged_in=logged_in)

#all image to do with level 2 ncea
@app.route('/level_2', methods=['GET', 'POST'])
def level_2():
    logged_in = check_logged_in()
    all_level_2_images = models.Photo.query.filter_by(ncea=2).all()
    return render_template('level_2.html', all_level_2_images=all_level_2_images, logged_in=logged_in)

#all images to do with level 3 ncea
@app.route('/level_3', methods=['GET', 'POST'])
def level_3():
    logged_in = check_logged_in()
    all_level_3_images = models.Photo.query.filter_by(ncea=3).all()
    return render_template('level_3.html', all_level_3_images=all_level_3_images, logged_in=logged_in)

#gallery queriies to display images
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    logged_in = check_logged_in()
    display_all = True
    form = forms.Filter_images()
    
    #queries database for all current tags, returns so can dusplay for filtering
    all_tags = models.Tag.query.all()
    tags_for_filter = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.options.choices = tags_for_filter

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
                images_that_fit_filter = [(str(tag.id)) for tag in chosen_tags]
                tags_to_search.append(images_that_fit_filter)
            
            #uses tag ids to then find the images that contain that tag
            photo_ids = []
            for tag_id in tags_to_search[:len(tags_to_search)][0]:
                search_for_photo_id = models.Photo_tag.query.filter_by(tid=tag_id).all()
                #image_id = [(str(image_id.pid)) for image_id in search_for_photo_id]
                photo_ids.append(search_for_photo_id.id)
            
    
            #uses all image ids for tags selected then get url so can be displayed
            urls = []
            for data in photo_ids:
                search_for_photo_url = models.Photo.query.filter_by(id=data).all()
                urls.append(image_url.id, image_url.url)
            #randomises order to be displayed
            random.shuffle(urls)

            return render_template('gallery.html', form=form, image_url=urls, display_all=display_all, logged_in=logged_in, url_of_all_images=url_of_all_images)



@app.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    form = forms.EditPhotoInfo()
    logged_in = check_logged_in()

    #queries image selected to retireve
    image_data = models.Photo.query.filter_by(id=id).first()
    data_for_image = exif_for_image(info_of_image)

    #used so can change depedniding orrientation of image
    if info_of_image[0][2] == "Portrait":
        format_of_image = "Portrait"
    else:
        format_of_image = "Landscape"

    #queries database for all tags linked with selected
    photo = models.Photo.query.filter_by(id=id).first_or_404()
    tag = models.Tag.query.filter_by(id=7).first_or_404()
    photo.tags.append(tag)
    db.session.commit()
    print(photo.tags, photo, id)
    for tag in photo.tags:
        print(tag.tag_name)

    list_of_tags = []
    for all_tags in tags_of_image:
        tags_id_image = models.Tag.query.filter_by(id=all_tags).all()
        tags_name = [(tags_name.tag_name) for tags_name in tags_id_image]
        list_of_tags.append(tags_name)
    
    all_tags = models.Tag.query.all()
    tags_for_form = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.tags.choices = tags_for_form

    all_locations = models.Locations.query.all()
    locations_for_form = [(str(location.id), location.location_name) for location in all_locations]
    form.locations.choices = locations_for_form
    if request.method=='GET':
        return render_template('photo.html', title="Info", logged_in=logged_in, info_of_image=info_of_image, data_for_image=data_for_image, tags_of_image=tags_of_image, list_of_tags=list_of_tags, format_of_image=format_of_image, form=form)

    else:
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

        #if new location tag isnt empty add to database
        if form.new_location.data != '':
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

        #add or remove tags 



        #if new tag isnt empty add to database
        new_tag = form.new_tag.data
        if new_tag != '':
            tags_formated = []
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
                    

        #add image with all data from form and image file 

        #update query
        info = models.Photo.query.filter_by(id=id).first()
        info.orientation = form.orientation.data  
        info.ncea = ncea_level
        info.location = form.locations.data
        db.session.merge(info)
        db.session.commit()


        # new_tags = [id[0] for id in form.tags.data]
        # print("New tags: " + str(new_tags))
        # remove_all_tags = models.Photo_tag.query.filter_by(pid=id).all()
        # db.session.delete(remove_all_tags)
        # db.session.commit()

        remove_tags = db.Photo.query.filter_by(id=id).first()
        db.session.delete(remove_tags.tags)
        db.session.commit()

    return redirect(str("/photo/" + id))
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
    all_locations = models.Locations.query.all()
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
                    tags_formated = []
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
                find_tag_id = []
                for tag in tags_chosen:
                    find_tag_id += models.Tag.query.filter_by(tag_name=tags_chosen).all()
                tag_id_list = [(str(tag.id)) for tag in find_tag_id]
                
                tag_id_list = tag_id_list + found_new_tag_ids
                
                for tag in tag_id_list:
                    add_tag_and_photo = models.Photo_tag(pid=photo_id, tid=tag)
                    db.session.add(add_tag_and_photo)
                    db.session.commit()
            else:
                duplicate_found = True
            return render_template('add.html', logged_in=logged_in, form=form, filename=filename, title="Add", duplicate_found=duplicate_found)
        return render_template('add.html', logged_in=logged_in, form=form, title="Add")

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)