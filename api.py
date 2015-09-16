from flask import Flask, render_template, url_for, request, redirect
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy

__author__ = 'wfournier'

app = Flask(__name__)
app.config.from_object('config')

api = Api(app)
db = SQLAlchemy(app)

search_parser = reqparse.RequestParser()
search_parser.add_argument('frequency')
search_parser.add_argument('description')

measurement_parser = reqparse.RequestParser()
measurement_parser.add_argument('location')
measurement_parser.add_argument('bearing')
measurement_parser.add_argument('strength')


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frequency = db.Column(db.Float)
    description = db.Column(db.String)
    start_time = db.Column(db.String)

    def __repr__(self):
        return '{freq}: {desc}'.format(freq=self.frequency, desc=self.description)

    def __init__(self, frequency, description):
        self.frequency = frequency
        self.description = description


@app.route('/')
def web_app():
    """
    Serve the main page, the web app
    """
    return render_template('web_app.html')


@app.route('/users', methods=['POST'])
def register():
    """
    Register a new user
    :return: redirect to /
    """
    # session['username'] = request.form['username']
    # session['message'] = request.form['message']
    return redirect(url_for('/'))


class SearchList(Resource):
    def get(self):
        """
        Retrieve list of searches
        :return: list of search IDs with frequency and description
        """
        return []

    def post(self):
        """
        Create a new search
        :return:
        """
        args = search_parser.parse_args()
        # create new record
        new_id = 0
        return new_id, 201


class Search(Resource):
    def get(self, id):
        """
        Retrieve current search result
        :param id: search ID
        :return: data for the current search
        """
        result = []
        return [], 200

    def put(self, id):
        """
        Submit new measurement
        :param id: search ID
        :return: result of insert into DB
        """
        args = measurement_parser.parse_args()
        # create new record
        result = True
        if result:
            return result, 200
        else:
            return result, 500


api.add_resource(SearchList, '/searches')
api.add_resource(Search, '/searches/<id>')

if __name__ == '__main__':
    app.run(debug=True)