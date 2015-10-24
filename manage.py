#!/usr/bin/env python

import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db

# create the flask application:
app = create_app(os.getenv('BUCKETLIST_FLASK_CONFIG') or 'default')

# initialize the 'CLI facing' flask extensions on the created app:
manager = Manager(app)
migrate = Migrate(app, db)

# add the flask-script commands to be run from the CLI:
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Discovers and runs unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
