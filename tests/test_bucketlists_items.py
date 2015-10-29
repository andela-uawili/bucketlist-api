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
        bucketlist_1 = Bucketlist(name="The Choleric's Wishlist", created_by=self.user)
        db.session.add(bucketlist_1)
        db.session.commit()

        # fix the db with sample bucketlists items for the bucketlist_3:
        item_1 = BucketlistItem(name="Bungee off the Brooklyn Bridge", done=False, bucketlist=bucketlist_1)
        db.session.add(item_1)
        item_2 = BucketlistItem(name="Kayak across the Atlantic", done=False, bucketlist=bucketlist_1)
        db.session.add(item_2)
        item_3 = BucketlistItem(name="Scuba dive in the Mariannah Trench", done=False, bucketlist=bucketlist_1)
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


    def test_create_bucketlist_item_with_parameters(self):
        """ Tests the create_bucketlist_item API endpoint.
            POST '/bucketlists/<int:id>/items/'
        """
        response = self.client.post(
            url_for('api.create_bucketlist_item', id=1),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'Camp on Mount Kilimanjaro',
                'done': False,
            })
        )
        response_data = json.loads(response.data) 
        bucketlist_item = response_data.get('bucketlist_item')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(bucketlist_item.get('name'), "Camp on Mount Kilimanjaro")
        self.assertEqual(bucketlist_item.get('done'), False)
        self.assertEqual(
            response_data.get('bucketlist_url'),  
            url_for('api.get_bucketlist', id=1, _external=True)
        )


    def test_create_bucketlist_item_without_parameters(self):
        """ Tests that the create_bucketlist_item API endpoint
            without providing a name errors out.
            POST '/bucketlists/<int:id>/items/'
        """
        response = self.client.post(
            url_for('api.create_bucketlist_item', id=1),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({})
        )
        self.assertEqual(response.status_code, 400)


    def test_create_bucketlist_item_with_invalid_id(self):
        """ Tests that the create_bucketlist_item API endpoint
            with invalid id errors out.
            POST '/bucketlists/<int:id>/items/'
        """
        response = self.client.post(
            url_for('api.create_bucketlist_item', id=34),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'Camp on Mount Kilimanjaro',
            })
        )
        self.assertIn(response.status_code, [404, 405])


    def test_update_bucketlist_item_with_valid_id_and_item_id(self):
        """ Tests that the update_bucketlist_item API endpoint
            when provided valid id.
            PUT '/bucketlists/<int:id>/items/<int:item_id>'
        """
        response = self.client.put(
            url_for('api.update_bucketlist_item', id=1, item_id=2),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'done': True,
            })
        )
        response_data = json.loads(response.data) 
        bucketlist_item = response_data.get('bucketlist_item')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(bucketlist_item.get('done'), True)


    def test_update_bucketlist_item_with_invalid_id(self):
        """ Tests that the update_bucketlist_item API endpoint
            errors out when provided an invalid id.
            PUT '/bucketlists/<int:id>/items/<int:item_id>'
        """
        response = self.client.put(
            url_for('api.update_bucketlist_item', id=233, item_id=2),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'The Mel-Chols Wishlist',
            })
        )
        self.assertIn(response.status_code, [404, 405])


    def test_update_bucketlist_item_with_invalid_item_id(self):
        """ Tests that the update_bucketlist_item API endpoint
            errors out when provided an invalid id.
            PUT '/bucketlists/<int:id>/items/<int:item_id>'
        """
        response = self.client.put(
            url_for('api.update_bucketlist_item', id=1, item_id=24),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'name': 'The Mel-Chols Wishlist',
            })
        )
        self.assertIn(response.status_code, [404, 405])


    def test_delete_bucketlist_item_with_valid_id_and_item_id(self):
        """ Tests the delete_bucketlist_item API endpoint
            when provided valid id.
            DELETE '/bucketlists/<int:id>/items/<int:item_id>'
        """
        response = self.client.delete(
            url_for('api.delete_bucketlist_item', id=1, item_id=2),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data) 
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('status'), 'deleted')
        self.assertEqual(
            response_data.get('bucketlist_url'),  
            url_for('api.get_bucketlist', id=1, _external=True)
        )


    def test_delete_bucketlist_item_with_invalid_id(self):
        """ Tests that the delete_bucketlist API endpoint
            errors out when provided an invalid id.
            DELETE '/bucketlists/<int:id>/items/<int:item_id>'
        """
        response = self.client.delete(
            url_for('api.delete_bucketlist_item', id=10, item_id=2),
            headers=self.get_api_headers(self.access_token),
        )
        self.assertIn(response.status_code, [404, 405])


    def test_delete_bucketlist_item_with_invalid_item_id(self):
        """ Tests that the delete_bucketlist API endpoint
            errors out when provided an invalid item_id.
            DELETE '/bucketlists/<int:id>/items/<int:item_id>'
        """
        response = self.client.delete(
            url_for('api.delete_bucketlist_item', id=1, item_id=234),
            headers=self.get_api_headers(self.access_token),
        )
        self.assertIn(response.status_code, [404, 405])