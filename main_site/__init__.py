from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about/index.html')


@app.route('/about/villalobos')
def aboutVillalobos():
    return render_template('about/villalobos.html')


@app.route('/client')
def client():
    return render_template('client/index.html')


@app.route('/press')
def press():
    return render_template('press/index.html')


@app.route('/contact')
def contact():
	return render_template('contact/index.html')
