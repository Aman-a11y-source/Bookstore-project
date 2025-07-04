from django.shortcuts import render, get_object_or_404,redirect
from books.models import Book,Review, Authors
from django.http import Http404
from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from books.form import ReviewForm, RegisterForm
from django.contrib.auth import login
from django.contrib.auth.models import User

class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "book_list"

    def get_queryset(self):
        queryset = super().get_queryset() 
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(shortDescription__icontains=query) |
                Q(longDescription__icontains=query) |
                Q(authors__name__icontains=query)
            ).distinct()
        
        return queryset

class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = context['book'].review_set.all().order_by('-created_at')
        context['authors'] = context['book'].authors.all()
        context['form'] = ReviewForm()
        return context
    
def review(request,id):
    book = get_object_or_404(Book, id=id) 
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST, request.FILES) 
            if form.is_valid():
                newReview = form.save(commit=False)
                newReview.book = book
                newReview.user = request.user
                newReview.save()
                return redirect('book.show', pk=id)
            else:
                print("Form errors:", form.errors)
                return redirect('book.show', pk=id)
        else:
            return redirect('login') 
    return redirect('book.show', pk=id)

def author(request,author):
    books= Book.objects.filter(authors__name=author)
    return render(request, "books/book_list.html", {'book_list': books, 'author': author})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book.all')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

# New Views for static pages
def about_us_view(request):
    return render(request, 'books/about_us.html')

def contact_view(request):
    # You can pass context here if needed, e.g., contact details
    context = {
        'phone_number': '+91 8972624560',
        'instagram_url': 'https://www.instagram.com/aman.brahma/',
        'linkedin_url': 'https://www.linkedin.com/in/aman-brahma-141282315/',
    }
    return render(request, 'books/contact.html', context)

def privacy_policy_view(request):
    return render(request, 'books/privacy_policy.html')

def terms_of_service_view(request):
    return render(request, 'books/terms_of_service.html')

