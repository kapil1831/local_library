from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language

from django.views import generic

# Create your views here.
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
    
    
class BookListView(generic.ListView):
    model = Book
    template_name = 'catalog/books.html'
    queryset = Book.objects.all()[:5]
    context_object_name = 'books'
    paginate_by = 2
    
class BookDetailView(generic.DetailView):
    model = Book
    
    
class AuthorListView(generic.ListView):
    model = Author
    template_name = 'catalog/authors.html'
    queryset = Author.objects.all()
    context_object_name = 'authors'
    paginate_by = 2

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'