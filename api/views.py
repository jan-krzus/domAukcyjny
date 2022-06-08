from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListAPIView
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework import serializers, viewsets, routers
from rest_framework import permissions
from auctions.models import Listings, Bid, Comment, Watchlist, Categories, User
from .serializers import ListingsSerializer, CategoriesSerializer,UserSerializer, CommentSerializer, BidsSerializer, WatchListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.views import APIView


class ItemsPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 10

class UsersView(generics.ListAPIView):
    """
    API endpoint który pozwala na wyświetlenie wszystkcih aukcji oraz utworzenie nowych.   
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

class ListingsView(generics.ListCreateAPIView):
    """
    API endpoint który pozwala na wyświetlenie wszystkcih aukcji oraz utworzenie nowych.
    """

    queryset = Listings.objects.all()
    serializer_class = ListingsSerializer
    filter_fields = ['active', 'seller__username', 'id']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'description']
    pagination_class = ItemsPagination


class ListingDetailsView(APIView):

    """
    API endpointa który edytuje, uaktualnia oraz usuwa aukcje o podanym id.
    """
    queryset = Listings.objects.all()
    serializer_class = ListingsSerializer


    def get_object(self, listing_id):

        '''
        Funkcja pomocnicza do wyciągania aukcji o danym id
        '''
        try:
            return Listings.objects.get(pk=listing_id)
        except Listings.DoesNotExist:
            return None
    def get(self, request, listing_id, *args, **kwargs):
        '''
        Funkcja pomocnicza wyciągająca szczegółowe informacje podanej aukcji
        '''
        listing_instance =  self.get_object(listing_id)
        if not listing_instance:
            return Response(
                {"res": "Aukcja o podanym id nie istnieje"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        listings_serializer = ListingsSerializer(listing_instance)
        return Response(listings_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, listing_id, **kwargs):
        '''
        Uaktualnie aukcje o podanym id.
        '''

        listing_instance = self.get_object(listing_id)
        if not listing_instance:
            return Response(
                {"res": "Aukcja o podanym id nie istnieje"}, 
                status=status.HTTP_400_BAD_REQUEST)

        data = JSONParser().parse(request)
        listings_serializer = ListingsSerializer(instance =listing_instance, data=data, partial = True)
        if listings_serializer.is_valid():
            listings_serializer.save()
            return Response(listings_serializer.data, status=status.HTTP_200_OK)
        return Response(listings_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
    # 3. edit
    def put(self, request, listing_id, *args, **kwargs):
        '''
        Uaktualnie aukcje o podanym id.
        '''
        listing_instance = self.get_object(listing_id)
        if not listing_instance:
            return Response(
                {"res": "Aukcja o podanym id nie istnieje"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'title': request.data.get('title'), 
            'description':  request.data.get('description'), 
            'starting_bid': request.data.get("starting_bid"),
            'desired_price': request.data.get("desired_price"),
            'image': request.data.get("image"),
            'active': request.data.get("active"),
        }

        listings_serializer = ListingsSerializer(instance = listing_instance, data=data, partial = True)
        if listings_serializer.is_valid():
            listings_serializer.save()
            return Response(listings_serializer.data, status=status.HTTP_200_OK)
        return Response(listings_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. Delete
    def delete(self, request, listing_id, *args, **kwargs):
        '''
        Usuwa aukcje o danym id.
        '''
        listing_instance = self.get_object(listing_id)
        if not listing_instance:
            return Response(
                {"res": "Aukcja o podanym id nie istnieje"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        listing_instance.delete()
        return Response(
            {"res": "Aukcja pomyślnie usunięta!"},
            status=status.HTTP_200_OK
        )
   

class CommentsView(generics.ListAPIView):
    """
    API endpoint który wyświetla komentarze.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    filter_fields = ['id','commenter__username']
    filter_backends = [DjangoFilterBackend]


class ListBidsview(ListAPIView):

    """
    API endpoint która wyświetla wszystkie licytowania użytkownika
    """

    queryset = Bid.objects.all()
    serializer_class = BidsSerializer
    filter_fields = ['id', 'listingid']
    filter_backends = [DjangoFilterBackend]


class WatchListsView(ListAPIView):

    """
    API endpoint która wyświetla obserwowane aukcje na podstawie id użytkownika
    """
    queryset = Watchlist.objects.all()
    serializer_class = WatchListSerializer
    filter_fields = ['user__username', 'id']
    filter_backends = [DjangoFilterBackend]
    

class CategoriesView(ListAPIView):

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


