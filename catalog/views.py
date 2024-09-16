from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language

from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import RenewBookForm
from django.urls import reverse, reverse_lazy
import datetime


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
    
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = BookInstance.objects.get(pk=pk)
    
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('borrowed-books'))
        
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial = {'renewal_date': proposed_renewal_date})
        
        
    context = {
        'form': form,
        'book_instance': book_instance
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth']
    initial = {'date_of_birth': '05/01/2018'}
    permission_required = 'catalog.add_author'
    
    
class AuthorUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.change_author'
    
class AuthorDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    
    permission_required = 'catalog.delete_author'
    
    def form_valid(self, form):
        try :
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        
        except Exception as e:
            return HttpResponseRedirect(reverse('author-detail', kwargs={'pk': self.object.pk}))
            
    