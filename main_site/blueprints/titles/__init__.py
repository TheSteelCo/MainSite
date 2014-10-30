import codecs
import csv
import MySQLdb
import StringIO

from flask import Blueprint, g, jsonify, render_template, request
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
    search_term = data.get('searchTerm')
    selected_search = data.get('selectedSearch').lower()
    orderby = data.get('orderby').lower()
    title_order = ', title' if orderby != 'title' else ''
    desc = ' desc' if data.get('ascending') == 'd' else ''
    orderby = orderby + title_order + desc
    results_per_page = int(data.get('resultsPerPage'))

    if data.get('isHotList') == 'true':
        listTable = HotList
        regionTable = HotListRegions
    else:
        listTable = GeneralList
        regionTable = GeneralListRegions

    # get items
    if current_user.region:
        items_query = g.db.query(listTable, regionTable.notes)
    else:
        items_query = g.db.query(listTable)

    if search_term != '':
        items_query = items_query.filter(getattr(listTable, selected_search).like("%" + search_term + "%"))

    if current_user.region:
        items_query = items_query.join(listTable.regions)\
            .filter(regionTable.region == current_user.region, regionTable.avail == 'a')\

    items_query = items_query.order_by(orderby)

    if results_per_page != 0:
        items_query = items_query.slice((int(page) - 1) * results_per_page, int(page) * results_per_page)
    
    items = items_query.all()

    # get total results
    results_query = g.db.query(func.count(listTable.code))
    if search_term != '':
        results_query = results_query.filter(getattr(listTable, selected_search).like("%" + search_term + "%"))

    if current_user.region:
        results_query = results_query.join(listTable.regions)\
            .filter(regionTable.region == current_user.region, regionTable.avail == 'a')
    
    total_results = results_query.scalar()

    returnTitles = []
    if current_user.region:
        for item in items:
            ser = item[0].serialize()
            returnTitles.append({
                'mvCompany': ser.get('company').upper(),
                'mvTitle': ser.get('title').upper(),
                'mvGenre': ser.get('genre'),
                'mvStatus': ser.get('status'),
                'mvDescription': ser.get('notes'),
                'mvCount': item[1]
            })
    else:
        for item in items:
            ser = item.serialize()
            returnTitles.append({
                'mvCompany': ser.get('company').upper(),
                'mvTitle': ser.get('title').upper(),
                'mvGenre': ser.get('genre'),
                'mvStatus': ser.get('status'),
                'mvDescription': ser.get('notes'),
                'mvCount': ''
            })
    return jsonify(dict(titles=returnTitles, results=total_results))


@titles.route('/import-lists', methods=['GET', 'POST'])
def import_lists():
    if _import_general_list(request.files['general']) and _import_hotlist(request.files['hotlist']):
        return jsonify(dict(message='success'))
    else:
        return jsonify(dict(message='error'))


@titles.route('/print', methods=['GET'])
def printable():
    return render_template('main_screen/printable.html')


def _import_general_list(file):
    try:
        if file and allowed_file(file.filename):
            output = StringIO.StringIO(file.read())
            firstline = True
            _create_temp_general_table()
            insert_code = ""
            insert_region_code = ""
            regions = []
            count = 0
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
                    elif count % 100 == 0:
                        _insert_list(insert_code, insert_region_code)
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
                count = count + 1
            if insert_code != '':
                _insert_list(insert_code, insert_region_code)
                g.db.execute('DROP TABLE IF EXISTS general_list;')
                g.db.execute('ALTER TABLE general_list_temp RENAME TO general_list;')
                g.db.execute('DROP TABLE IF EXISTS general_list_regions;')
                g.db.execute('ALTER TABLE general_list_regions_temp RENAME TO general_list_regions;')
        return True
    except:
        return False


def _insert_list(insert_code, insert_region_code):
    if insert_code != '':
        g.db.execute(insert_code[:-2] + ';')
        g.db.execute(insert_region_code[:-2] + ';')


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
            count = 0
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
                    elif count % 100 == 0:
                        _insert_list(insert_code, insert_region_code)
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
            count = count + 1
            if insert_code != '':
                _insert_list(insert_code, insert_region_code)
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
