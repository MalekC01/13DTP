
from flask import Flask, render_template, request, redirect, abort, \
    send_from_directory
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Config)

import models
import forms



#error messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images/uploads'
app.config['PATH'] = 'static/images/uploads/'

# {% for picture in files %}
#     <img src="{{ url_for(path, filename=picture) }}">
# {% endfor %} 



#home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title="Home")

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    #all_photos = models.Photo.query.filter_by(url=url).all()
    list_of_files = os.listdir(app.config['UPLOAD_PATH'])
 
    files = list_of_files[1:]
    print("files: " + str(files))
    path = app.config['PATH']
    for pictures in files:
        print("pictures: " + str(pictures))
        print(path + pictures)

    return render_template('gallery.html', files=files, path=path)

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
        print(form.tags.data)
        if form.validate_on_submit():
            uploaded_file = request.files['display-image']
            filename = uploaded_file.filename
            print(filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            photo_url = str( "uploads/" + filename)



            check_duplicate_photo = models.Photo.query.filter_by(url=photo_url).all()
            print(check_duplicate_photo)
            if check_duplicate_photo == []:
                #Take ncea input from form and get ready to be inputted into database
                ncea_level = form.ncea.data
                if ncea_level == "Level 1":
                    ncea_level = "1"
                elif ncea_level == "Level 2":
                    ncea_level = "2"
                else:
                    ncea_level = "Not NCEA"
                print(ncea_level)

                locations_chosen = form.locations.data
                print("locations chosen: " + str(locations_chosen))

            
                new_location = form.new_location.data
                print(new_location)
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


                add_photo_url = models.Photo(url=photo_url, location=location_id, ncea=ncea_level)
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


            return render_template('add.html', form=form, filename=filename, title="Add")

        return render_template('add.html', form=form, title="Add")

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)