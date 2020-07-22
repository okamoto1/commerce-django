from .models import Watchlist, Auction, Bids, User, Comments


def watchlist_items(user):
    items_saved = []
    for saved in Watchlist.objects.filter(usuario = user):
        items_saved.append(saved.item_id.id)
    return items_saved

def actual_bid(id):
    filter = Auction.objects.get(id = id)
    if Bids.objects.filter(item_id = filter):
        actual_bid = Bids.objects.filter(item_id = filter).latest('bid_value').bid_value
    else:
        actual_bid = filter.min_bid
    return actual_bid

def seller_or_buyer(id, user):
    filter = Auction.objects.get(id = id)
    seller = Auction.objects.filter(id = id).values('seller')
    author = User.objects.filter(pk__in=seller)
    query = Bids.objects.filter(item_id = filter)
    if author[0] == user:
        edit = True
        log_bids = query
    else:
        edit = False
        log_bids = query.count()
    return {'edit': edit, 'log_bids': log_bids}

def details_and_comments(id):
    filter = Auction.objects.get(id = id)
    comments = Comments.objects.filter(item_id = filter)
    details = Auction.objects.filter(id = id)
    return {'comments': comments, 'details': details}

def declare_winner(id, user):
    filter = Auction.objects.get(id = id)
    query = Bids.objects.filter(item_id = filter)
    if query:
        winner = query.latest('bid_value').buyer
    else:
        winner = 'There is no winner'
    return winner
