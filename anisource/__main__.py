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
        est_time = res.origin['results'][0]['data']['est_time']
    except KeyError:
        est_time = None

    try:
        part = res.origin['results'][0]['data']['part']
    except KeyError:
        part = None

    res = res.raw[0]
    return render_template(
        "search_image.html",
        title=res.title,
        est_time=est_time,
        part=part,
        author=res.author,
        photo=res.thumbnail,
        similarity=res.similarity
    )


if __name__ == '__main__':
    app.run(debug=True)
