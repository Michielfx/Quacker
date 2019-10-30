from eca import *

import random
from eca.generators import start_offline_tweets
import datetime
import textwrap
from popularity_account_noah import *


## You might have to update the root path to point to the correct path
## (by default, it points to <rules>_static)
# root_content_path = 'template_static'


# binds the 'setup' function as the action for the 'init' event
# the action will be called with the context and the event
@event('init')
def setup(ctx, e):
    ctx.count = 0

    # Noah Values:
    ctx.pop_dic = {}
    # ----------------------------

    start_offline_tweets('data/xfactor.txt', 'tweets', time_factor=1000)


@event('tweets')
def tweet(ctx, e):
    # we receive a tweet
    tweet = e.data

    # ----------------------------
    # Noah is working on this
    pop_at_acc(ctx, tweet)
    # ----------------------------

    # parse date
    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

    # nicify text
    text = textwrap.fill(tweet['text'],initial_indent='    ', subsequent_indent='    ')

    # generate output
    output = "[{}] {} (@{}):\n{}".format(time, tweet['user']['name'], tweet['user']['screen_name'], text)
    emit('tweets', tweet)



