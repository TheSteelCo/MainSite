from flask import Blueprint, g, jsonify
from main_site.models import GeneralList

titles = Blueprint('titles', __name__)


@titles.route('/loadtitles', methods=['GET'])
def load_titles():
    items = g.db.query(GeneralList).all()
    returnTitles = []
    for item in items:
        ser = item.serialize()
        returnTitles.append({
            'mvCompany': ser.get('company'),
            'mvTitle': ser.get('title'),
            'mvGenre': ser.get('genre'),
            'mvStatus': ser.get('status'),
            'mvDescription': ser.get('notes'),
            'mvCount': 'count a'
        })
    return jsonify(titles=returnTitles)
