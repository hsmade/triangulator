from datetime import datetime
from app import app, api, db, models
from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, url_for, request, redirect
from hashlib import md5
from flask.ext.login import login_user, login_required, current_user

search_parser = reqparse.RequestParser()
search_parser.add_argument('frequency')
search_parser.add_argument('description')

measurement_parser = reqparse.RequestParser()
measurement_parser.add_argument('longitude')
measurement_parser.add_argument('latitude')
measurement_parser.add_argument('heading')
measurement_parser.add_argument('strength')
measurement_parser.add_argument('search')

register_parser = reqparse.RequestParser()
register_parser.add_argument('call')
register_parser.add_argument('password')
register_parser.add_argument('email')


def get_user_by_name(call):
    user = [user for user in models.User.query.all() if user.call == call]
    if len(user) == 1:
        return user[0]
    else:
        return None


class User(Resource):
    def post(self):
        """
        Register a new user
        :return: redirect to /
        """
        args = register_parser.parse_args()
        password = md5()
        password.update(args.password)
        new_user = models.User(call=args.call, email=args.email, password_hash=password.hexdigest())
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            return str(e), 500
        return redirect(url_for('web_app'))

    @login_required
    def get(self):
        users = models.User.query.all()
        return [user.call for user in users]


class SearchList(Resource):
    @login_required
    def get(self):
        """
        Retrieve list of searches
        :return: list of search IDs with frequency and description
        """
        searches = [search.to_dict() for search in models.Search.query.all()]
        return searches

    @login_required
    def post(self):
        """
        Create a new search
        :return:
        """
        args = search_parser.parse_args()
        new_search = models.Search(frequency=args.frequency,
                                   description=args.description,
                                   start_time=datetime.now())
        db.session.add(new_search)
        db.session.commit()
        return redirect(url_for('web_app', search=new_search.id))


class Search(Resource):
    @login_required
    def get(self, id):
        """
        Retrieve current search result
        :param id: search ID
        :return: data for the current search
        """
        search = models.Search.query.get(id) or None
        if not search:
            return [], 404
        else:
            return search.to_dict(), 200

    @login_required
    def post(self, id):
        """
        Submit new measurement
        :param id: search ID
        :return: result of insert into DB
        """
        args = measurement_parser.parse_args()
        new_measurement = models.Measurement(search_id=id,
                                             heading=args.heading,
                                             strength=args.strength,
                                             timestamp=datetime.now(),
                                             latitude=args.latitude,
                                             longitude=args.longitude,
                                             user_id=current_user.get_id())
        db.session.add(new_measurement)
        db.session.commit()
        return redirect(url_for('web_app', search=args.search))

api.add_resource(User, '/users')
api.add_resource(SearchList, '/searches')
api.add_resource(Search, '/searches/<id>')


@app.route('/login')
def login():
    return '''
    <form action="/users/login" method="post">
            <p>Username: <input name="username" type="text"></p>
            <p>Password: <input name="password" type="password"></p>
            <input type="submit">
    </form>
    '''


@app.route('/')
@login_required
def web_app():
    search_id = request.args.get('search')
    search_dict = False
    average_longitude = 0
    average_latitude = 0
    if search_id:
        search = models.Search.query.get(search_id)
        if search:
            search_dict = search.to_dict()
            if search_dict['measurements']:
                average_longitude = \
                    sum([measurement['longitude'] for measurement in search_dict['measurements']]) / len(search_dict['measurements'])
                average_latitude = \
                    sum([measurement['latitude'] for measurement in search_dict['measurements']]) / len(search_dict['measurements'])
        return render_template('web_app.html', search=search_dict,
                               average_longitude=average_longitude, average_latitude=average_latitude)
    else:
        return render_template('web_app.html', searches=models.Search.query.all())


@app.route('/users/login', methods=['post'])
def login_check():
    user = get_user_by_name(request.form['username'])
    if user:
        print 'found user: {}'.format(user)
    else:
        return 'Invalid username', 404
    password = md5()
    password.update(request.form['password'])
    if user.password_hash == password.hexdigest():
        login_user(user)
        print 'Logged in'
        return redirect(url_for('web_app'))
    else:
        return 'Invalid password', 500


@app.route('/login_or_register')
def login_or_register():
    """
    :return: register / login page
    """
    return '''
    <a href="{login}">Login</a>
    <a href="{register}">Register</a>
    '''.format(login=url_for("login"), register=url_for("register"))


@app.route('/register')
def register():
    """
    Register
    :return:
    """
    return '''
    <form action="{users}" method="post">
    Call: <input name="call"><br />
    e-Mail: <input name="email"><br />
    Password: <input name="password" type="password"><br />
    <input type="submit">
    </form>
    '''.format(users="/users")
