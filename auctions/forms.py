from django import forms
from .models import Listings

class ListForm(forms.ModelForm):

    class Meta:
        model = Listings
        fields = ('title', 'description', 'starting_bid', 'desired_price', 'category', 'image')
        labels = { 'title': 'Tytuł', 'description': 'Opis aukcji', 'starting_bid': 'Cena wywoławcza', 'desired_price': 'Cena końcowa', 'category': 'Kategoria', 'image': 'Obrazek' }
