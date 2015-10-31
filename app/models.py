from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app, request, url_for, g
from . import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, index=True, unique=True)
    password_hash = db.Column(db.Text)
    username = db.Column(db.Text, nullable=True)
    date_joined = db.Column(db.DateTime, index=True, default=datetime.now())
    logged_in = db.Column(db.Boolean, default=False)

    bucketlists = db.relationship(
        'Bucketlist', 
        lazy='dynamic', 
        backref=db.backref('created_by', lazy='select'),
        cascade='all, delete-orphan'
    )

    @property
    def password(self):
        raise AttributeError('The password attribute is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.username if self.username else self.email

    def to_json(self):
        """ returns a json-style dictionary representation of the user.
        """
        json_user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_joined': self.date_joined.strftime(current_app.config['DATE_TIME_FORMAT']),
            'url': url_for('api.get_user', id=self.id, _external=True),
        }
        return json_user


class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, index=True, nullable=False)
    date_created = db.Column(db.DateTime, index=True, default=datetime.now())
    date_modified = db.Column(db.DateTime, index=True, default=datetime.now(), onupdate=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   
    items = db.relationship(
        'BucketlistItem', 
        lazy='dynamic', 
        backref=db.backref('bucketlist', lazy='select'),
        cascade='all, delete-orphan'
    )

    def to_json(self, with_items=False):
        """ returns a json-style dictionary representation of the bucketlist
            and it's associated items.
        """
        json_bucketlist = {
            'id': self.id,
            'name': self.name,
            'item_count': self.items.count(),
            'date_created': self.date_created.strftime(current_app.config['DATE_TIME_FORMAT']),
            'date_modified': self.date_modified.strftime(current_app.config['DATE_TIME_FORMAT']),
            'created_by': {
                'username': str(self.created_by),
                'url': url_for('api.get_user', id=self.creator_id, _external=True),
            },
            'url': url_for('api.get_bucketlist', id=self.id, _external=True),
        }
        return json_bucketlist

    @staticmethod
    def from_json(json_bucketlist):
        """ creates a new bucketlist or updates an existing one from
            a json-style representation.
        """
        # create new:
        bucketlist = Bucketlist()
        
        # update the item with the json values:
        name = json_bucketlist.get('name')
        if name:
            bucketlist.name = name

        return bucketlist

    @staticmethod
    def get_user_bucketlist(user, id):
        """ Fetchs a user's bucketlist by id.
        """
        # get the bucketlist:
        bucketlist = Bucketlist.query\
                     .filter_by(created_by=user, id=id)\
                     .first()
        if not bucketlist:
            raise Exception('Item does not exist')
        
        return bucketlist


class BucketlistItem(db.Model):
    __tablename__ = 'bucketlist_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, index=True, nullable=False)
    date_created = db.Column(db.DateTime, index=True, default=datetime.now())
    date_modified = db.Column(db.DateTime, index=True, default=datetime.now(), onupdate=datetime.now())
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'), nullable=False)
    done = db.Column(db.Boolean, default=False)
   
    def to_json(self):
        """ returns a json-style dictionary representation of the bucketlist item
        """
        json_bucketlist_item = {
            'id': self.id,
            'name': self.name,
            'date_created': self.date_created.strftime(current_app.config['DATE_TIME_FORMAT']),
            'date_modified': self.date_modified.strftime(current_app.config['DATE_TIME_FORMAT']),
            'done': self.done,
        }
        return json_bucketlist_item

    @staticmethod
    def from_json(json_bucketlist_item):
        """ creates a new bucketlist item or updates an existing one from
            a json-style representation.
        """
        # create new:
        bucketlist_item = BucketlistItem()
        
        # update the item with the json values:
        name = json_bucketlist_item.get('name')
        done = json_bucketlist_item.get('done')
        if name:
            bucketlist_item.name = name
        if isinstance(done, bool):
            bucketlist_item.done = done
        
        return bucketlist_item

    @staticmethod
    def get_bucketlist_item(bucketlist, id):
        """ Fetchs an item by id from a bucketlist.
        """
        # get bucketlist-item:
        bucketlist_item = BucketlistItem.query\
                          .filter_by(bucketlist=bucketlist, id=id)\
                          .first()
        if not bucketlist_item:
            raise Exception('Item does not exist')
        
        return bucketlist_item