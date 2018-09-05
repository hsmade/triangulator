#!python
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import app, db, models
from hashlib import md5
import sys
import os

def upgrade():
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' + str(v))

if os.path.isfile("app.db"):
    upgrade()
else:
    db.create_all()
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO,
                            api.version(SQLALCHEMY_MIGRATE_REPO))

    upgrade()
    if len(sys.argv) == 1:
        raise SystemExit('Please specify a password')
    
    password = md5()
    password.update(sys.argv[1])
    
    found_admin = None
    for user in models.User.query.all():
        if user.call == 'admin':
            found_admin = user
    if found_admin:
        found_admin.password_hash = password.hexdigest()
        db.session.commit()
    else:
        admin = models.User(call='admin', email='triangulator@hph7wim.com', password_hash=password.hexdigest())
        db.session.add(admin)
        db.session.commit()


app.run(debug=True, host='0.0.0.0', port=8001)

