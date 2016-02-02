import logging
logging.basicConfig(level=logging.DEBUG)
from app import db, models
from hashlib import md5
import sys

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


