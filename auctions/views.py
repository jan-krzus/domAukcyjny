import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Bid,Categories,Listings,Categories, Watchlist, Comment
from .models import User
from .forms  import ListForm
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.messages import add_message, ERROR,SUCCESS
from .cart import Cart
from decimal import Decimal



def index(request):
    '''
    Funkcja wyświetlająca główną stronę aplikacji.
    '''
    context = {"Listings": Listings.objects.all().order_by('-created_at'),
               "user": request.user,
               "header": "Home"}

    return render(request, "auctions/index.html", context = context )   

def active_listing(request):
    '''
    Funkcja wyświetlająca aktywne aukcje.
    '''
    context = {"Listings": Listings.objects.filter(active=True),
               "user": request.user,
               "header": "Active listings",
               }
    return render(request, "auctions/index.html", context = context )



def login_view(request):
    '''
    Funkcja służca do logowania.
    '''
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Błędna nazwa użytkownika bądź hasło"
            })
    else:
        return render(request, "auctions/login.html")

@login_required     
def logout_view(request):
    '''
    Funkcja wylogowywania.
    '''
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def register(request):
    '''
    Funkcja rejerstracji nowego użytkownika
    '''
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Hasła nie zgadzają się."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Nazwa użytkownika jest już zajęta."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



def listingpage(request, listing_id):
    '''
    Funkcja wyświetlająca widok pojedyńczej aukcji
    listing_id - id aukcji
    '''
    item = Listings.objects.get(pk=listing_id)
    context = {"listing": item,
               "user": request.user, 
               "winner": item.get_winner(),
               "seller": item.get_seller(),
               "bids": Bid.objects.filter(listingid=listing_id),
               "comment_list": (item.comment).all(),
               "min_starting_bid": (item.starting_bid)+Decimal(0.1) ,
               "min_bid": (item.highest_bid)+Decimal(0.1),
                }
    return render(request, "auctions/listing.html", context = context )   

class CreateListing(LoginRequiredMixin, CreateView):
    model = Listings
    form_class = ListForm

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.save()
        return super(CreateListing, self).form_valid(form)



def all_categories(request):
    '''
    Funkcja wyświetlająca wszystkie aukcje
    '''
    categories = Categories.objects.all()
    context = {"categories" : categories,
    }
    return render(request, "auctions/categories.html", context = context)

def category_active_list(request, name):
    '''
    Funkcja wyświetlająca przedmioty z danej kategorii.
    name - nazwa przeglądanej kategorii
    '''
    cat_type    = Categories.objects.get(category_name=name)
    cat_listing = Listings.objects.filter(category=cat_type, active=True)

    context = {"Listings" :cat_listing,
    }
    if cat_listing:
        return render(request, "auctions/index.html", context = context )
    else:
        
        context = {"message": "Sorry, This Category has no active listings at the moment!",
        }
        return render(request, "auctions/errors.html", context = context) 


@login_required     
def make_bid(request, listing_id, method=(["POST"])):
    '''
    Funkcja do podbijania kwoty na aukcji.
    listing_id - id aukcji
    POST["amount"] - kwota licytacji
    '''
    amount = request.POST["amount"]
    item = Listings.objects.get(pk=listing_id)

    if amount:
        if float(amount) > item.highest_bid:
            new_bid = Bid(bidder=request.user, listingid=item, bid_value=amount)
            new_bid.save()
            item.update_price(amount)
            item.set_current_winner(request.user)
            item.save()
            return HttpResponseRedirect(reverse('listingpage', args=[listing_id]))

    else:
        return HttpResponseRedirect(reverse('listingpage', args=[listing_id]))


@login_required 
def view_winner(request, listing_id):
    '''
    Wyświetlanie zwycięzcy
    '''
    item = Listings.objects.get(pk=listing_id)
    winner = item.get_winner()
    return HttpResponseRedirect(reverse('listingpage', args=[listing_id]))
     
@login_required
def reopen_auction(request, listing_id):
    '''
    Funkcja do ponownego rozpoczęcia aukcji.
    '''
    item = Listings.objects.get(pk=listing_id)
    item.reopen()
    item.save()
    return HttpResponseRedirect(reverse('listingpage', args=[listing_id]))




@login_required
def watchlist_page(request):
    '''
    Funkcja wyświetlająca obserwowane aukcje.
    '''
    if Watchlist.objects.filter(user=request.user):

            user_watchlist = Watchlist.objects.get(user=request.user)
            user_items = user_watchlist.active_items()
                
            context = {"user_items":user_items,
                       "count": user_watchlist.get_count(),
            }

            if user_watchlist:
                return render(request, 'auctions/watchlist_list.html', context=context)
            else:
                return render(request, 'auctions/watchlist_list.html', context = {"message": 'Your watchlist is empty!'} )   
        
    else:
        return render(request, 'auctions/watchlist_list.html', context = {"message": 'Your watchlist is empty!'} )   

@login_required
def add_to_wishlist(request, product_id):
    '''
    Funkcja dodająca aukcje od obserwowanych.
    product_id - id aukcji
    '''
    item_to_save = Listings.objects.get(pk=product_id)

    if Watchlist.objects.filter(user=request.user, listing=product_id).exists():
        add_message(request, ERROR, "You already have it in your watchlist.")
        return HttpResponseRedirect(reverse('listingpage', args=[product_id]))

    else:
        user_list, created = Watchlist.objects.get_or_create(user=request.user)
        user_list.listing.add(item_to_save)
        add_message(request, SUCCESS, "Successfully added to your watchlist")
        return HttpResponseRedirect(reverse('listingpage', args=[product_id]))


@login_required
def Winlist(request):
    '''
    Funkcja wyświetlająca widok wygranych aukcji.
    '''
    if Listings.objects.filter(Winner=request.user, active=False):
        user_winlist = Listings.objects.filter(Winner=request.user, active=False)
        print(Listings.objects.filter(Winner=request.user))

        context = {"user_winlist": user_winlist,
                   "win_count": len(user_winlist),
        }
        return render(request, 'auctions/winlist.html', context=context)
    else:
        return render(request, 'auctions/winlist.html', context = {"message": 'Your winlist is empty!',
                                                                   "count" : (Watchlist.objects.get(user=request.user)).get_count()} )   

@login_required
def add_comment(request, listing_id):
    '''
    Funkcja dodająca komentarz do aukcji.
    listing_id - id aukcji
    '''
    getListing = Listings.objects.get(pk=listing_id)
    comment = request.POST["comment"]
    new_comment = getListing.comment.create(comment=comment, listingid=getListing, commenter=request.user)
    return HttpResponseRedirect(reverse('listingpage', args=[listing_id]))

@login_required(login_url="/users/login")
def cart_add(request, id):
    '''
    Dodanie przedmiotu do koszyka.
    id - id aukcji
    '''
    cart = Cart(request)
    product = Listings.objects.get(pk=id)
    cart.add(product=product, winner=product.Winner)
    return redirect("cart_detail")

@login_required(login_url="/users/login")
def item_clear(request, id):
    '''
    Usunięcie pojedyńczego przedmiotu z koszyka.
    id - id aukcji
    '''
    cart = Cart(request)
    product = Listings.objects.get(pk=id)
    cart.remove(product)
    return redirect("cart_detail")

@login_required(login_url="/users/login")
def cart_clear(request):
    '''
    Wyczyszczenie koszyka.
    '''
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")

@login_required(login_url="/users/login")
def cart_detail(request):
    '''
    Otwarcie koszyka.
    '''
    context = {"win_count": len(Listings.objects.filter(Winner=request.user, active=False)),
        }

    return render(request, 'auctions/cart_detail.html', context=context)

@login_required
def buy_now(request,listing_id):
    '''
    Kup teraz.
    '''
    item = Listings.objects.get(pk=listing_id)
    item.Winner=request.user
    item.update_price(item.desired_price)
    item.end()
    item.save()

    if Watchlist.objects.filter(user=request.user, listing=listing_id).exists():
            watchlist = Watchlist(user=item.Winner)
            item_to_delete = get_object_or_404(Watchlist, listing=listing_id)
            watchlist.listing.remove(item_to_delete)


    return HttpResponseRedirect(reverse(index))



@login_required
def close_auction(request, listing_id):
    '''
    Funkcja zamykająca aukcję.
    listing_id - id aukcji
    '''
    item = Listings.objects.get(pk=listing_id)
    item.end()
    item.save()

    if Watchlist.objects.filter(user=request.user, listing=listing_id).exists():
            watchlist = Watchlist(user=item.Winner)
            item_to_delete = get_object_or_404(Watchlist, listing=listing_id)
            watchlist.listing.remove(item_to_delete)


    return HttpResponseRedirect(reverse('listingpage', args=[listing_id]))
