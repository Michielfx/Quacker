import datetime
import operator


def pop_at_acc(ctx, tweet):
    # Noah is working on this

    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

    # You can mention more than one person per tweet
    for mention in (tweet["entities"]["user_mentions"]):
        # If the key doesn't exist we initialize it at 1 otherwise increment it
        try:
            ctx.pop_dic[mention["screen_name"]] += 1
        except:
            ctx.pop_dic[mention["screen_name"]] = 1

        # We keep track of the increments name+time so that we can decrement after a day has passed
        ctx.pop_rem.append([mention["screen_name"], time])

    # We go through all the stored tweets, if any are older than one day we decrement and remove it from the list
    for i, old_tweet in enumerate(ctx.pop_rem):
        diff = time - old_tweet[1]
        if diff.days > 0:
            ctx.pop_dic[old_tweet[0]] -= 1  # This decrements the value
            ctx.pop_rem = ctx.pop_rem[1:]  # This removes the tweet from the list
        else:
            break  # Since the list is ordered from oldest to newest we can stop when tweets are younger than 1 day

    # We need to sort+reverse the dict to get the top 10 most common accounts
    sort = sorted(ctx.pop_dic.items(), key=operator.itemgetter(1), reverse=True)
    return sort[:10]  # We return the first 10 elements


