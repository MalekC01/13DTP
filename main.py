from flask import Flask, render_template, request, redirect, abort
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Config)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'


import models

#home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title="Home")

#returns on all pages
# @app.contect_processor()
# def contect_processor():


@app.route('/add')
def add():
    return render_template('add.html', title="Add")


@app.route('/add', methods=['POST'])
def uploaded_files():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    print(filename)
    photo_url = str( "uploads/" + filename)

    check_duplicate = None
    check_duplicate = models.Photo.query.filter_by(url=photo_url).first() 

    if check_duplicate == None:
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        location = request.form.get('location') 
    
        ncea_level = 0

        if request.form.get('ncea_level') == 2:
            ncea_level = "2"
        elif request.form.get('ncea_level') == 3:
            ncea_level = "3"
        else:
            ncea_level = "Not NCEA"
            
            

        add_photo_url = models.Photo(url=photo_url, location=location, ncea=ncea_level)
        db.session.add(add_photo_url)
        db.session.commit()

        photo_id = models.Photo.query.filter_by(url=photo_url).first()

        print(type(photo_id))

        length = len(str(photo_id))
        
        found_id = str(photo_id)[7:length-1]
        print(found_id)

    else:
        print("Photo already in database try another one")
    

    

    

    #session.query(User.name).filter(User.id == 1).first()

    if request.form.get('landscape'):
        # do query to add tag to photo id

        
        print(photo_url)



        return redirect('/add')




    if request.form.get('astro'):
    # match with bears (terrifying)
        return redirect('/add')

    return render_template('add.html', title="Add")

#runs port on local site
if __name__ == '__main__':
    app.run(port=8080, debug=True)