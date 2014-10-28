from flask import Flask, g, render_template, request
from flask.ext.login import LoginManager

from main_site.blueprints.titles import titles
from main_site.blueprints.users import users
from main_site.models import Users
from main_site.utils import get_db

from sqlalchemy import func


def create_app(config=None):
    app = Flask(__name__)

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_request
    def teardown(exception=None):
        g.db.close()

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
        return main()
        #return render_template('client/index.html')

    @app.route('/press')
    def press():
        return render_template('press/index.html')

    @app.route('/contact')
    def contact():
        return render_template('contact/index.html')

    @app.route('/main')
    def main():
        return render_template('main_screen/index.html')

    @app.route('/main/upload')
    def main_upload():
        return render_template('main_screen/dataupload.html')

    @app.route('/main/users')
    def main_users():
        return render_template('main_screen/users.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            data = request.get_json(force=true)
            username = data.get('username')
            password = data.get('password')
            user = db.query(Users).filter(func.lower(Users.username) == func.lower(username)).first()
            if user:
                if user.check_password(password):
                    login_user(user)
                    flash("Logged in successfully.")
                    return render_template('main_screen/index.html')

        return render_template('client/index.html')

    app.register_blueprint(titles, url_prefix='/titles')
    app.register_blueprint(users, url_prefix='/users')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        return Users.get(userid)

    return app

app = create_app()
