from flask import Blueprint, g, jsonify, request
from main_site.models import Users
from sqlalchemy import func

users = Blueprint('users', __name__)


@users.route('/add-user', methods=['GET', 'POST'])
def add_user():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    region = data.get('region')
    admin = data.get('admin')
    user = Users(username, password, region, admin)

    if not g.db.query(Users).filter(func.lower(Users.username) == func.lower(username)).first():
        g.db.add(user)
        g.db.commit()
        return jsonify(results='success', message='added')
    else:
        return jsonify(results='failure', message='user already exists')


@users.route('/edit-user', methods=['GET', 'POST'])
def edit_user():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    region = data.get('region')
    admin = data.get('admin')
    user = g.db.query(Users).filter(func.lower(Users.username) == func.lower(username)).first()
    if user:
        print region
        print admin
        user.set_password(password)
        user.region = region
        user.admin = admin
        g.db.commit()
        return jsonify(results='success', message='modified')
    else:
        return jsonify(results='failure', message='user not found')


@users.route('/get-users', methods=['GET'])
def get_users():
    items = g.db.query(Users).order_by(Users.username).all()
    returnUsers = []
    for item in items:
        returnUsers.append(item.serialize())
    return jsonify(users=returnUsers)


@users.route('/delete-user', methods=['POST'])
def delete_user():
    data = request.get_json(force=True)
    username = data.get('username')
    user = g.db.query(Users).filter(func.lower(Users.username) == func.lower(username)).first()
    if user:
        g.db.delete(user)
        g.db.commit()
        return jsonify(results='success', message='modified')
    else:
        return jsonify(results='failure', message='user not found')
