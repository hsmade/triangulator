from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    call = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(32))
    measurements = db.relationship('Measurement', backref='submitter', lazy='dynamic')
    enabled = db.Column(db.Integer)

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
    heading = db.Column(db.Integer)
    strength = db.Column(db.Integer)
    location = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Measurement {}/{}>'.format(self.heading, self.strength)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'heading': self.heading,
            'strength': self.strength,
            'location': self.location,
            'timestamp': str(self.timestamp),
            'endpoint': ''  # FIXME calculate end point of line by location and heading
        }