import codecs
import csv
import MySQLdb
import StringIO

from flask import Blueprint, g, jsonify, request
from main_site.models import GeneralList, GeneralListRegions
from sqlalchemy import func

titles = Blueprint('titles', __name__)

ALLOWED_EXTENSIONS = set(['tab'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@titles.route('/loadtitles', methods=['GET'])
def load_titles():
    data = request.args
    page = data.get('currentPage')
    searchTerm = data.get('searchTerm')
    selectedSearch = data.get('selectedSearch').lower()
    orderby = data.get('orderby').lower()
    title_order = ', title' if orderby != 'title' else ''
    desc = ' desc' if data.get('ascending') == 'd' else ''
    orderby = orderby + title_order + desc
    if searchTerm == '':
        items = g.db.query(GeneralList, GeneralListRegions.notes)\
                    .join(GeneralList.regions)\
                    .filter(GeneralListRegions.region == 'usa', GeneralListRegions.avail == 'a')\
                    .order_by(orderby)\
                    .slice((int(page)-1) * 20, int(page) * 20)\
                    .all()
        total_results = g.db.query(func.count(GeneralList.code))\
                    .join(GeneralList.regions)\
                    .filter(GeneralListRegions.region == 'usa', GeneralListRegions.avail == 'a')\
                    .scalar()
    else:
        items = g.db.query(GeneralList, GeneralListRegions.notes)\
                    .filter(getattr(GeneralList, selectedSearch).like("%" + searchTerm + "%"))\
                    .join(GeneralList.regions)\
                    .filter(GeneralListRegions.region == 'usa', GeneralListRegions.avail == 'a')\
                    .order_by(orderby)\
                    .slice((int(page)-1) * 20, int(page) * 20)\
                    .all()
        total_results = g.db.query(func.count(GeneralList.code))\
                    .filter(getattr(GeneralList, selectedSearch).like("%" + searchTerm + "%"))\
                    .join(GeneralList.regions)\
                    .filter(GeneralListRegions.region == 'usa', GeneralListRegions.avail == 'a')\
                    .scalar()
    returnTitles = []
    for item in items:
        ser = item[0].serialize()
        returnTitles.append({
            'mvCompany': ser.get('company'),
            'mvTitle': ser.get('title'),
            'mvGenre': ser.get('genre'),
            'mvStatus': ser.get('status'),
            'mvDescription': ser.get('notes'),
            'mvCount': item[1]
        })
    return jsonify(dict(titles=returnTitles, results=total_results))


@titles.route('/import-general', methods=['GET', 'POST'])
def import_general_list():
    file = request.files['file']
    if file and allowed_file(file.filename):
        output = StringIO.StringIO(file.read())
        firstline = True
        _create_temp_general_table()
        insert_code = ""
        insert_region_code = ""
        regions = []
        print 'building insert table'
        for line in output.getvalue().splitlines():
            if firstline:
                firstline = False
                tabs = line.split('\t')
                for i in xrange(6, len(tabs), 2):
                    regions.append(unicode(tabs[i], errors='replace').encode('ascii', 'replace'))
                print regions
            else:
                if insert_code == "":
                    insert_code = "INSERT INTO general_list_temp(code, title, genre, company, status, notes) VALUES "
                    insert_region_code = "INSERT INTO general_list_regions_temp(code, region, avail, notes) VALUES "

                tabs = line.split('\t')
                insert_code = insert_code + "('%s', '%s', '%s', '%s', '%s', '%s'), """ % (
                        MySQLdb.escape_string(unicode(tabs[0], errors='replace').encode('ascii', 'replace')),
                        MySQLdb.escape_string(unicode(tabs[1], errors='replace').encode('ascii', 'replace')),
                        MySQLdb.escape_string(unicode(tabs[2], errors='replace').encode('ascii', 'replace')),
                        MySQLdb.escape_string(unicode(tabs[3], errors='replace').encode('ascii', 'replace')),
                        MySQLdb.escape_string(unicode(tabs[4], errors='replace').encode('ascii', 'replace')),
                        MySQLdb.escape_string(unicode(tabs[5], errors='replace').encode('ascii', 'replace')),
                    )
                for i in xrange(6, len(tabs), 2):
                    insert_region_code = insert_region_code + "('%s', '%s', '%s', '%s'), " % (
                            MySQLdb.escape_string(unicode(tabs[0], errors='replace').encode('ascii', 'replace')),
                            MySQLdb.escape_string(regions[(i-6)/2]),
                            MySQLdb.escape_string(unicode(tabs[i+1], errors='replace').encode('ascii', 'replace')),
                            MySQLdb.escape_string(unicode(tabs[i], errors='replace').encode('ascii', 'replace'))
                        )
        print 'inserting...'
        if insert_code != '':
            print 'inserting general data'
            g.db.execute(insert_code[:-2] + ';')
            print 'inserting regional data'
            g.db.execute(insert_region_code[:-2] + ';')
            print 'renaming tables!'
            g.db.execute('DROP TABLE IF EXISTS general_list;')
            g.db.execute('ALTER TABLE general_list_temp RENAME TO general_list;')
            g.db.execute('DROP TABLE IF EXISTS general_list_regions;')
            g.db.execute('ALTER TABLE general_list_regions_temp RENAME TO general_list_regions;')
        print 'done!'


def _create_temp_general_table():
    print 'dropping temp table'
    g.db.execute('DROP TABLE IF EXISTS general_list_temp;')
    g.db.execute('DROP TABLE IF EXISTS general_list_regions_temp;')
    print 'creating temp table'
    g.db.execute("""CREATE TABLE IF NOT EXISTS general_list_temp (
                code varchar(6) NOT NULL,
                title varchar(255) NOT NULL,
                genre varchar(255) NOT NULL,
                company varchar(255) NOT NULL,
                status varchar(255) NOT NULL,
                notes text NOT NULL,
                PRIMARY KEY (code))""")
    g.db.execute("""CREATE TABLE IF NOT EXISTS general_list_regions_temp (
                code varchar(6) NOT NULL,
                region varchar(20) NOT NULL,
                avail varchar(1) NOT NULL,
                notes text NOT NULL,
                PRIMARY KEY (code, region))""")
