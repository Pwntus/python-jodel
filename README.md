# python-jodel
_Requires Python >= 3.1_

Unofficial [Jodel](https://jodel-app.com/) client written in Python.

The client will work _"out of the box"_, meaning that you do not need to find your own access token!
Every API request will also check if the access token has expired and update it if necessary.

During client initialization a configuration file `pj_config` is either read or written with the current configuration for the client.
The client will re-use this configuration if it exists.

## Usage
```python
>>> python import python_jodel
>>> location = {lat = 78.089409, lng = 15.525395, city = 'Svalbard'}

>>> client = python_jodel.Client(location)

>>> # Setting / changing the location after initialization
>>> client.set_location({lat = 60.165998, lng = 24.939687, city = 'Helsinki', country = 'Finland', name = 'Helsinki'})
```

## Client methods
Every call will return a (HTTP status code, response text) tuple.

```python
>>> client.set_location({location['lat'], location['lng'], location['city'], country = None, name = None})
>>> client.post(message = None, color = None)
>>> client.delete_post(post_id)
>>> client.get_posts_recent(skip = None, limit = 60, mine = False)
>>> client.get_posts_discussed(skip = None, limit = 60, mine = False)
>>> client.get_posts_popular(skip = None, limit = 60, mine = False)
>>> client.get_post(post_id)
>>> client.vote_up(post_id)
>>> client.vote_down(post_id)
>>> client.get_karma()
>>> client.get_user()
```