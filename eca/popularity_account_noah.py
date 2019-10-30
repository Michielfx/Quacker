


def pop_at_acc(ctx, tweet):
    # Noah is working on this
    for mention in (tweet["entities"]["user_mentions"]):
        print(mention["screen_name"])

