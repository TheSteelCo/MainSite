import codecs
import csv
import StringIO

from flask import Blueprint, g, jsonify, request
from main_site.models import GeneralList

titles = Blueprint('titles', __name__)

ALLOWED_EXTENSIONS = set(['tab'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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


@titles.route('/import-general', methods=['GET', 'POST'])
def import_general_list():
    file = request.files['file']
    if file and allowed_file(file.filename):
        output = StringIO.StringIO(file.read())
        firstline = True
        for item in g.db.query(GeneralList).all():
            g.db.delete(item)
        for line in output.getvalue().splitlines():
            if firstline:
                firstline = False
            else:
                tabs = line.split('\t')
                item = GeneralList(
                    code=tabs[0],
                    title=tabs[1],
                    genre=tabs[2],
                    company=tabs[3],
                    status=tabs[4],
                    notes=tabs[5]
                )
                g.db.add(item)

        g.db.commit()

