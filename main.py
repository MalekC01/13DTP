from image_exif import exif_for_image
import forms
import models
from flask import Flask, render_template, request, redirect, session, flash, Response
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, update, delete
from config import Config
import random
import hashlib
import re
import copy


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(
    app,
    session_options={
        "expire_on_commit": False,
        "autoflush": False})


# error messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'password'
app.config['UPLOAD_EXTENSIONS'] = [
    '.gif',
    '.jpg',
    '.JPG',
    '.PNG',
    '.png',
    '.xmp',
    '.CR2',
    '.jpeg']
app.config['UPLOAD_PATH'] = 'static/images/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
admin_key = "Secret Code"


# Logs out after 5 mins
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=5)


def check_logged_in():
    if 'username' in session:
        return True
    return False

# sends error redirects to error page
@app.errorhandler(404)
def page_not_found(e):
    logged_in = check_logged_in()
    return render_template('error.html', logged_in=logged_in), 404


# 500 error page, main use for potential overflow error in photos page
@app.route('/500', methods=['GET', 'POST'])
def error_500():
    return render_template('500_page.html')


# home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    logged_in = check_logged_in()
    # choses random images in correct format to display on home screen
    pictures_for_slideshow = models.Photo.query.filter_by(
        orientation="Landscape").all()
    images_id_slides = [(str(id.id), id.url) for id in pictures_for_slideshow]
    try:
        random_index = random.sample(images_id_slides, 3)
    except BaseException:
        random_index = None
    return render_template(
        'home.html',
        title="Home",
        random_index=random_index,
        logged_in=logged_in)


# end session log user out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    logged_in = check_logged_in()
    if request.method == 'GET':  # did the browser ask to see the page
        return render_template('login.html', form=form, logged_in=logged_in)
    else:
        username = form.username.data
        check_username_exists = models.Users.query.filter_by(
            username=username.lower()).first()
        if check_username_exists is not None:
            # hashes plain string user input, then adds to database
            pre_hashed = bytes(form.password.data, 'utf-8')
            hashed_password = int.from_bytes(
                hashlib.sha256(pre_hashed).digest()[:8], 'little')

            if hashed_password == check_username_exists.password:
                session['username'] = form.username.data
                return redirect('/')

            else:
                # wrong password
                flash("Password is incorrect try again!")
        else:
            # username doen't exist
            flash("Username is incorrect try again!")
        return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    logged_in = check_logged_in()
    if request.method == 'GET':  # did the browser ask to see the page
        return render_template('register.html', form=form)
    else:
        username = form.username.data
        # check username doesnt exist
        check_username_exists = models.Users.query.filter_by(
            username=username.lower()).first()
        if check_username_exists is not None:
            flash("This username is already taken please try again!")
        else:
            # check passwords match
            if form.password.data == form.password_check.data:
                # check no anyone can sign up must know admin code
                if form.key.data == admin_key:
                    # makes sure length of password string doesnt exceed 12
                    # characters
                    length_check = len(form.password.data)

                    if length_check < 12 and length_check > 0:

                        # list of special characters to compare against
                        string_check = re.compile('[@_!# $%^&*()<>?/\\|}{~:]')
                        # does not include special characters
                        if (string_check.search(form.password.data) is None):

                            pre_hashed = bytes(form.password.data, 'utf-8')
                            hashed_password = int.from_bytes(
                                hashlib.sha256(pre_hashed).digest()[:8], 'little')

                            register_user = models.Users(
                                username=form.username.data, password=hashed_password)
                            db.session.add(register_user)
                            db.session.commit()

                            session['username'] = form.username.data
                            return redirect('/')

                        else:
                            flash(
                                "Passwords may not include special characters try again!")

                    else:
                        flash("Password longer than 12 characters!")

                else:
                    flash("Admin code was incorrect!")

            else:
                flash("The passwords didnt match. Try again!")

        return render_template('register.html', form=form)


# page for all ncea images
@app.route('/ncea', methods=['GET', 'POST'])
def ncea():
    logged_in = check_logged_in()
    level_2_images = models.Photo.query.filter_by(
        ncea=2, orientation="Portrait").all()
    level_3_images = models.Photo.query.filter_by(
        ncea=3, orientation="Portrait").all()

    # takes a random 3 images from each ncea level and displays on the slides
    level_2_slides = [(str(id.id), id.url) for id in level_2_images]
    try:
        random_index_level_2 = random.sample(level_2_slides, 3)

    except BaseException:
        random_index_level_2 = None

    level_3_slides = [(str(id.id), id.url) for id in level_3_images]
    try:
        random_index_level_3 = random.sample(level_3_slides, 3)
        print(random_index_level_3)
    except BaseException:
        random_index_level_3 = None

    return render_template(
        'ncea.html',
        logged_in=logged_in,
        level_2_images=level_2_images,
        level_3_images=level_3_images,
        level_2_slide=random_index_level_2,
        level_3_slide=random_index_level_3)


# displays all ncea images dependent on what level is chosen
@app.route("/level/<int:ncea>", methods=['GET', 'POST'])
def image_ncea_level(ncea):
    logged_in = check_logged_in()
    all_chosen_level_photos = models.Photo.query.filter_by(ncea=ncea).all()
    return render_template(
        'ncea_level.html',
        all_chosen_level_photos=all_chosen_level_photos,
        logged_in=logged_in)


# gallery queriies to display images
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    logged_in = check_logged_in()
    display_all = True
    form = forms.Filter_images()

    # queries database for all current tags, returns so can dusplay for
    # filtering
    all_tags = models.Tag.query.all()
    tags_for_filter_buttons = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.options.choices = tags_for_filter_buttons

    # queries for all images in database and returns with url so src can
    # display in html
    url_of_all_images = models.Photo.query.all()

    # shuffles list indexes so each time page is refreshed order of images
    # will change
    id_url = [(str(url.id), url.url, url.orientation)
              for url in url_of_all_images]

    landscape_gallery = models.Photo.query.filter_by(
        orientation="Landscape").all()
    portrait_gallery = models.Photo.query.filter_by(
        orientation="Portrait").all()

    if request.method == 'GET':  # did the browser ask to see the page
        return render_template(
            'gallery.html',
            id_url=id_url,
            form=form,
            display_all=display_all,
            logged_in=logged_in,
            url_of_all_images=url_of_all_images)
    else:  # its a POST, the user clicked SUBMIT
        if form.options.data is None:
            list_of_tags = []
            return redirect("/gallery")
        else:
            image_url = None
            display_all = False

            list_of_tags = []

            # takes all tags selected in filter form and queries for the ids
            tags_to_search = []
            for tag_ids in form.options.data:
                chosen_tags = models.Tag.query.filter_by(id=tag_ids).all()

                for tag_ids in chosen_tags:
                    tags_to_search.append(tag_ids.id)
                    list_of_tags.append(tag_ids.tag_name)

            print(list_of_tags)
            photo_ids = []
            for tag in tags_to_search:
                search_tags = models.Tag.query.filter_by(id=tag).first()
                for each_tag in search_tags.photos:
                    photo_ids.append(int(each_tag.id))

            # uses all image ids for tags selected then get url so can be
            # displayed
            urls = []
            for image_id in photo_ids:
                search_for_photo_url = models.Photo.query.filter_by(
                    id=image_id).first()
                urls.append(
                    (search_for_photo_url.id,
                     search_for_photo_url.url))
            # limits any duplicates so double up images are not displayed
            urls = tuple(set(urls))
            return render_template(
                'gallery.html',
                form=form,
                image_url=urls,
                display_all=display_all,
                logged_in=logged_in,
                url_of_all_images=url_of_all_images,
                list_of_tags=list_of_tags)


@app.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    
    form = forms.EditPhotoInfo()
    logged_in = check_logged_in()

    # prevents overflow error by limiting id size to one that page can handle
    if id > 2**63 - 1:
        return redirect("/500")

    photo = models.Photo.query.filter_by(id=id).first_or_404()
    # gets data from exif function
    exif_data = exif_for_image(photo)

    all_tags = models.Tag.query.all()
    form.tags.choices = [(tag_name.id, str(tag_name.tag_name))
                         for tag_name in all_tags]

    list_of_locations = models.Location.query.all()
    form.locations.choices = [(location_name.id, str(
        location_name.location_name)) for location_name in list_of_locations]


    if request.method == 'GET':

        return render_template(
            'photo.html',
            title="Info",
            form=form,
            photo=photo,
            exif_data=exif_data,
            logged_in=logged_in,)

    else:
        has_data = True

        # rasies error so user knows reason for form not being submitted
        if form.tags.data == [] and form.new_tag.data == "":
            flash("Tags field left empty!")
            has_data = False
        if form.orientation.data is None:
            flash("Orientation field left empty!")
            has_data = False
        if form.ncea.data is None:
            flash("Ncea field left empty!")
            has_data = False
        if form.locations.data is None and form.new_location.data == "":
            flash("Locations field left empty!")
            has_data = False

        if has_data:
            # ncea data from form
            ncea_level = form.ncea.data

            # if new tag isnt empty add to database
            new_tag = form.new_tag.data
            found_new_tag_ids = []
            if new_tag != '':
                tags_formated = []
                tags_formated = new_tag.split(", ")

                # makes sure image hasnt already been added
                found_new_tag_ids = []
                for duplicate in tags_formated:
                    check_tag_duplicate = models.Tag.query.filter_by(
                        tag_name=duplicate).all()
                    if check_tag_duplicate == []:
                        add_tag = models.Tag(tag_name=duplicate)
                        db.session.add(add_tag)
                        db.session.commit()

                        find_new_tag_id = models.Tag.query.filter_by(
                            tag_name=duplicate).all()
                        found_new_tag_ids += find_new_tag_id
                        found_new_tag_ids = [(str(tag.id))
                                             for tag in found_new_tag_ids]
                    else:
                        flash("Duplicate tag found please select or try again!")

            # update query
            photo = models.Photo.query.filter_by(id=id).first()

            # if new location has been added
            if form.new_location.data != "":
                try:
                    # check not trying to add exisiting location
                    check_location_duplicate = models.Location.query.filter_by(
                        location_name=form.new_location.data).first_or_404()
                except BaseException:
                    add_location = models.Location(
                        location_name=form.new_location.data)
                    db.session.add(add_location)
                    db.session.commit()

                    find_id_of_new_location = models.Location.query.filter_by(
                        location_name=form.new_location.data).first_or_404()
                    photo.location = []
                    photo.location = int(find_id_of_new_location.id)
                    db.session.commit()
            else:
                photo.location = form.locations.data
                db.session.commit()

            # commits image to photo table with all requried data
            photo.orientation = form.orientation.data
            photo.ncea = ncea_level
            photo.tags = []
            db.session.merge(photo)
            db.session.commit()

            list_of_tags = form.tags.data + found_new_tag_ids

            # adds tags and image to join table
            for tag in list_of_tags:
                add_tag = models.Tag.query.filter_by(id=int(tag)).first()
                photo.tags.append(add_tag)
            db.session.merge(photo)
            db.session.commit()
            flash("Image data sucessfulyl updated!")

    return redirect(str("/photo/") + str(id))


@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    logged_in = check_logged_in()
    if not logged_in:
        return redirect('/')

    form = forms.Add_Photo()

    # query database for all tags
    all_tags = models.Tag.query.all()
    tags_for_form = [(str(tag.id), tag.tag_name) for tag in all_tags]
    form.tags.choices = tags_for_form

    # query database for all previous locations
    all_locations = models.Location.query.all()
    locations_for_form = [(str(location.id), location.location_name)
                          for location in all_locations]
    form.locations.choices = locations_for_form

    if request.method == 'GET':  # did the browser ask to see the page
        return render_template('add.html', logged_in=logged_in, form=form)
    else:  # its a POST, ie: the user clicked SUBMIT
        # uplaoding image to local files
        if form.validate_on_submit():
            uploaded_file = request.files['display-image']

            filename = uploaded_file.filename

            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                flash("Wrong extention!")
                return redirect("/add")

            uploaded_file.save(
                os.path.join(
                    app.config['UPLOAD_PATH'],
                    filename))
            photo_url = str("uploads/" + filename)

            # check image hasnt already been uploaded

            check_duplicate_photo = models.Photo.query.filter_by(
                url=photo_url).first()

            # if no duplicate image has been found add to database
            if check_duplicate_photo is None:
                # Take ncea input from form and get ready to be inputted into
                # database
                orientation = form.orientation.data

                # ncea data from form
                ncea_level = form.ncea.data

                # location data from form
                new_location = form.new_location.data
                location = form.locations.data

                # if new location tag isnt empty add to database
                if new_location != '':
                    # change to if any instead of querying all
                    check_location_duplicate = models.Location.query.filter_by(
                        location_name=new_location).all()
                    if check_location_duplicate == []:
                        add_location = models.Location(
                            location_name=new_location)
                        db.session.add(add_location)
                        db.session.commit()
                    else:
                        flash("New location added is a dupliacte try again!")
                    find_location_id = models.Location.query.filter_by(
                        location_name=new_location).all()
                    location_id_list = [(str(location.id))
                                        for location in find_location_id]
                    location_id = location_id_list[0]

                else:
                    location_id = form.locations.data

                # if new tag isnt empty add to database
                found_new_tag_ids = []
                new_tag = form.new_tag.data
                if new_tag != '':
                    tags_formated = []
                    tags_formated = new_tag.split(", ")

                    for duplicate in tags_formated:
                        check_tag_duplicate = models.Tag.query.filter_by(
                            tag_name=duplicate).all()
                        if check_tag_duplicate == []:
                            add_tag = models.Tag(tag_name=duplicate)
                            db.session.add(add_tag)
                            db.session.commit()
                            find_new_tag_id = models.Tag.query.filter_by(
                                tag_name=duplicate).all()
                            found_new_tag_ids += find_new_tag_id
                            found_new_tag_ids = [(str(tag.id))
                                                 for tag in found_new_tag_ids]
                        else:
                            flash(
                                "The new tag to be added is a dupliacte try again!")

                # add image with all data from form and image file
                add_photo_url = models.Photo(
                    url=photo_url,
                    location=location_id,
                    ncea=ncea_level,
                    orientation=orientation)
                db.session.add(add_photo_url)
                db.session.commit()

                # find image id within database after being commited so next
                # query can be made
                find_photo_id = models.Photo.query.filter_by(
                    url=photo_url).first()

                # uses photo id from previous query as well as tag ids, adds to
                # join table
                tag_id_list = form.tags.data + found_new_tag_ids

                photo = models.Photo.query.filter_by(url=photo_url).first()
                for tag in form.tags.data:
                    add_tag = models.Tag.query.filter_by(id=int(tag)).first()
                    photo.tags.append(add_tag)
                    db.session.merge(photo)
                    db.session.commit()
                flash("Photo uploaded sucessfully!")

                # errors
                if form.tags.data is None:
                    flash("Tags section left empty fill all sections to proccede!")
                if form.locations is None:
                    flash("Locations section left empty fill all sections to proccede!")

            else:
                duplicate_found = True
                flash("This image is a duplicate find a new one or try again!")
            return render_template(
                'add.html',
                logged_in=logged_in,
                form=form,
                filename=filename,
                title="Add")
        return render_template(
            'add.html',
            logged_in=logged_in,
            form=form,
            title="Add")


# runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)
