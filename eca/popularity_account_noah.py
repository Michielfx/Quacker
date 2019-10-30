


def pop_at_acc(ctx, tweet):
    # Noah is working on this
    for mention in (tweet["entities"]["user_mentions"]):
        try:
            ctx.pop_dic[mention["screen_name"]] += 1
        except:
            ctx.pop_dic[mention["screen_name"]] = 1

