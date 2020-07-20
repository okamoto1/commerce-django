from django.forms import ModelForm
from django import forms

from .models import Auction, Bids, Comments


class Listing_Form(forms.Form):
    init_bid = forms.IntegerField(label="Initial Bid",
        min_value = 0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Starting Bid'
        })
    )
    title = forms.CharField(label="Items Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Item's name"
        })
    )
    description = forms.CharField(label="Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Description'
        })
    )
    image = forms.FileField(label="Choose Image")
    

class BidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        self.fields['bid_value'].widget.attrs['min'] = 50

    class Meta:
        model = Bids
        fields = ['bid_value']



class CommentsForm(forms.Form):
    comentarios = forms.CharField(label="",
        widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Place your comment here'
        })
    )

class CategoryForm(forms.Form):
    category = forms.CharField(label="Create a category",
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Category"
    }))
