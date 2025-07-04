from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="book.all"),
    path("<int:pk>",views.BookDetailView.as_view(), name='book.show'),
    path('<int:id>/review',views.review, name='book.review'),
    path("<str:author>",views.author, name="author.books"),
    path('register/', views.register, name='register'),

   
    path('about-us/', views.about_us_view, name='about_us'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
]
