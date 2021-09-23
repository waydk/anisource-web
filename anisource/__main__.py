from flask import Flask, render_template
from PicImageSearch import SauceNAO
from environs import Env

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    env = Env()
    env.read_env()

    api_key = env.str("SAUCE_API")
    saucenao = SauceNAO(api_key=api_key)
    res = saucenao.search('https://trace.moe/img/tinted-good.jpg')
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
