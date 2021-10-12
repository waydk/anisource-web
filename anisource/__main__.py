from PicImageSearch import SauceNAO
from environs import Env
import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import base64

# SET YOUR FOLDER
UPLOAD_FOLDER = 'anisource/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def saucenao_search(filename=None, link=None):
    env = Env()
    env.read_env()

    api_key = env.str("SAUCE_API")
    saucenao = SauceNAO(api_key=api_key)
    if filename:
        res = saucenao.search(f"anisource/img/{filename}")
        os.remove(f"anisource/img/{filename}")
    else:
        res = saucenao.search(link)
    try:
        est_time = res.origin['results'][0]['data']['est_time']
    except (KeyError, AttributeError):
        est_time = None

    try:
        part = res.origin['results'][0]['data']['part']
    except (KeyError, AttributeError):
        part = None

    try:
        res = res.raw[0]
    except AttributeError:
        return render_template("error.html", error="Not found")
    return render_template(
        "search_image.html",
        title=res.title,
        est_time=est_time,
        part=part,
        author=res.author,
        photo=res.thumbnail,
        similarity=res.similarity,
        url=res.url
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file, text = None, None
        if 'text' in request.form:
            text = request.form['text']
        if 'fileUpload' in request.files:
            file = request.files['fileUpload']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('search_by_image',
                                    filename=filename))
        if text:
            bytes_text = base64.b64encode(text.encode("UTF-8"))
            decoded_text = bytes_text.decode("utf-8")
            return redirect(url_for('search_by_link', link=decoded_text))
    return render_template("index.html")

@app.route('/search_image/<filename>')
def search_by_image(filename):
    return saucenao_search(filename=filename)

@app.route('/search_link/<link>')
def search_by_link(link):
    bytes_text = base64.b64decode(link.encode("utf-8"))
    link = bytes_text.decode('utf-8')
    return saucenao_search(link=link)

@app.route('/about')
def show_about():
    return render_template("about.html")

@app.route('/examples')
def show_examples():
    return render_template("examples.html")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html', error=e), 404


if __name__ == '__main__':
    app.run()
