import codecs
import csv
import MySQLdb
import StringIO

from flask import Blueprint, g, jsonify, request
from flask.ext.login import current_user
from main_site.models import GeneralList, GeneralListRegions, HotList, HotListRegions
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

    if data.get('isHotList') == 'true':
        listTable = HotList
        regionTable = HotListRegions
    else:
        listTable = GeneralList
        regionTable = GeneralListRegions

    if searchTerm == '':
        items = g.db.query(listTable, regionTable.notes)\
                    .join(listTable.regions)\
                    .filter(regionTable.region == current_user.region, regionTable.avail == 'a')\
                    .order_by(orderby)\
                    .slice((int(page) - 1) * 20, int(page) * 20)\
                    .all()
        total_results = g.db.query(func.count(listTable.code))\
            .join(listTable.regions)\
            .filter(regionTable.region == current_user.region, regionTable.avail == 'a')\
            .scalar()
    else:
        items = g.db.query(listTable, regionTable.notes)\
                    .filter(getattr(listTable, selectedSearch).like("%" + searchTerm + "%"))\
                    .join(listTable.regions)\
                    .filter(regionTable.region == current_user.region, regionTable.avail == 'a')\
                    .order_by(orderby)\
                    .slice((int(page) - 1) * 20, int(page) * 20)\
                    .all()
        total_results = g.db.query(func.count(listTable.code))\
            .filter(getattr(listTable, selectedSearch).like("%" + searchTerm + "%"))\
            .join(listTable.regions)\
            .filter(regionTable.region == current_user.region, regionTable.avail == 'a')\
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


@titles.route('/import-lists', methods=['GET', 'POST'])
def import_lists():
    if _import_general_list(request.files['general']) and _import_hotlist(request.files['hotlist']):
        return jsonify(dict(message='success'))
    else:
        return jsonify(dict(message='error'))


def _import_general_list(file):
    try:
        if file and allowed_file(file.filename):
            output = StringIO.StringIO(file.read())
            firstline = True
            _create_temp_general_table()
            insert_code = ""
            insert_region_code = ""
            regions = []
            for line in output.getvalue().splitlines():
                if firstline:
                    firstline = False
                    tabs = line.split('\t')
                    for i in xrange(6, len(tabs), 2):
                        regions.append(unicode(tabs[i], errors='replace').encode('ascii', 'replace'))
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
            if insert_code != '':
                g.db.execute(insert_code[:-2] + ';')
                g.db.execute(insert_region_code[:-2] + ';')
                g.db.execute('DROP TABLE IF EXISTS general_list;')
                g.db.execute('ALTER TABLE general_list_temp RENAME TO general_list;')
                g.db.execute('DROP TABLE IF EXISTS general_list_regions;')
                g.db.execute('ALTER TABLE general_list_regions_temp RENAME TO general_list_regions;')
        return True
    except:
        return False

def _create_temp_general_table():
    g.db.execute('DROP TABLE IF EXISTS general_list_temp;')
    g.db.execute('DROP TABLE IF EXISTS general_list_regions_temp;')
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


def _import_hotlist(file):
    try:
        if file and allowed_file(file.filename):
            output = StringIO.StringIO(file.read())
            firstline = True
            _create_temp_hotlist_table()
            insert_code = ""
            insert_region_code = ""
            regions = []
            for line in output.getvalue().splitlines():
                if firstline:
                    firstline = False
                    tabs = line.split('\t')
                    for i in xrange(6, len(tabs), 2):
                        regions.append(unicode(tabs[i], errors='replace').encode('ascii', 'replace'))
                else:
                    if insert_code == "":
                        insert_code = "INSERT INTO hot_list_temp(code, title, genre, company, status, notes) VALUES "
                        insert_region_code = "INSERT INTO hot_list_regions_temp(code, region, avail, notes) VALUES "

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
            if insert_code != '':
                g.db.execute(insert_code[:-2] + ';')
                g.db.execute(insert_region_code[:-2] + ';')
                g.db.execute('DROP TABLE IF EXISTS hot_list;')
                g.db.execute('ALTER TABLE hot_list_temp RENAME TO hot_list;')
                g.db.execute('DROP TABLE IF EXISTS hot_list_regions;')
                g.db.execute('ALTER TABLE hot_list_regions_temp RENAME TO hot_list_regions;')
        return True
    except:
        return False


def _create_temp_hotlist_table():
    g.db.execute('DROP TABLE IF EXISTS hot_list_temp;')
    g.db.execute('DROP TABLE IF EXISTS hot_list_regions_temp;')
    g.db.execute("""CREATE TABLE IF NOT EXISTS hot_list_temp (
                code varchar(6) NOT NULL,
                title varchar(255) NOT NULL,
                genre varchar(255) NOT NULL,
                company varchar(255) NOT NULL,
                status varchar(255) NOT NULL,
                notes text NOT NULL,
                PRIMARY KEY (code))""")
    g.db.execute("""CREATE TABLE IF NOT EXISTS hot_list_regions_temp (
                code varchar(6) NOT NULL,
                region varchar(20) NOT NULL,
                avail varchar(1) NOT NULL,
                notes text NOT NULL,
                PRIMARY KEY (code, region))""")