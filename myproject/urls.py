from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Map the root URL ("") to include your books app's URLs.
    # Since books.urls has path("", views.BookListView.as_view(), name="book.all"),
    # this will make your BookListView the default page at the root.
    path('', include('books.urls')), # <--- THIS IS THE KEY CHANGE

    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True), name='login'),
    # Keep Django's authentication URLs included. They will now be at paths like /logout/, /password_reset/ etc.
    # Note: If you want /accounts/login/ etc. to also work, you can keep the original include,
    # but for a cleaner setup, you might rely on the specific named URLs like 'login', 'logout'.
    # If you remove the path('', include('django.contrib.auth.urls')), ensure all auth links use named URLs.
    # For now, let's keep it as it was, but the books app is now primary at root.
    # If you want to explicitly avoid /accounts/ paths, you'd remove the line below
    # and ensure all auth links in templates use named URLs like {% url 'login' %}.
    path('', include('django.contrib.auth.urls')), # This line remains, but is less critical for root if books.urls is first.
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
