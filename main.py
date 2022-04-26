from flask import Flask, render_template, request, redirect, abort
import os
from sqlalchemy import insert
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

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
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    photo_url = str(filename + "/uploads")

    insert(Photo)
    values(url=photo_url)


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