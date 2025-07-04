from django.shortcuts import render, get_object_or_404,redirect
from books.models import Book,Review, Authors
from django.http import Http404
from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
# from django.core.files.storage import FileSystemStorage # Not needed if using ModelForm.save()
from books.form import ReviewForm # Ensure ReviewForm is imported

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
        context['form'] = ReviewForm() # Pass an empty form instance for GET requests
        return context
    
def review(request,id):
    book = get_object_or_404(Book, id=id) # Get the book instance

    if request.method == 'POST':
        if request.user.is_authenticated:
            # Pass request.POST for text data and request.FILES for file uploads
            form = ReviewForm(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit=False) creates a Review instance but doesn't save it to DB yet.
                # This allows us to assign foreign keys (book, user) before saving.
                newReview = form.save(commit=False)
                newReview.book = book # Assign the book instance
                newReview.user = request.user # Assign the logged-in user
                newReview.save() # Now save the instance to the database (including the image)
                return redirect('book.show', pk=id) # Redirect back to the book detail page
            else:
                # If the form is not valid, you might want to re-render the page with the form errors
                # For debugging, printing errors is useful.
                print("Form errors:", form.errors)
                # For better UX, you'd typically re-render book_detail.html with the invalid form
                # return render(request, 'books/book_detail.html', {'book': book, 'form': form, 'reviews': book.review_set.all().order_by('-created_at'), 'authors': book.authors.all()})
                return redirect('book.show', pk=id) # For now, just redirect
        else:
            # If user is not authenticated, redirect to login
            return redirect('login')
    # If it's a GET request to /review/id (e.g., direct access), redirect back to book detail
    return redirect('book.show', pk=id)

def author(request,author):
    books= Book.objects.filter(authors__name=author)
    return render(request, "books/book_list.html", {'book_list': books, 'author': author})
