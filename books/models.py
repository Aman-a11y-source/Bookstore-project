from django.db import models
from django.contrib.auth.models import User


class Authors(models.Model):
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=256)
    pageCount = models.IntegerField(default=0)
    thumbnailUrl = models.CharField(max_length=512, null=True)
    shortDescription = models.CharField(max_length=512, null=True)
    longDescription = models.TextField(null=True)
    isbn = models.CharField(max_length=13, null=True)
    publishedDate= models.DateField(null=True)
    authors = models.ManyToManyField('Authors', related_name='books', blank=True)
    categories = models.CharField(max_length=256, null=True)
    status = models.CharField(max_length=256, null=True)
    image = models.ImageField(upload_to="images", null=True)
    
    

    def __str__(self):
        return self.title
    


class Review(models.Model):
   body = models.TextField(null=False)
   user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
   created_at = models.DateTimeField(auto_now=True)
   book = models.ForeignKey(Book, on_delete=models.CASCADE,null=True)
   image = models.ImageField(upload_to="reviews", null=True)



   