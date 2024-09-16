from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language

from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


from django.contrib.auth.mixins import AccessMixin

class StaffRequiredMixin(AccessMixin):
    """
    Mixin that requires the user to be a staff member.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            # Optionally, redirect to a custom page or return a 403 response
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to access this page.")


# Create your views here.
@login_required
def index(request):
    
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    num_authors = Author.objects.count()
    num_genre = Genre.objects.count()
    num_books_with_word_power = Book.objects.filter(title__icontains= 'power').count()
    
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits
    
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_books_with_word_power': num_books_with_word_power,
        'num_visits': num_visits
    }
    
    return render(request, 'index.html', context=context)
    
    
class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = 'catalog/books.html'
    queryset = Book.objects.all()[:5]
    context_object_name = 'books'
    paginate_by = 2
    
class BookDetailView(generic.DetailView):
    model = Book
    
    
class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    template_name = 'catalog/authors.html'
    queryset = Author.objects.all()
    context_object_name = 'authors'
    paginate_by = 2

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 2
    context_object_name = 'bookinstances'
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    
class BorrowedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/borrowed_books.html'
    context_object_name = 'borrowed_books'
    paginate_by = 5
    
    permission_required = 'catalog.can_mark_returned'
    
    
    def get_queryset(self) -> QuerySet[Any]:
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')