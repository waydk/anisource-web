from PicImageSearch import SauceNAO
from environs import Env
import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

# SET YOUR FOLDER
UPLOAD_FOLDER = '/home/waydk/python_projects/anisource-web/anisource/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('search',
                                    filename=filename))
    return render_template("index.html")

@app.route('/search/<filename>')
def search(filename):
    env = Env()
    env.read_env()

    api_key = env.str("SAUCE_API")
    saucenao = SauceNAO(api_key=api_key)
    res = saucenao.search(f"anisource/img/{filename}")
    try:
        est_time = f"☁ Est Time: {res.origin['results'][0]['data']['est_time']}\n"
    except KeyError:
        est_time = ''

    try:
        part = f"☁ Part: {res.origin['results'][0]['data']['part']}\n"
    except KeyError:
        part = ''

    res = res.raw[0]
    author = f"☁ <h1> Author: {res.author}\n</h1>" if res.author else ''
    message = f"☁ Title: {res.title}" \
              f"☁ Similarity: {res.similarity}%" \
              f"{author}" \
              f"{est_time}" \
              f"{part}" \
              f"☁ Url: {res.url}"
    return message

if __name__ == '__main__':
    app.run(debug=True)
