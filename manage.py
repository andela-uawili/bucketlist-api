#!/usr/bin/env python

import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db

# start the coverage engine:
COV = None
if os.environ.get('BUCKETLIST_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

# create the flask application:
app = create_app(os.getenv('BUCKETLIST_FLASK_CONFIG') or 'default')

# initialize the 'CLI facing' flask extensions on the created app:
manager = Manager(app)
migrate = Migrate(app, db)

# add the flask-script commands to be run from the CLI:
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
    """Discovers and runs unit tests"""

    # restart coverage engine if environ variable not set:
    if coverage and not os.environ.get('BUCKETLIST_COVERAGE'):
        import sys
        os.environ['BUCKETLIST_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    
    # run the tests:
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=1).run(tests)
    
    # output coverage report:
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


# start the server:
if __name__ == '__main__':
    manager.run()
