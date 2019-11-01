from eca import *

import random
from profanity_check import predict, predict_prob
from langdetect import detect
from eca.generators import start_offline_tweets
from textblob import TextBlob
import datetime
import textwrap
from popularity_account_noah import *
from collections import *
import operator


## You might have to update the root path to point to the correct path
## (by default, it points to <rules>_static)
# root_content_path = 'template_static'


# binds the 'setup' function as the action for the 'init' event
# the action will be called with the context and the event
@event('init')
def setup(ctx, e):
    ctx.count = 0

    # Noah Values:
    ctx.pop_dic = {}  # Keeps track of how often each account is mentioned
    ctx.pop_rem = []  # Keeps track of account values that need to be decremented
    # ----------------------------

    #Giel Values:
    ctx.p_sent = 0
    ctx.n_sent = 0
    ctx.sent_dict = defaultdict(list)
    ctx.ctry_dict = {}
    ctx.ctry_tweet_list = []

    start_offline_tweets('data/xfactor.txt', 'tweets', time_factor=1000)


@event('tweets')
def tweet(ctx, e):
    # we receive a tweet
    tweet = e.data

    # ----------------------------
    # Noah is working on this
    emit('account', {
        'action': 'update',
        'value': pop_at_acc(ctx, tweet)})

    # ----------------------------

    # parse date
    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

    # nicify text
    text = textwrap.fill(tweet['text'],initial_indent='    ', subsequent_indent='    ')
    
    #VIEWERMOOD
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
    # emit to outside world
    if len(ctx.sent_dict.get('tweets')) > 15:
        emit('mood',{
             'mood_value': ctx.sent_dict.get('norms')})

    #PBC (popularity by country)
    #defining current country
    cur_country = tweet.get('place').get('country')
    #if current current not yet in country dictionary, give it value 1
    if cur_country not in ctx.ctry_dict:
        ctx.ctry_dict[cur_country] = 1
    #otherwise increase the value of the country by 1
    else:
    	ctx.ctry_dict[cur_country] += 1
    #appending time and current country as a tuple to the list
    ctx.ctry_tweet_list.append((time,cur_country))
    #whenever a tweet in the ctx.ctry_tweet_list is more than a month old 
    #the (time, country) tuple is removed and the counter for that country in the ctx.ctry_dict is decreased by 1
    while (time-ctx.ctry_tweet_list[0][0]).total_seconds() > (30*24*60*60):
        oldest_country= ctx.ctry_tweet_list[0][1]
        ctx.ctry_dict[oldest_country] -= 1
        ctx.ctry_tweet_list = ctx.ctry_tweet_list[1:]
    #creating a list for the 5 most popular country, sorted by the counntry counter in the dict
    sorted_dict = sorted(ctx.ctry_dict.items(), key=operator.itemgetter(1))[::-1][:5]
    #top5 countries of the the sorted_dict
    top5 = [tup[0] for tup in sorted_dict]
    #emiting a list of up to 5 countries order in popularity from left to right
    emit('ctry_pop',{
         'ctry_value': top5})
    

    # generate output
    # output = "[{}] {} (@{}):\n{}".format(time, tweet['user']['name'], tweet['user']['screen_name'], text)
    if predict_prob([tweet['text']]) < 0.6:
        isProfane = False
    else:
        isProfane = True

    if detect(tweet['text']) == 'en':
        isEnglish = True
    else:
        isEnglish = False

    tweet['isProfane'] = isProfane
    tweet['isEnglish'] = isEnglish
    emit('tweets', tweet)

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
