from flask import Blueprint, jsonify

titles = Blueprint('titles', __name__)

@titles.route('/loadtitles', methods=['GET'])
def load_titles():
	returnTitles = [
	{
		'mvCompany': 'company a',
		'mvTitle': 'title a',
		'mvGenre': 'genre a',
		'mvStatus': 'status a',
		'mvDescription': 'description a',
		'mvCount': 'count a'
	},
	{
		'mvCompany': 'company z',
		'mvTitle': 'title z',
		'mvGenre': 'genre z',
		'mvStatus': 'status z',
		'mvDescription': 'description z',
		'mvCount': 'count z'
	}
	]
	return jsonify(titles=returnTitles)