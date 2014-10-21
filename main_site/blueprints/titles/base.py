from flask import jsonify

def load_titles():
	print 'loading titles'
	return jsonify(titles='')