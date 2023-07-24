## Digester
### A Dockerized news digest creation microservice

A backend app with a couple of endpoints to create news digests, created using Django and DRF. Includes the app itself, and 3 parsers for various:
- IXBT. Works using two requests - to get the news and to count popularity based on number of comments (normalized by time, since generally the older the news is, the more comments it gets)
- Lenta. Works except for popularity and correct tags.
- RBC. Works except for the popularity.

When it updates the news, it automatically creates tags that are not in the database, which can then be added to user's interests if desired. The app creates a news digest based on various factors:
- News popularity. Currently, only the news with popularity above average are included.
- Only news from subscriptions.
- Only news with tags within the user's interests.

After creating a new digest, the app sends a message to the 'parser' RabbitMQ queue with a relative link to an endpoint with the digest, to be used by the frontend.

The app connects to an SQLite database since we're currently not planning any sort of high loads, however, a switch to PostgreSQL can be done easily if needed. 

### Installation

There're *three ways* to get to know this project better.

#### 1) Take a look

Its latest version is already running on an AWS server by the URL http://ondeletecascade.ru:8000/api/ and every action can be performed there. The instance will keep running for some time, but no guarantees on how long it will last.

You can also copy the project and run it on your PC or server:

```
git clone https://github.com/holohup/can_do.git && cd can_do/backend
```
After that, there're two options:

#### 2) Run in a Docker container

```
git clone https://github.com/holohup/digester.git && cd digester && mv .env.sample .env && docker-compose build && docker-compose up -d && docker-compose exec -it -u root digester_api sh ./init.sh 
docker build . -t can_do && docker run -d -p 8000:8000 --name can_do can_do && docker exec -it -u root $(docker ps -aqf "name=^can_do$") sh ./init.sh
```

These commands build a Docker image, run it, apply migrations, collect static files and preload fixtures for the project to become more substantial right away.

#### 3) Set up a Python virtual environment and launch the test server.

```
python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py loaddata fixtures/initial.json && cp .env.sample .env && python manage.py runserver
```

> *If you don't want the fixtures to be preloaded, skip the **loaddata** command. Then you would need to create an admin*:

```
python manage.py createsuperuser
```

**That's it!** After either step, the **Can Do API** will become available by the address http://127.0.0.1:8000/api/. From here on, the API links will be provided to this address, however, feel free to use the *ondeletecascade*.ru version.

### Usage

The Django admin panel is located at http://127.0.0.1:8000/admin/. The preloaded fixtures provide two already registered users:

**admin** / **admin** (an admin :)
**leo** / **shmleoleo** (an ordinary user)

If you have skipped the fixture preloading, create an admin and a user of your choice using the Django admin, or the new user registration endpoint: http://127.0.0.1:8000/api/auth/users/. It requires a simple JSON:
```json
{
    "username": "alexey",
    "password": "shmalexei"
}
```
If everything went **OK** and the password was not too short and didn't look at all like the username, you'll get the user registration confirmation:
```json
{
    "email": "",
    "username": "alexey",
    "id": 3
}
```
You would also need a JWT Token. Send the same username/password JSON combo POST request to http://127.0.0.1:8000/api/auth/jwt/create/ and you'll receive a response that looks similar to:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4OTMxNzczNCwiaWF0IjoxNjg5MjMxMzM0LCJqdGkiOiI4ZDVmYTAxZTc3OGI0Yjc1YmYxYjY3MjMwYzZlMTEzZiIsInVzZXJfaWQiOjN9.eFH82eZvzNtbBUpKaXAoXltdFb3w_jOcVdU7U3rXbhc",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjkxODIzMzM0LCJpYXQiOjE2ODkyMzEzMzQsImp0aSI6IjczMzkwOTJhZDdlNDRmYWY5ZDczYzRjZWJmZGMwN2EzIiwidXNlcl9pZCI6M30.koJbtDboe8fQsqQNgY_LyHZsi4fqJ2cWdwRHBvAu2Us"
}
```
Now copy the "access" key to your favorite program (I use **Postman** and highly recommend it) to use it (**Bearer** in the headers) and enjoy the API.


### Endpoints

#### Create a new todo item

POST to http://127.0.0.1:8000/api/tasks/
```json
{
    "title": "Feed the dog",
    "description": "He likes chicken sausages",
    "done": false
}
```
Only the title field is required, but you can provide extra details in the other fields if you want. The response will contain the new task id.

#### Modify an existing to-do item.

Use the id from the previous step to modify any of the fields, and send a PATCH request with modified JSON from the previous step to http://127.0.0.1:8000/api/tasks/{task_id}

#### Get a list of your tasks.

Since you're authorized via the JWT token, you can get a list of your tasks. Send a GET request to http://127.0.0.1:8000/api/tasks/

You can also get all of your task id's from that list.

#### Get your user info.

Simple information about the authorized user (according to the token) - email, username, and id.
Send a GET request to http://127.0.0.1:8000/api/auth/users/me/

#### Refresh your token

The current token TTL is set to 30 days. If you ever feel the need to refresh it, you need to send a POST request with JSON that looks like this:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4OTMxNzczNCwiaWF0IjoxNjg5MjMxMzM0LCJqdGkiOiI4ZDVmYTAxZTc3OGI0Yjc1YmYxYjY3MjMwYzZlMTEzZiIsInVzZXJfaWQiOjN9.eFH82eZvzNtbBUpKaXAoXltdFb3w_jOcVdU7U3rXbhc"
}
```
Where "refresh" is the key you received when acquired the token. The endpoint is: http://127.0.0.1:8000/api/auth/jwt/refresh/

Then you would need to use the new token provided by the system.


#### Reordering

Here comes the tricky part. There's a special endpoint for reordering items. It accepts a simple JSON with a list of IDs in the new order and reorders the to-do tasks accordingly. Let's say you've got task IDs **1, 2, and 3** (you can get those from the task list endpoint). If you reorder them, they'll come in a new order once you get a new task list. To reorder, send a PATCH request to http://127.0.0.1:8000/api/tasks/reorder/ containing a simple JSON:


```json
{
    "new_order": [3, 1, 2]
}
```
The response either provides the new order, or reports an error (e.g. you tried to include another user's post, or didn't include some of your posts in the new order)

```json
{
    "new_order": [
        3,
        1,
        2,
    ]
}
```

### Final words

#### Ways to improve the app / todo
- If the sources are changed after the digest has been formed, the latest article parsed attribute will tell lies, since now it relies on user's subscriptions. Change to maximum from already parsed sources and make an attribute that tells when the source has been parsed last.
- Migrate to source relative popularity instead of overall popularity by all sources, since that what the Source model has been made for, come up with a **brilliant** query to decrease the number of db interactions.
- Introduce a duplicate filter in case different sources have the same or a similiar article, in order to only get one of them in a digest.
- Cache average popularity from a source, latest article timestamp.
- Error handling on serialization/deserialization, parser class selection, data retrieval, text parsing.
- Tinker with **meaningcloud** or some other text analyzing API with Python SDK to automatically add tags to texts from sources which do not provide tags.
- DB Cleaner for old news that didn't go into any digest for some period of time (a month perhaps?)
- Make an abstract parser class with abstractmethods - take common logic to common methods.
- Make Django admin more beautiful using inlines, query searches, etc, optimize queries.
- Make endpoints for subscriptions management, interests, tags
- Implement some kind of authentication (JWT?)
- Place business logic to a single place :(
- Pagination / filtering when a number of digests grows




