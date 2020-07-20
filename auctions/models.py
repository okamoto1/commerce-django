from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendedor")
    item = models.CharField(max_length=100)
    min_bid = models.IntegerField()
    description = models.TextField()
    active = models.BooleanField(default=True)
    image = models.ImageField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller}, {self.item}, {self.description}, {self.active}, {self.min_bid}"

class Bids(models.Model):
    item_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="item_bids")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comprador")
    bid_value = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer}, lance de {self.bid_value}, no dia {self.date}"

class Comments(models.Model):
    item_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="item_comments")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario")
    date = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField()

    def __str__(self):
        return f"{self.usuario},  {self.comentarios}, {self.item_id}"

class Watchlist(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_watchlist")
    item_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="item_watchlist")

    def __str__(self):
        return f"{self.usuario}, {self.item_id}, {self.id}"


class Category(models.Model):
    category = models.CharField(max_length=64)
    itemsFromCategory = models.ManyToManyField(Auction, blank=True, related_name="itemsFromCategory")

    def __str__(self):
        return f" {self.id}, {self.category}"
