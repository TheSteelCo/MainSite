from flask import Flask, g, render_template, request
from flask.ext.login import current_user, login_required, login_user, logout_user, LoginManager, flash
from flask.ext.wtf import Form
from wtforms.fields import PasswordField, TextField
from wtforms.validators import Required


from main_site.blueprints.titles import titles
from main_site.blueprints.users import users
from main_site.models import Users
from main_site.utils import get_db

from sqlalchemy import func

class LoginForm(Form):
    username = TextField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = get_db().query(Users).filter(func.lower(Users.username) == func.lower(self.username.data)).first()
        if user is None:
            flash('Unknown username')
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True

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

    @app.route('/press')
    def press():
        return render_template('press/index.html')

    @app.route('/contact')
    def contact():
        return render_template('contact/index.html')

    @app.route('/main')
    @login_required
    def main():
        return render_template('main_screen/index.html', list='general')

    @app.route('/main/hotlist')
    @login_required
    def main_hotlist():
        return render_template('main_screen/index.html', list='hotlist')

    @app.route('/main/upload')
    @login_required
    def main_upload():
        if current_user.admin:
            return render_template('main_screen/dataupload.html', list='admin')
        else:
            return render_template('main_screen/index.html', list='general')

    @app.route('/main/users')
    @login_required
    def main_users():
        if current_user.admin:
            return render_template('main_screen/users.html', list='admin')
        else:
            return render_template('main_screen/index.html', list='general')

    @app.route('/client', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated():
            return render_template('main_screen/index.html', list='general')
        form = LoginForm()
        if form.validate_on_submit():
            login_user(form.user)
            flash("Logged in successfully.")
            return render_template('main_screen/index.html', list='general')

        return render_template('client/index.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return render_template('index.html')

    app.register_blueprint(titles, url_prefix='/titles')
    app.register_blueprint(users, url_prefix='/users')

    app.secret_key = "vizar"

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "client"

    @login_manager.user_loader
    def load_user(userid):
        return get_db().query(Users).filter(Users.id == userid).first()

    return app

app = create_app()
