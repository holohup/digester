## Digester
### A Dockerized news digest creation microservice

A backend app with a couple of endpoints to create news digests, created using Django and DRF. Includes the app itself, and 3 parsers for various:
- IXBT. Works using two requests - to get the news and to count popularity based on the number of comments (normalized by time, since generally, the older the news is, the more comments it gets)
- Lenta. Works except for popularity and correct tags.
- RBC. Works except for the popularity.

When it updates the news, it automatically creates tags that are not in the database, which can then be added to the user's interests if desired. The app creates a news digest based on various factors:
- News popularity. Currently, only the news with popularity above average is included.
- Only news from subscriptions.
- Only news with tags within the user's interests.

After creating a new digest, the app sends a message to the 'parser' RabbitMQ queue with a relative link to an endpoint with the digest, to be used by the frontend.

The app connects to an SQLite database since we're currently not planning any sort of high loads, however, a switch to PostgreSQL can be done easily if needed. The app is provided with some preinstalled fixtures (optional, but highly recommended): a user, some news, tags, subscriptions, sources, and a digest.

### Installation

There're *three ways* to get to know this project better.

#### 1) Take a look

Its latest version is already running at http://ondeletecascade.ru:5001/ and every action can be performed there, the fixtures are preloaded. The instance will keep running for some time, but no guarantees on how long it will last.

You can also copy the project and run it on your PC or server:

```
git clone https://github.com/holohup/digester.git && cd digester && mv .env.sample .env
```
After that, there're two options:

#### 2) Run in a Docker container

```
docker-compose build && docker-compose up -d && docker exec -it -u root $(docker ps -aqf "name=^digester_api$") sh ./init.sh
```
(from the digester directory)

These commands build a Docker image, run it, and apply migrations and preload fixtures for the project to immediately become more substantial.

#### 3) Set up a Python virtual environment and launch the test server.

```
echo "RABBITMQ_URL=\"amqp://guest:guest@localhost:5672\"" >>.env && python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py loaddata fixtures/init.json && python manage.py runserver 0:5001
```

Launch another two terminals and execute the commands in each:
```
source venv/bin/activate && celery -A digester worker -l debug
```

```
docker run -p 5672:5672 -p 15672:15672 rabbitmq:3.10.25-management-alpine
```

> *If you don't want the fixtures to be preloaded in either of those ways, skip the **loaddata** command. Then you would need to create an admin*:

```
python manage.py createsuperuser
```

**That's it!** After either step, the **Digester** will become available by the address http://127.0.0.1:5001/api/. From here on, the API links will be provided to this address, however, feel free to use the *ondeletecascade*.ru version.

### Usage

1) Edit Sources. In the admin panel, you can add as many sources as you wish. However, in order to work properly, they need to have a Parser Class provided. The fixtures include currently working parsers, but feel free to write your own. The parser should receive a time-aware timestamp upon activation to look only for the news, it should provide a method parse() and return the result in a .result property or variable.
2) Edit subscriptions. In order to parse the sources, add the subscription to the user of your choice.
3) Interests can be edited in Django admin on the user's page.

The Django admin panel is located at http://127.0.0.1:5001/admin/. The preloaded fixtures provide an already registered user:

**admin** / **admin** (an admin :)

If you have skipped the fixture preloading, create an admin and a user of your choice using the command:
```
python manage.py createsuperuser
```

### Endpoints

#### Start digest creation

GET to http://127.0.0.1:5001/api/generate/<user_id> (which is 1 in fixtures - if you have preloaded them, the URL would be http://127.0.0.1:5001/api/generate/1/). The request can be done in a browser.

You'll get a response with the id of a digest being generated, something like:
```json
{
    "message": "Digest creation has started. Digest id = 5"
}
```

Use this id to fetch the digest when it's ready.

#### Get the digest.

Use the id from the previous step to send a GET to http://127.0.0.1:5001/api/digest/{task_id}.
Fair warning - if no new news matches the default criteria, an empty digest will still be there, but the message sent to RabbitMQ will inform about this. If there's news in the digest, you'll receive a response similar to:
```json
{
    "id": 5,
    "posts": [
        {
            "text": "text1",
            "link": "link1"
        },
        {
            "text": "text2",
            "link": "link2"
        },
    ],
    "created_at": "2023-07-24T08:50:08.841000Z"
}
```
You can view an example at http://ondeletecascade.ru:5001/api/digest/5/

#### Get a list of digests.

http://127.0.0.1:5001/api/digest/


### Final words

#### Ways to improve the app/todo
- If the sources are changed after the digest has been formed, the latest article parsed attribute will tell lies, since now it relies on the user's subscriptions. Change to maximum from already parsed sources and make an attribute that tells when the source has been parsed last
- Migrate to source relative popularity instead of overall popularity by all sources, since that is what the Source model has been made for, and come up with a **brilliant** query to decrease the number of db interactions
- Introduce a duplicate filter in case different sources have the same or a similar article, in order to only get one of them in a digest
- Cache average popularity from a source, latest article timestamp
- Error handling on serialization/deserialization, parser class selection, data retrieval, and text parsing
- Tinker with **meaningcloud** or some other text analyzing API with Python SDK to automatically add tags to texts from sources that do not provide tags
- DB Cleaner for old news that didn't go into any digest for some period of time (a month perhaps?)
- Make an abstract parser class with abstract methods - take common logic to common methods
- Make Django admin more beautiful using inlines, query searches, etc, and optimize queries
- Make endpoints for subscriptions management, interests, tags
- Implement some kind of authentication (JWT?)
- Place business logic in a single place
- Pagination/filtering when a number of digests grows
- Increase test coverage
