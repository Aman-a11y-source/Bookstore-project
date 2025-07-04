from django.contrib import admin
from books.models import Book,Review,Authors
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Authors)
