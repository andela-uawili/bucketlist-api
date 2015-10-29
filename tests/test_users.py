import unittest
import json
from flask import current_app, url_for
from app import create_app, db
from app.models import User


class UsersTestCase(unittest.TestCase):
    """ Testcase for the User related API endpoints
    """

    def setUp(self):

        # setup the app and push app context:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # init the test client:
        self.client = self.app.test_client()

        # setup the db:
        db.create_all()

        # create test user:
        self.user = User(
            username="Somebody", 
            email="somebody@somedomain.com",
            password="anything"
        )
        db.session.add(self.user)
        db.session.commit()

        # log the user in and get authentication token:
        response = self.client.post(
            url_for('login'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email': 'somebody@somedomain.com',
                'password': 'anything',
            })
        )
        self.access_token = json.loads(response.data).get('access_token')


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


    def test_gets_user_with_valid_id(self):
        """ Tests the get_user API endpoint with valid id
            GET '/users/<id>'
        """
        response = self.client.get(
            url_for('api.get_user', id=self.user.id),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        profile = response_data.get('profile')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile.get('email'), self.user.email)
        self.assertEqual(profile.get('url'), url_for('api.get_user', id=self.user.id, _external=True))
        self.assertEqual(response_data.get('bucketlists_url'), url_for('api.get_bucketlists', _external=True))


    def test_get_user_with_invalid_id_forbidden(self):
        """ Tests the get_user API endpoint with invalid id
            GET '/users/<id>'
        """
        # get user with invalid id:
        response = self.client.get(
            url_for('api.get_user', id=243),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)


    def test_updates_user_with_valid_id(self):
        """ Tests the update_user API endpoint with valid id.
            PUT '/users/<id>'
        """
        response = self.client.put(
            url_for('api.get_user', id=self.user.id),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'username': 'Wizkid'
            })
        )
        response_data = json.loads(response.data)
        profile = response_data.get('profile')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.username, 'Wizkid')
        self.assertEqual(profile.get('username'), 'Wizkid')
        self.assertEqual(response_data.get('bucketlists_url'), url_for('api.get_bucketlists', _external=True))


    def test_update_user_with_invalid_id_forbidden(self):
        """ Tests the update_user API endpoint with invalid id.
            PUT '/users/<id>'
        """
        response = self.client.put(
            url_for('api.get_user', id=243),
            headers=self.get_api_headers(self.access_token),
            data=json.dumps({
                'username': 'Wizkid'
            })
        )
        self.assertEqual(response.status_code, 400)
    

    def test_deregisters_user_with_valid_id(self):
        """ Tests the deregister_user API endpoint with a valid id.
            DELETE '/users/<id>'
        """
        # deregister user :
        response = self.client.delete(
            url_for('api.get_user', id=self.user.id),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('status'), 'deregistered')
        self.assertEqual(response_data.get('registration_url'), url_for('api.register_user', _external=True))
        self.assertEqual(User.query.get(self.user.id), None)

    
    def test_deregister_user_with_invalid_id_forbidden(self):
        """ Tests the deregister_user API endpoint.
            DELETE '/users/<id>'
        """
        response = self.client.delete(
            url_for('api.get_user', id=243),
            headers=self.get_api_headers(self.access_token)
        )
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
