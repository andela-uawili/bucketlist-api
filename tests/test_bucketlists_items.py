import unittest
import json
from flask import current_app, url_for
from app import create_app, db
from app.models import User, Bucketlist, BucketlistItem


class BucketlistsItemsTestCase(unittest.TestCase):
    """ Testcase for the BucketlistItem related API endpoints 
    """

    def setUp(self):

        # setup the app and push app context:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        # setup the db:
        db.create_all()

        # create test user:
        self.user = User(
            username="Somebody", 
            email="somebody2@somedomain.com",
            password="anything"
        )
        db.session.add(self.user)
        db.session.commit()

        # init the test client:
        self.client = self.app.test_client()

        # log the user in and get authentication token:
        response = self.client.post(
            url_for('login'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email': 'somebody2@somedomain.com',
                'password': 'anything',
            })
        )
        self.access_token = json.loads(response.data).get('access_token')

        # fix the db with sample bucketlists for the user:
        bucketlist_1 = Bucketlist(name="The Melancholic's Wishlist", created_by=self.user)
        db.session.add(bucketlist_1)
        bucketlist_2 = Bucketlist(name="The Phlegmatic's Wishlist", created_by=self.user)
        db.session.add(bucketlist_2)
        bucketlist_3 = Bucketlist(name="The Choleric's Wishlist", created_by=self.user)
        db.session.add(bucketlist_3)
        db.session.commit()

        # fix the db with sample bucketlists items for the bucketlist_3:
        item_1 = BucketlistItem(name="Bungee off the Brooklyn Bridge", done=True, bucketlist=bucketlist_3)
        db.session.add(item_1)
        item_2 = BucketlistItem(name="Kayak across the Atlantic", done=True, bucketlist=bucketlist_3)
        db.session.add(item_2)
        item_3 = BucketlistItem(name="Scuba dive in the Mariannah Trench", done=True, bucketlist=bucketlist_3)
        db.session.add(item_3)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_create_bucketlist_with_name(self):
        """ Tests the create_bucketlist API endpoint 
            with a name provided.
            POST '/bucketlists/'
        """
        response = self.client.post(
            url_for('api.create_bucketlist'),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'The Sanguines Wishlist',
            })
        )
        response_data = json.loads(response.data) 
        bucketlist = response_data.get('bucketlist')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(bucketlist.get('name'), "The Sanguines Wishlist")
        self.assertEqual(bucketlist.get('created_by').get('username'), self.user.username)
        self.assertEqual(
            response_data.get('bucketlists_url'),  
            url_for('api.get_bucketlists', _external=True)
        )


    def test_create_bucketlist_without_name(self):
        """ Tests that the create_bucketlist API endpoint
            without providing a name errors out.
            POST '/bucketlists/'
        """
        response = self.client.post(
            url_for('api.create_bucketlist'),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({})
        )
        self.assertEqual(response.status_code, 400)


    def test_update_bucketlist_with_valid_id(self):
        """ Tests that the update_bucketlist API endpoint
            when provided valid id.
            PUT '/bucketlists/3'
        """
        response = self.client.put(
            url_for('api.update_bucketlist', id=1),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'The Mel-Sans Wishlist',
            })
        )
        print response
        
        response_data = json.loads(response.data) 
        bucketlist = response_data.get('bucketlist')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(bucketlist.get('name'), "The Mel-Sans Wishlist")
        self.assertEqual(bucketlist.get('created_by').get('username'), self.user.username)
        self.assertEqual(
            response_data.get('bucketlists_url'),  
            url_for('api.get_bucketlists', _external=True)
        )


    def test_update_bucketlist_with_invalid_id(self):
        """ Tests that the update_bucketlist API endpoint
            errors out when provided an invalid id.
            PUT '/bucketlists/10'
        """
        response = self.client.put(
            url_for('api.update_bucketlist', id=10),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'The Mel-Chols Wishlist',
            })
        )
        self.assertEqual(response.status_code, 405)


    def test_delete_bucketlist_with_valid_id(self):
        """ Tests the delete_bucketlist API endpoint
            when provided valid id.
            DELETE '/bucketlists/3'
        """
        response = self.client.delete(
            url_for('api.delete_bucketlist', id=3),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data) 
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('status'), 'deleted')
        self.assertEqual(
            response_data.get('bucketlists_url'),  
            url_for('api.get_bucketlists', _external=True)
        )


    def test_delete_bucketlist_with_invalid_id(self):
        """ Tests that the delete_bucketlist API endpoint
            errors out when provided an invalid id.
            DELETE '/bucketlists/10'
        """
        response = self.client.delete(
            url_for('api.delete_bucketlist', id=10),
            headers=self.get_api_headers(self.access_token),
        )
        self.assertEqual(response.status_code, 405)