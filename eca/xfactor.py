from eca import *

import random
from eca.generators import start_offline_tweets
import datetime
import textwrap

## You might have to update the root path to point to the correct path
## (by default, it points to <rules>_static)
# root_content_path = 'template_static'


# binds the 'setup' function as the action for the 'init' event
# the action will be called with the context and the event
@event('init')
def setup(ctx, e):
    ctx.count = 0
    fire('sample', {'previous': 0.0})
    start_offline_tweets('data/xfactor.txt', 'tweets', time_factor=10000)


# define a normal Python function
def clip(lower, value, upper):
    return max(lower, min(value, upper))

@event('sample')
def generate_sample(ctx, e):
    ctx.count += 1
    if ctx.count % 50 == 0:
        emit('debug', {'text': 'Log message #'+str(ctx.count)+'!'})

    # base sample on previous one
    sample = clip(-100, e.data['previous'] + random.uniform(+5.0, -5.0), 100)

    # emit to outside world
    emit('sample',{
        'action': 'add',
        'value': sample
    })
    
    # chain event
    fire('sample', {'previous': sample}, delay=0.40)

@event('tweets')
def tweet(ctx, e):
    print("Tweet")
    # we receive a tweet
    tweet = e.data

    # parse date
    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

    # nicify text
    text = textwrap.fill(tweet['text'],initial_indent='    ', subsequent_indent='    ')

    # generate output
    output = "[{}] {} (@{}):\n{}".format(time, tweet['user']['name'], tweet['user']['screen_name'], text)
    emit('tweets', output)