from app import db
import math


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    call = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(32))
    measurements = db.relationship('Measurement', backref='submitter', lazy='dynamic')
    enabled = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<User {}>'.format(self.call)

    def is_active(self):
        return self.enabled

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frequency = db.Column(db.String(32))
    description = db.Column(db.String(255))
    start_time = db.Column(db.DateTime)
    measurements = db.relationship('Measurement', backref='search', lazy='dynamic')

    def __repr__(self):
        return '<Search {}/{}'.format(self.frequency, self.description)

    def to_dict(self):
        return {
            'id': self.id,
            'frequency': self.frequency,
            'description': self.description,
            'start_time': str(self.start_time),
            'measurements': [measurement.to_dict() for measurement in self.measurements]
                }


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    strength = db.Column(db.Integer)
    heading = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Measurement {}/{}>'.format(self.heading, self.strength)

    def to_dict(self):
        R = 6378.1  # Radius of the Earth
        bearing = math.radians(self.heading)
        d = 50  # distance in KM
        lat_start = math.radians(float(self.latitude))
        lon_start = math.radians(float(self.longitude))
        lat_end = math.asin( math.sin(lat_start)*math.cos(d/R) +
            math.cos(lat_start)*math.sin(d/R)*math.cos(bearing))
        lon_end = lon_start + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat_start),
            math.cos(d/R)-math.sin(lat_start)*math.sin(lat_end))
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'strength': self.strength,
            'heading': self.heading,
            'timestamp': str(self.timestamp),
            'endpoint_latitude': str(math.degrees(lat_end)),
            'endpoint_longitude': str(math.degrees(lon_end)),
        }