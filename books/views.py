from django.shortcuts import render, get_object_or_404,redirect
from books.models import Book,Review, Authors
from django.http import Http404
from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from books.form import ReviewForm, RegisterForm # Import your new RegisterForm
from django.contrib.auth import login # Import login function
from django.contrib.auth.models import User # Import User model for validation

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

# New Registration View
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save() # Save the new user
            login(request, user) # Log the user in immediately after registration
            return redirect('book.all') # Redirect to the book list page after successful registration
        # If form is not valid, it will fall through to render the form with errors
    else:
        form = RegisterForm() # Empty form for GET request
    
    # Render the registration template with the form
    return render(request, 'registration/register.html', {'form': form})

