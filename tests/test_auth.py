import unittest
import json
from flask import current_app, url_for
from app import create_app, db
from app.models import User


class AuthenticationTestCase(unittest.TestCase):
    """ Testcase for the Authentication related API endpoints 
    """

    def setUp(self):

        # setup the app and push app context:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # setup the db:
        db.create_all()

        # create test user:
        user = User(
            username="Somebody", 
            email="somebody@somedomain.com",
            password="anything"
        )
        db.session.add(user)
        db.session.commit()

        # init the test client:
        self.client = self.app.test_client()


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
    

    def test_user_can_register_with_username(self):
        """ Tests user registration specifying username.
            POST '/auth/register'
        """
        response = self.client.post(
            url_for('api.register_user'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'username': 'Lagbaja', 
                'email':'lagbaja@somedomain.com',
                'password': 'nothing',
            })
        )
        response_data = json.loads(response.data) 
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data.get('username'), "Lagbaja")
        self.assertIn( url_for('login'), response.data)


    def test_user_can_register_without_username(self):
        """ Tests user registration without specifying username.
            POST '/auth/register'
        """
        response = self.client.post(
            url_for('api.register_user'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email':'wizkid@somedomain.com',
                'password': 'something',
            })
        )
        response_data = json.loads(response.data) 
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data.get('username'), "wizkid@somedomain.com")
        self.assertIn( url_for('login'), response.data)


    def test_register_user_without_password_forbidden(self):
        """ Tests user registration without specifying password.
            POST '/auth/register'
        """
        response = self.client.post(
            url_for('api.register_user'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email':'wizkid@somedomain.com',
            })
        )
        response_data = json.loads(response.data) 
        self.assertEqual(response.status_code, 400)


    def test_register_user_with_registered_email_forbidden(self):
        """ Tests user registration with existing email forbidden.
            POST '/auth/register'
        """
        response = self.client.post(
            url_for('api.register_user'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email':'somebody@somedomain.com',
                'password': 'something',
            })
        )
        response_data = json.loads(response.data) 
        self.assertEqual(response.status_code, 403)


    def test_registered_user_login(self):
        """ Tests user login for registered.
            POST '/auth/login'
        """
        response = self.client.post(
            url_for('login'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email': 'somebody@somedomain.com',
                'password': 'anything',
            })
        )
        response_data = json.loads(response.data) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('profile').get('email'), 'somebody@somedomain.com')
        self.assertEqual(response_data.get('bucketlists_url'), url_for('api.get_bucketlists', _external=True))
        self.assertNotEqual(response_data.get('access_token'), None)


    def test_unregistered_user_login_forbidden(self):
        """ Tests user login for unregistered is not allowed.
            POST '/auth/login'
        """
        response = self.client.post(
            url_for('login'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email': 'unregistered@somedomain.com',
                'password': 'somerandompassword',
            })
        )
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)


    def test_user_logout(self):
        """ Tests logout for a logged in user.
            GET '/auth/logout'
        """
        # log in a registered user:
        response = self.client.post(
            url_for('login'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email': 'somebody@somedomain.com',
                'password': 'anything',
            })
        )
        response_data = json.loads(response.data) 
        access_token = response_data.get('access_token')
        id = response_data.get('profile').get('id')
        user = User.query.get(id)

        # log the user out
        response = self.client.get(
            url_for('api.logout'),
            headers=self.get_api_headers(access_token=access_token)
        )
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('status'), 'logged out')
        self.assertEqual(response_data.get('login_url'), url_for('login', _external=True))

        # check that the user is actually logged out:
        self.assertFalse(user.logged_in)
    

    def test_login_protection_logout_roundtrip(self):
        """ Tests auth protection during the login logout roundtrip.
        """
        # try to access a resource without token:
        response = self.client.get(
            url_for('api.get_bucketlists'),
            headers=self.get_api_headers()
        )
        self.assertEqual(response.status_code, 401)

        # log in a registered user:
        response = self.client.post(
            url_for('login'),
            headers=self.get_api_headers(),
            data=json.dumps({
                'email': 'somebody@somedomain.com',
                'password': 'anything',
            })
        )
        response_data = json.loads(response.data) 
        access_token = response_data.get('access_token')
        id = response_data.get('profile').get('id')
        user = User.query.get(id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.logged_in)

        # try to access the same resource with token:
        response = self.client.get(
            url_for('api.get_bucketlists'),
            headers=self.get_api_headers(access_token=access_token)
        )
        self.assertEqual(response.status_code, 200)

        # log the user out
        response = self.client.get(
            url_for('api.logout'),
            headers=self.get_api_headers(access_token=access_token)
        )
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user.logged_in)

        # try to access the same resource with token:
        response = self.client.get(
            url_for('api.get_bucketlists'),
            headers=self.get_api_headers(access_token=access_token)
        )
        self.assertEqual(response.status_code, 401)

        # log the user out again to test exception
        response = self.client.get(
            url_for('api.logout'),
            headers=self.get_api_headers(access_token=access_token)
        )
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)



if __name__ == '__main__':
    unittest.main()