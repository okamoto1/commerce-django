from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Auction)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)
admin.site.register(Category)
