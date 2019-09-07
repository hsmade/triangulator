from datetime import datetime
from app import app, api, db, models
from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, url_for, request, redirect
from hashlib import md5
from flask_login import login_user, login_required, current_user, logout_user
from functools import wraps
import logging
from logging import handlers

file_handler = handlers.RotatingFileHandler('/tmp/triangulator.log',
                                            maxBytes=10024000)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - {} - %(message)s'.format(
    getattr(current_user, 'call', 'Not authenticated')))
file_handler.setFormatter(formatter)
logger = logging.getLogger('app.view')
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

search_parser = reqparse.RequestParser()
search_parser.add_argument('frequency')
search_parser.add_argument('description')

measurement_parser = reqparse.RequestParser()
measurement_parser.add_argument('longitude')
measurement_parser.add_argument('latitude')
measurement_parser.add_argument('heading')
measurement_parser.add_argument('strength')
measurement_parser.add_argument('search')
measurement_parser.add_argument('timestamp')

register_parser = reqparse.RequestParser()
register_parser.add_argument('call')
register_parser.add_argument('password')
register_parser.add_argument('email')
register_parser.add_argument('longitude')
register_parser.add_argument('latitude')


def requires_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user and current_user.call != 'admin':
            return 'Not allowed', 404
        return f(*args, **kwargs)
    return wrapper


def get_user_by_name(call):
    user = [user for user in models.User.query.all() if user.call == call]
    if len(user) == 1:
        return user[0]
    else:
        print user
        return None


class User(Resource):
    def post(self):
        """
        Register a new user
        :return: redirect to /
        """
        args = register_parser.parse_args()
        logger.debug('User:post() with args: {}'.format(args))
        password = md5()
        password.update(args.password)
        print args.longitude, args.latitude
        if not args.longitude: 
            args.longitude=0
        if not args.latitude: 
            args.longitude=0
        new_user = models.User(call=args.call, email=args.email, password_hash=password.hexdigest(),
                               longitude=args.longitude, latitude=args.latitude)
        try:
            db.session.add(new_user)
            db.session.commit()
            # new_measurement = models.Measurement(search_id=0, user_id=new_user.id, latitude=args.latitude,
                                                 # longitude=args.longitude, strength=0, heading=0)
            # db.session.add(new_measurement)
            # db.session.commit()
        except Exception as e:
            return str(e), 500

        login_user(new_user)
        return redirect(url_for('web_app'))

    @requires_admin
    @login_required
    def get(self):
        logger.debug('User:get()')
        users = models.User.query.all()
        return [(user.call, user.email) for user in users]


class SearchList(Resource):
    @login_required
    def get(self):
        """
        Retrieve list of searches
        :return: list of search IDs with frequency and description
        """
        logger.debug('SearchList:get()')
        searches = [search.to_dict() for search in models.Search.query.all()]
        return searches

    @login_required
    def post(self):
        """
        Create a new search
        :return:
        """
        args = search_parser.parse_args()
        logger.debug('SearchList.post() with args: {}'.format(args))
        new_search = models.Search(frequency=args.frequency,
                                   description=args.description,
                                   start_time=datetime.now(),
                                   user_id=current_user.id)
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
        logger.debug('Search:get(id={})'.format(id))
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
        logger.debug('Search.post(id={}) with args: {}'.format(id, args))
        if not args.timestamp:
            timestamp = datetime.now()
        else:
            timestamp = datetime.strptime(args.timestamp, '%Y-%m-%d %H:%M')
        new_measurement = models.Measurement(search_id=id,
                                             heading=float(args.heading),
                                             strength=int(args.strength),
                                             timestamp=timestamp,
                                             latitude=float(args.latitude),
                                             longitude=float(args.longitude),
                                             user_id=current_user.get_id())
        db.session.add(new_measurement)
        db.session.commit()
        return redirect(url_for('web_app', search=args.search))

api.add_resource(User, '/users')
api.add_resource(SearchList, '/searches')
api.add_resource(Search, '/searches/<id>')


@app.route('/login')
def login():
    """
    Login page
    """
    logger.debug('login()')
    return render_template('login.html', user=None)


@app.route('/')
@login_required
def web_app():
    """
    Main app page
    """
    search_id = request.args.get('search')
    start = request.args.get('start', False)
    end = request.args.get('end', False)
    if start:
        start = datetime.strptime(start, '%Y-%m-%d %H:%M')
    if end:
        end = datetime.strptime(end, '%Y-%m-%d %H:%M')
    logger.debug('web_app() with search_id: {}'.format(search_id))
    search_dict = False
    average_longitude = 0
    average_latitude = 0
    if search_id:
        search = models.Search.query.get(search_id)
        if search:
            search_dict = search.filter(start, end)
            if search_dict['measurements']:
                average_longitude = \
                    sum([measurement['longitude'] for measurement in search_dict['measurements']]) / len(search_dict['measurements'])
                average_latitude = \
                    sum([measurement['latitude'] for measurement in search_dict['measurements']]) / len(search_dict['measurements'])
        return render_template('web_app.html', search=search_dict,
                               average_longitude=average_longitude,
                               average_latitude=average_latitude,
                               searches=models.Search.query.all(),
                               user=current_user,
                               datetime=datetime.now().strftime('%Y-%m-%d %H:%M'),
                               key=app.config["KEY"],
                               )
    else:
        return render_template('web_app.html', searches=models.Search.query.all(),
                               key=app.config["KEY"],
                               user=current_user, datetime=datetime.now().strftime('%Y-%m-%d %H:%M'))


@app.route('/users/login', methods=['post'])
def login_check():
    """
    For flask-login, verifies login
    """
    logger.debug('login_check() with form: {}'.format(request.form))
    user = get_user_by_name(request.form['call'])
    if user:
        print 'found user: {}'.format(user)
    else:
        return 'Invalid username', 404
    if not user.is_active():
        return 'User disabled', 500
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
    base page, not authenticated
    """
    logger.debug('login_or_register()')
    return render_template('login_or_register.html', user=None)


@app.route('/register')
def register():
    """
    Register a new user
    """
    logger.debug('register()')
    return render_template('register.html', user=None)


@app.route('/logout')
def logout():
    """
    Logout
    """
    logger.debug('logout()')
    logout_user()
    return redirect(url_for('web_app'))


@app.route('/admin/users')
@requires_admin
def user_list():
    logger.debug('user_list()')
    return render_template('users.html', users=models.User.query.all(), user=current_user)


@app.route('/admin/users/<id>/enable')
@requires_admin
def user_enable(id):
    logger.debug('user_enable(id={})'.format(id))
    user = models.User.query.get(id)
    if not user:
        return 'User not found', 404
    else:
        user.enabled = 1
        db.session.commit()
        return redirect(url_for('user_list'))


@app.route('/admin/users/<id>/disable')
@requires_admin
def user_disable(id):
    logger.debug('user_disable(id={})'.format(id))
    user = models.User.query.get(id)
    if not user:
        return 'User not found', 404
    else:
        user.enabled = 0
        db.session.commit()
        return redirect(url_for('user_list'))


@requires_admin
@app.route('/admin/users/<id>/delete')
def user_delete(id):
    logger.debug('user_delete(id={})'.format(id))
    user = models.User.query.get(id)
    if not user:
        return 'User not found', 404
    else:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('user_list'))


@app.route('/user/<id>/measurements')
def user_measurements(id):
    logger.debug('user_measurements(id={})'.format(id))
    user = models.User.query.get(id)
    if not (user == current_user or current_user.call == 'admin'):
        return 'Not allowed', 403
    measurements = [row.to_dict() for row in models.Measurement.query.all() if row.user_id == user.id]
    if user.call == 'admin':
        measurements.insert(0, {
            'timestamp': 'Registration',
            'search_id':    0,
            'longitude': user.longitude,
            'latitude': user.latitude,
            'heading': 0,
            'strength': 0,
        })
    return render_template('measurements.html', measurements=measurements, user=current_user)


@app.route('/measurement/<id>/delete')
def measurement_delete(id):
    logger.debug('measurement_delete(id={})'.format(id))
    measurement = models.Measurement.query.get(id)
    user = models.User.query.get(measurement.user_id)
    if not (current_user == user or current_user.call == 'admin'):
        return 'Not allowed', 403
    db.session.delete(measurement)
    db.session.commit()
    return redirect('/user/{user}/measurements'.format(user=user.id))


@app.route('/user/<user_id>/searches')
def user_searches(user_id):
    logger.debug('user_searches(user_id={})'.format(user_id))
    user = models.User.query.get(user_id)
    if not (user == current_user or current_user.call == 'admin'):
        return 'Not allowed', 403
    searches = [row.to_dict() for row in models.Search.query.all() if row.user_id == user.id]
    return render_template('searches.html', searches=searches, user=current_user)


@app.route('/search/<id>/delete')
def search_delete(id):
    logger.debug('search_delete(id={})'.format(id))
    search = models.Search.query.get(id)
    user = models.User.query.get(search.user_id)
    if not (current_user == user or current_user.call == 'admin'):
        return 'Not allowed', 403
    db.session.delete(search)
    db.session.commit()
    return redirect('/user/{user}/searches'.format(user=user.id))
