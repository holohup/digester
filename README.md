# digester
News sites digest micro service

## todo
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
