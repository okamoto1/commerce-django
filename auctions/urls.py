from django.urls import path
from django.conf import settings
from django.conf import settings
from django.conf.urls.static import static


from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-auction", views.create_list, name="new-listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add-watchlist/<int:id>", views.add_watchlist, name="add_watchlist"),
    path("remove-watchlist/<int:id>", views.remove_watchlist, name="remove_watchlist"),
    path("comment/<str:title>/<int:id>", views.adding_comment , name="adding_comment"),
    path("bid/<str:title>/<int:id>", views.adding_bid , name="adding_bid"),
    path("close/<int:id>", views.close_auction, name="close_auction"),
    path("auction/<str:title>/<int:id>", views.items_page, name="items_page")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
