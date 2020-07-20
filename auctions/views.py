from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.urls import reverse
from .forms import Listing_Form, BidForm, CommentsForm, Upload_Image
import datetime

from .models import User, Auction, Bids, Comments, Watchlist


def index(request):
    items_saved = []
    active_auctions = Auction.objects.filter(active = True)
    if request.user.is_authenticated:
        for saved in Watchlist.objects.filter(usuario = request.user):
            items_saved.append(saved.item_id.id)
    return render(request, "auctions/index.html", {
        'all_auctions': active_auctions,
        'watchlist': items_saved,
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


def create_list(request):
    if request.method == "POST":
        form = Listing_Form(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            init_bid = form.cleaned_data["init_bid"]
            seller = request.user
            listing = Auction.objects.create(
                seller = seller,
                item = title,
                description = description,
                min_bid = init_bid
            )
            return render(request, "auctions/items-page.html")
    return render(request, "auctions/new-listing.html", {
        "form": Listing_Form(),
        "image": Upload_Image()
    })


def items_page(request, title, id):
    details = Auction.objects.filter(id = id)
    filter = Auction.objects.get(id = id)
    seller = details.values('seller')
    author = User.objects.filter(pk__in=seller)
    if author[0] == request.user:
        edit = True
        bid = Bids.objects.filter(item_id = filter)
    return render(request, "auctions/items-page.html", {
        "BidForm": BidForm(),
        "CommentForm": CommentsForm(),
        "comments": Comments.objects.filter(item_id = filter),
        "items": details
    })


def upload_image(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()
            fs.save(uploaded_file.name, uploadedfile)
            return HttpResponseRedirect('/success/url/')
        else:
            form = UploadFileForm()
        return render(request, 'upload.html', {'form': form})


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


def adding_bid(request, title, id):
    filter = Auction.objects.get(id = id)
    print(filter.min_bid)
    if request.method == "POST":
        form = BidForm(request.POST, 'teste')
        if form.is_valid():
            bid_value = form.cleaned_data["bid_value"]
            Bids.objects.create(
                buyer = request.user,
                bid_value = bid_value,
                item_id = filter,
                date = datetime.date.today()
            )
    return HttpResponseRedirect(reverse("items_page", args=(title, id,)))

def add_watchlist(request, id):
    query = Auction.objects.get(pk = id)
    Watchlist.objects.create(usuario = request.user, item_id = query)
    return HttpResponseRedirect(reverse("index"))


def remove_watchlist(request, id):
    query = Watchlist.objects.filter(item_id = id).delete()
    return HttpResponseRedirect(reverse("index"))


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


def close_auction(request, id):
    query = Auction.objects.filter(id = id).update(active = False)
    return HttpResponseRedirect(reverse("index"))
