import python_jodel

client = python_jodel.Client()

# Get client karma
response = client.get_karma()
if response[0] != 200:
	print('Something went wrong while fetching karma')
else:
	print('Client karma: %d\n\n' % response[1]['karma'])

# Fetch 10 most recent posts
response = client.get_posts_recent(limit = 10)

if response[0] != 200:
	print('Something went wrong while fetching recent posts')
else:
	for post in response[1]['posts']:
		print('[Date: %s, ID: %s, vote count: %d]\n%s\n\n' % (post['created_at'], post['post_id'], post['vote_count'], post['message']))
