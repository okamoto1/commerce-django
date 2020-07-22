from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.urls import reverse

from .functions import watchlist_items, actual_bid, seller_or_buyer, details_and_comments, declare_winner
from .forms import Listing_Form, BidForm, CommentsForm, CategoryForm

from .models import User, Auction, Bids, Comments, Watchlist, Category


def index(request):
    active_auctions = Auction.objects.filter(active = True).order_by('-date')
    if request.user.is_authenticated:
        return render(request, "auctions/index.html", {
            'all_auctions': active_auctions,
            'watchlist': watchlist_items(request.user),
        })
    return render(request, "auctions/index.html", {
        'all_auctions': active_auctions,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_list(request):
    if request.method == "POST":
        form = Listing_Form(request.POST, request.FILES)
        if form.is_valid():
            #create auction
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            init_bid = form.cleaned_data["init_bid"]
            image = request.FILES['image']
            seller = request.user
            listing = Auction.objects.create(
                seller = seller,
                item = title,
                description = description,
                min_bid = init_bid,
                image = image
            )
            #select category
            category_name = request.POST["category"]
            if category_name != 'Select a category':
                category = Category.objects.get(category = category_name)
                listing.selectcategory.add(category)
            return HttpResponseRedirect(reverse('index'))
    return render(request, "auctions/new-listing.html", {
        "form": Listing_Form(),
        "categories": Category.objects.all().order_by('category')
    })


def category(request):
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all().order_by('category'),
        "form": CategoryForm()
    })

def show_category_items(request, title):
    category = Category.objects.get(category = title)
    items = category.category_items.all()
    return render(request, "auctions/category-item.html",{
        "category": category,
        "items": items,
        'watchlist': watchlist_items(request.user),
    })

@login_required
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category"]
            if Category.objects.filter(category = category_name):
                message = 'Category already exist'
                return render(request, "auctions/category.html", {
                    "categories": Category.objects.all(),
                    "message": message,
                    "form": CategoryForm()
                })
            else:
                create_category = Category.objects.create(
                    category = category_name.capitalize()
                )
    return HttpResponseRedirect(reverse("category"))

def items_page(request, title, id):
    user_type = seller_or_buyer(id, request.user)
    item_stuff = details_and_comments(id)
    if not Auction.objects.get(id = id).active:
        winner = declare_winner(id, request.user)
        if winner == request.user:
            return render(request, "auctions/items-page.html", {
                "BidForm": BidForm(),
                "CommentForm": CommentsForm(),
                "value": actual_bid(id),
                "comments": item_stuff['comments'],
                "items": item_stuff['details'],
                "log_bids": user_type['log_bids'],
                "edit" : user_type['edit'],
                "winner": winner
            })
    return render(request, "auctions/items-page.html", {
        "BidForm": BidForm(),
        "CommentForm": CommentsForm(),
        "value": actual_bid(id),
        "comments": item_stuff['comments'],
        "items": item_stuff['details'],
        "log_bids": user_type['log_bids'],
        "edit" : user_type['edit'],
    })

@login_required
def adding_comment(request, title, id):
    filter = Auction.objects.get(id = id)
    if request.method == "POST":
        form = CommentsForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comentarios"]
            Comments.objects.create(
                usuario = request.user,
                comentarios = comment,
                item_id = filter
            )
    return HttpResponseRedirect(reverse("items_page", args=(title, id,)))

@login_required
def adding_bid(request, title, id):
    filter = Auction.objects.get(id = id)
    item_stuff = details_and_comments(id)
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid_value = form.cleaned_data["bid_value"]
            if bid_value <= actual_bid(id):
                return render(request, "auctions/items-page.html", {
                    "BidForm": BidForm(),
                    "CommentForm": CommentsForm(),
                    "value": actual_bid(id),
                    "comments": item_stuff['comments'],
                    "items": item_stuff['details'],
                    "message" : 'Invalid value'
                })
            else:
                Bids.objects.create(
                    buyer = request.user,
                    bid_value = bid_value,
                    item_id = filter,
                )
    return HttpResponseRedirect(reverse("items_page", args=(title, id,)))

@login_required
def add_watchlist(request, id):
    query = Auction.objects.get(pk = id)
    Watchlist.objects.create(usuario = request.user, item_id = query)
    return HttpResponseRedirect(reverse("index"))

@login_required
def remove_watchlist(request, id):
    query = Watchlist.objects.filter(item_id = id).delete()
    return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    show_favitems = Watchlist.objects.filter(usuario = request.user)
    if show_favitems:
        return render(request, "auctions/watchlist.html", {
            'saved_items': show_favitems
        })
    else:
        return render(request, "auctions/watchlist.html", {
            'mensagem': 'Empty'
        })

@login_required
def close_auction(request, id):
    update_status = Auction.objects.filter(id = id).update(active = False)
    return HttpResponseRedirect(reverse("index"))
