from flask import Flask, render_template, request, redirect, abort
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

#home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title="Home")

#returns on all pages
# @app.contect_processor()
# def contect_processor():


@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    form = Add_Photo()
    if request.method=='GET':  # did the browser ask to see the page
        return render_template('add.html', form=form)
    else:  # its a POST, ie: the user clicked SUBMIT
        if form.validate_on_submit():

            #Take ncea input from form and get ready to be inputted into database
            ncea_level = form.ncea.data
            if ncea_level == "Level 1":
                ncea_level = "1"
            elif ncea_level == "Level 2":
                ncea_level = "2"
            else:
                ncea_level = "Not NCEA"

            uploaded_file = request.files['file']
            filename = uploaded_file.filename
            
            photo_url = str( "uploads/" + filename)

            print("Filename: " +  str(photo_url))
            print("Ncea Level: " + str(ncea_level))


            # add_photo_url = models.Photo(url=photo_url, location=location, ncea=ncea_level)
            # db.session.add(add_photo_url)
            # db.session.commit()
    return render_template('add.html', title="Add", form=form)


    # #check image hasnt already been added to database
    # check_duplicate = None
    # check_duplicate = models.Photo.query.filter_by(url=photo_url).first() 


    # #if new image add to uploads file
    # if check_duplicate == None:
    #     uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    #     location = request.form.get('location') 
    
    #     #add ncea data
    #     ncea_level = 0

    #     if request.form.get('ncea_level') == 2:
    #         ncea_level = "2"
    #     elif request.form.get('ncea_level') == 3:
    #         ncea_level = "3"
    #     else:
    #         ncea_level = "Not NCEA"
            
    #     #add deatials about image to Photo table
    #     add_photo_url = models.Photo(url=photo_url, location=location, ncea=ncea_level)
    #     db.session.add(add_photo_url)
    #     db.session.commit()

    #     photo_id = models.Photo.query.filter_by(url=photo_url).first()
    #     photo_length = len(str(photo_id))
    #     found_photo_id = str(photo_id)[7:photo_length-1]

    #     #check new tag feild add if not all ready a tag
    #     new_tag = None
    #     new_tag = request.form.get('new_tag')
    #     if new_tag != None:
    #         tag_check = models.Tags.query.filter_by(tag_name=new_tag).first()
    #         if tag_check == None:
    #             add_new_tag = models.Tags(tag_name=new_tag)
    #             db.session.add(add_new_tag)
    #             db.session.commit()
    #         else:
    #             print("Error tag not added to database")
    #             app.config['error_tag_not_added'] = True
    #             error_found = True
    #     else:
    #             print("Error tag already exists")
    #             error_tag_found = True
    #             error_found = True


    #     if request.form.get('landscape'):
    #     # do query to add tag to photo id
    #         landscape_id = models.Tags.query.filter_by(tag_name="landscape").first()
    #         landscape_length = len(str(landscape_id))
    #         found_landscape_id = str(landscape_id)[6:landscape_length-1]

    #     add_tags = models.Photo_tag(pid=found_photo_id, tid=found_landscape_id)
    #     db.session.add(add_tags)
    #     db.session.commit() 
        
        




        # add_photo_tag = models.Photo_tag(pid=found_id, tid=)
        # db.session.add(add_photo_tag)



    # else:
    #     print("Photo already in database try another one")
    #     error_duplicate = True
    
    #session.query(User.name).filter(User.id == 1).first()

    # return render_template('add.html', title="Add", error_duplicate=error_duplicate, error_tag_not_added=error_tag_not_added, error_tag_found=error_tag_found)
    return render_template('add.html', form=form, title="Add", error_duplicate=error_duplicate, error_tag_not_added=error_tag_not_added, error_tag_found=error_tag_found)

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)