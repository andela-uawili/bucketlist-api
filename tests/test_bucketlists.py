import unittest
import json
from flask import current_app, url_for
from app import create_app, db
from app.models import User, Bucketlist, BucketlistItem


class BucketlistsTestCase(unittest.TestCase):
    """ Testcase for the Bucketlist related API endpoints 
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


    def get_api_headers(self, access_token=''):
        """ formats the headers to be used when accessing API endpoints.
        """
        return {
            'Authorization': "JWT {}".format(access_token),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    
    def test_get_bucketlists_with_default_parameters(self):
        """ Tests the get_bucketlists API endpoint with no/default 
            query string parameters
            GET '/bucketlists/'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_bucketlists'),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        bucketlists = response_data.get('bucketlists')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(bucketlists), 3)
        self.assertEqual(response_data.get('total'), 3)
        self.assertEqual(response_data.get('current_page'), 1)
        self.assertEqual(response_data.get('prev_url'), None)
        self.assertEqual(response_data.get('next_url'), None)


    def test_get_bucketlists_with_limit_and_page_parameters(self):
        """ Tests the get_bucketlists API endpoint with limit
            and page_parameters query string parameters
            GET '/bucketlists/?limit=1&page=2'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_bucketlists', limit=1, page=2),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        bucketlists = response_data.get('bucketlists')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(bucketlists), 1)
        self.assertEqual(response_data.get('total'), 3)
        self.assertEqual(response_data.get('current_page'), 2)
        self.assertEqual(response_data.get('prev_url'),  url_for('api.get_bucketlists', limit=1, page=1, _external=True))
        self.assertEqual(response_data.get('next_url'),  url_for('api.get_bucketlists', limit=1, page=3, _external=True))


    def test_get_bucketlists_with_search_parameter(self):
        """ Tests the get_bucketlists API endpoint with serach query string parameters
            GET '/bucketlists/?q=brooklyn'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_bucketlists', q='Choleric', limit=150),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        bucketlists = response_data.get('bucketlists')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(bucketlists), 1)
        self.assertEqual(bucketlists[0].get('name'), "The Choleric's Wishlist")
        self.assertEqual(response_data.get('total'), 1)
        self.assertEqual(response_data.get('current_page'), 1)
        self.assertEqual(response_data.get('prev_url'),  None)
        self.assertEqual(response_data.get('next_url'),  None)


    def test_get_bucketlist_with_valid_id_and_parameters(self):
        """ Tests the get_bucketlist API using valid id.
            Page and limit params for its items are also specified
            GET '/bucketlist/3?limit=1&page=2'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_bucketlist', id=3, limit=1, page=2),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        bucketlist = response_data.get('bucketlist')
        bucketlist_items = bucketlist.get('items')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(bucketlist.get('name'), "The Choleric's Wishlist")

        self.assertEqual(len(bucketlist_items), 1)
        self.assertEqual(response_data.get('total'), 3)
        self.assertEqual(response_data.get('current_page'), 2)
        self.assertEqual(
            response_data.get('prev_url'),  
            url_for('api.get_bucketlist',  id=3, limit=1, page=1, _external=True)
        )
        self.assertEqual(
            response_data.get('next_url'),  
            url_for('api.get_bucketlist', id=3, limit=1, page=3, _external=True)
        )
        self.assertEqual(
            response_data.get('bucketlists_url'),  
            url_for('api.get_bucketlists', _external=True)
        )


    def test_get_bucketlist_with_valid_id_and_invalid_limit(self):
        """ Tests the get_bucketlist API using valid id.
            Page and limit params for its items are also specified
            GET '/bucketlist/3?limit=150'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_bucketlist', id=3, limit=150),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        bucketlist = response_data.get('bucketlist')
        bucketlist_items = bucketlist.get('items')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(bucketlist.get('name'), "The Choleric's Wishlist")

        self.assertEqual(len(bucketlist_items), 3)
        self.assertEqual(response_data.get('total'), 3)
        self.assertEqual(response_data.get('current_page'), 1)
        self.assertEqual(response_data.get('prev_url'), None)
        self.assertEqual(response_data.get('next_url'), None)
        self.assertEqual(
            response_data.get('bucketlists_url'),  
            url_for('api.get_bucketlists', _external=True)
        )


    def test_get_bucketlist_with_invalid_id(self):
        """ Tests the get_bucketlist API endpoint using valid id.
            Page and limit params for its items are also specified
            GET '/bucketlist/5'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_bucketlist', id=5),
            headers=self.get_api_headers(self.access_token)
        )
        self.assertEqual(response.status_code, 404)


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
        self.assertIn(response.status_code, [404, 405])


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
        self.assertIn(response.status_code, [404, 405])