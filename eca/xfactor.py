from eca import *

import random
from profanity_check import predict, predict_prob
from langdetect import detect
from eca.generators import start_offline_tweets
import datetime
import textwrap
from popularity_account_noah import *
from collections import *
from textblob import TextBlob


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
    ctx.pop_rem = []
    # ----------------------------

    #Giel Values:
    ctx.p_sent = 0
    ctx.n_sent = 0
    ctx.sent_dict = defaultdict(list)

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

    #GIEL{
    #uses a python extension to determine the sentiment of a text
	#see from textblob import TextBlob, and pip install textblob
    sentiment = get_tweet_sentiment(text)
	#counting positive and negative sentiment tweets while storing them in ctx values
    if sentiment == 'positive':
        ctx.p_sent += 1
    elif sentiment == 'negative':
        ctx.n_sent += 1
	#output data should be in following form: 
	#{'norms':(pos, neg), 'tweets':[(time1,sentiment1), (time2,sentiment2), ..., (timeN,sentimenN)]]
	#where pos and neg are the normalized positive and negative sentiment counters
	#at every every the time of the tweet and its sentiment are stored as a tuple in tweets
    ctx.sent_dict['tweets'].append((time,sentiment))
	#at every incoming tweet (event), remove all tweets in the 'tweets' list in ctx.sent_dict
	#that were sent 10 or more minutes before the incoming tweets. additionally substract the according
	#sentiment counters
    while (time-ctx.sent_dict.get('tweets')[0][0]).total_seconds() > 600:
        oldest_tweet = ctx.sent_dict['tweets'][0]
        if oldest_tweet[1] == 'positive':
            ctx.p_sent -= 1
        elif oldest_tweet[1] == 'negative':
            ctx.n_sent -= 1
        ctx.sent_dict['tweets'] = ctx.sent_dict['tweets'][1:]
    #at every event the normalized values are stored in norms
    ctx.sent_dict['norms'] = norm(ctx.p_sent,ctx.n_sent)
    #printing the dict to show what the output data will look like, however only ctx.sent_dict['norms']
    #is needed for plotting the charts
    # emit to outside world
    if len(ctx.sent_dict.get('tweets')) > 15:
        emit('mood',{
             'action': 'update',
             'value': ctx.sent_dict.get('norms')})
	#}GIEL


    # generate output
    # output = "[{}] {} (@{}):\n{}".format(time, tweet['user']['name'], tweet['user']['screen_name'], text)
    if predict_prob([tweet['text']]) < 0.6 and detect(tweet['text']) == 'en':
        emit('tweets', tweet)

#GIEL{
#normalizing function for positive and negative counters
def norm(a,b):
    if (a,b) == (0,0):
        return (0,0)
    a_norm = a/(a+b)
    b_norm = b/(a+b)
    return (a_norm,b_norm)

#tweet sentiment function using the tweetblob library
def get_tweet_sentiment(tweet): 
    tweetblob = TextBlob(tweet)
    if tweetblob.sentiment.polarity > 0: 
        return 'positive'
    elif tweetblob.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'
#GIEL}
