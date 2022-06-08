from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path("listings/", views.ListingsView.as_view(), name='get_listings'),
    path("users/", views.UsersView.as_view(), name='get_users'),
    path("listings/<int:listing_id>/", views.ListingDetailsView.as_view()),
    path("comments/", views.CommentsView.as_view()),
    path("watchlists/", views.WatchListsView.as_view()),
    path("categories/", views.CategoriesView.as_view()),
    path("bids/", views.ListBidsview.as_view()),
]