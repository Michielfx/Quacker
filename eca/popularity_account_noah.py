import datetime
import operator


def pop_at_acc(ctx, tweet):
    # Noah is working on this

    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    for mention in (tweet["entities"]["user_mentions"]):
        try:
            ctx.pop_dic[mention["screen_name"]] += 1
        except:
            ctx.pop_dic[mention["screen_name"]] = 1

        ctx.pop_rem.append([mention["screen_name"], time])

    #print(ctx.pop_rem)
    for i, old_tweet in enumerate(ctx.pop_rem):
        diff = time - old_tweet[1]
        if diff.days > 0:
            ctx.pop_dic[old_tweet[0]] -= 1
            ctx.pop_rem = ctx.pop_rem[1:]
        else:
            break

    sort = sorted(ctx.pop_dic.items(), key=operator.itemgetter(1), reverse=True)
    return sort[:9]


