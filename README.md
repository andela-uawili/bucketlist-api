
# BucketList API [![Build Status](https://travis-ci.org/andela-uawili/bucketlist-api.svg)](https://travis-ci.org/andela-uawili/bucketlist-api) [![Coverage Status](https://coveralls.io/repos/andela-uawili/bucketlist-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/andela-uawili/bucketlist-api?branch=master)
Flask API for a bucket list service.

The service allows users to create and manage one or more bucket lists. The API is RESTful and uses Token-based Authentication (JWT) to secure the public resource endpoints from unauthorized parties. The MIME-type for content transfer on the the service is ```application/json```.



## Endpoints
All endpoints must be prefixed by ```/api/:version/``` where ```:version``` represents the API version in use. For example, in the API v1, the login endpoint would be ```/api/v1/auth/login```.

The available endpoints are listed below:

EndPoint |Functionality|Public Access
---------|-------------|--------------
POST /auth/register|Registers a new user on the service|TRUE
POST /auth/login|Logs a user in|TRUE
GET /auth/logout/:id|Logs out this user|FALSE
GET /user/|Get the profile of this user|FALSE
PUT /user/|Update the profile of this user|FALSE
DELETE /user/|Delete this user account|FALSE
POST /bucketlists/|Create a new bucket list|FALSE
GET /bucketlists/|List all the created bucket lists|FASLE
GET /bucketlists/:id|Get single bucket list (along with it's items)|FALSE
PUT /bucketlists/:id|Update this bucket list|FALSE
DELETE /bucketlists/:id|Delete this single bucket list|FALSE
POST /bucketlists/:id/items/|Create a new item in bucket list|FALSE
PUT /bucketlists/:id/items/:item_id|Update a bucket list item|FALSE
DELETE /bucketlists/:id/items/:item_id|Delete an item in a bucket list|FALSE



## Resources


#### Auth:

__POST /auth/register__  |  Register a user   
Parameters/Input data: ```{ "username":"<username[optional]>", "email":"<email>", "password":"<password>"}```   
Response data (if successful) contains the ```username``` and the ```login_url```

__POST /auth/login__  |  Logs in a user    
Parameters/Input data: ```{ "email":"<email>", "password":"<password>"}```   
Response data contains user's ```profile``` and ```access_token``` for use in the ```Authorization``` header of subsequent requests to other endpoints.  

__GET /auth/logout/:id__ |  Logs out this user   
Parameters/Input data: :id URL parameter, represents the id of the currently logged in user.   
Logs user with :id out and returns the ```login_url```   


#### User:

__GET /user/__  | Get this user's profile   
Parameters/Input data: none    
Response data contains the user's ```profile``` and their ```bucketlists_url```   

__PUT /user/__  | Update this user's profile   
Parameters/Input data: none   
Response data contains the user's updated ```profile``` and their ```bucketlists_url```   

__DELETE /user/__  | Deregisters the user   
Parameters/Input data: none    
Response data contains the deletion ```status``` and the ```registration_url```   


#### Bucket List:

__POST /bucketlists/__  |  create a new bucketlist     
Parameters/Input data: ```{"name":"name/title of bucketlist"} ```   
Response data contains the created ```bucketlist``` and the ```bucketlists_url```   

__GET /bucketlists/__ |  List all the bucket lists created by this user    
Parameters/Input data: none  
Response data contains the ```bucketlists```    

__GET /bucketlists/:id__ |  Get single bucket list     
Parameters/Input data: :id URL parameter, represents the id of the bucketlist.   
Response data contains the ```bucketlist``` (items included) and the ```bucketlists_url```     

__PUT /bucketlists/:id__ |  Update this bucket list     
Parameters/Input data:  
:id URL parameter, represents the id of the bucketlist.   
```{"name":"my bucketlist item", "Done":false } ```   
Response data contains the updated ```bucketlist``` and the ```bucketlists_url```    

__DELETE /bucketlists/:id__ |  Delete this bucket list     
Parameters/Input data: :id URL parameter, represents the id of the bucketlist.   
Response data contains the user's deletion ```status``` and the ```registration_url```   


#### Bucket List Item: 

__POST /bucketlists/:id/items/__ | Create a new item in bucket list   
Parameters/Input data: ```{"name":"my bucketlist item", "done":false } ```   
Response data contains the created ```bucketlist_item``` and the current ```bucketlist_url```   

__PUT /bucketlists/:id/items/:item_id__ | Update a bucket list item   
Parameters/Input data:   
:id URL parameter, represents the id of the bucketlist.   
:item_id URL parameter,represents the id of the bucketlist item.   
``` {"name":"update my bucketlistitem", "done":true } ```   
Response data contains the updated ```bucketlist_item``` and the current```bucketlist_url```  

__DELETE /bucketlists/:id/items/:item_id__ | Delete an item in a bucket list   
Parameters/Input data:   
:id URL parameter, represents the id of the bucketlist.   
:item_id URL parameter,represents the id of the bucketlist item.  
Response data contains the deletion ```status``` and the current```bucketlist_url``` 

**__NOTE:__** All non-public access endpoints can only be accessed with an authentication token set in the ```Authorization``` header of the request. This token is found in the response when a user successfully logs in. The token value set in Authorization header must begin with the JWT prefix as shown:   
```JWT <access_token>```   
Remember the single space between the prefix and token.   


## Other Features


#### Search
User can search for bucketlists by appending the ```q``` querystring parameter to the ```GET /bucketlists/``` endpoint url. 
For example to search for bucketlists with the word Kilimanjaro:   
``` GET /bucketlists/?q=kilimanjaro ```    
The search feature is not case sensitive.   


#### Pagination
User can also limit the number of results returned in a page of bucket lists or bucket list items by appending the ```limit``` and or ```page``` to relevant endpoint urls. For example   
```GET /bucketlists/?limit=5&page=3``` or   
```GET /bucketlists/:id/?page=1```   
The default limit is 20, the maximum is 100 and default page number is 1. 

**__NOTE:__** Also the search and pagination parameters can be used together on the same resource result set.



### Sample Request Response
```
$ curl -u young: GET http://localhost:5000/api/v1.0/bucketlists/1?limit=2&page=1
HTTP/1. 0 200 OK
Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDQ2MTQwNzM5LCJuYmYiOjE0NDYxNDA3MzksImV4cCI6MTQ0NjE0NDMzOX0A00pbgY-3UGUXNwlAnZNu9UfI8su7e_hsiwcU6SjLH4
Content-Type: application/json
Content-Length: 976
Cache-Control: no-cache
Server: Werkzeug/0. 8. 3 Python/2. 7. 3
Date: Thu, 29 October 2015 07: 36: 22 GMT

{
  "bucketlist": {
  	"id": 1,
    "name": "The Melancholic Bucketlist",
    "date_created": "2015-10-24 22:07:22",
    "date_modified": "2015-10-29 12:23:40",
    "item_count": 3,
    "items": [
      {
      	"id": 1,
        "name": "Wake up on mount everest!",
        "date_created": "2015-10-24 23:41:03",
        "date_modified": "2015-10-24 23:41:03",
        "done": true
      },
      {
        "id": 2,
        "name": "Kayak across the Atlantic!",
        "date_created": "2015-10-24 23:41:03",
        "date_modified": "2015-10-24 23:41:03",
        "done": false
      }
    ],
    "created_by": {
      "url": "http://localhost:5000/api/v1.0/users/1",
      "username": "Toby Ogunsanya"
    },
    "url": "http://localhost:5000/api/v1.0/bucketlists/1"
  },
  "bucketlists_url": "http://localhost:5000/api/v1.0/bucketlists/",
  "current_page": 1,
  "next_url": "http://localhost:5000/api/v1.0/bucketlists/1?limit=2&page=2",
  "prev_url": null,
  "total": 3
}

```


## Usage

#### Installation
1. Install all the package dependencies in your python setup or virtual environment.   
``` pip install -r requirements.txt ```   

2. Run the database creation and migration commands:   
``` python manage.py db init ```   
``` python manage.py db migrate ```   
``` python manage.py db upgrade ```   

#### Running the Server
``` python manage.py runserver ```   

#### Testing
* To run tests:  
``` python manage.py test ``` 

* For the coverage report:    
  1. ``` coverage run --source=app manage.py test ```   
  2. ``` coverage report ```   


