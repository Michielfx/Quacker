import datetime


def pop_at_acc(ctx, tweet):
    # Noah is working on this

    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    for mention in (tweet["entities"]["user_mentions"]):
        try:
            ctx.pop_dic[mention["screen_name"]] += 1
        except:
            ctx.pop_dic[mention["screen_name"]] = 1

        ctx.pop_rem.append([mention["screen_name"], time])

    l = []
    for i, old_tweet in enumerate(ctx.pop_rem):
        diff = time - old_tweet[1]
        if diff.days > 0:
            l.append(i)
            ctx.pop_dic[old_tweet[0]] -= 1

    for i in l:
        del ctx.pop_rem[i]

    #print(ctx.pop_dic)


