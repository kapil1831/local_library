from django.db import models
from django.urls import reverse
from django.db.models.constraints import UniqueConstraint
from django.db.models.functions import Lower
import uuid
# Create your models here.

class Genre(models.Model):
    """ Model representing a book genre. """
    name = models.CharField(max_length=50, help_text='Enter a book genre (e.g. Science Fiction, French Poetry etc.)', unique=True)
    
    def __str__(self) -> str:
        """ string for representing the Genre object. """
        return self.name
    
    def get_absolute_url(self):
        return reverse("genre-detail", kwargs={"id": self.id})
    
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message = "Genre already exists (case insensitive match)"
            ),
        ]
        
        
class Language(models.Model):
    """ Model representing a Language (e.g. English, French, Japanese, etc.) """
    name = models.CharField(max_length=50, help_text='Enter the book\'s natural language (e.g. English, French, Japanese etc.)', unique=True)
    
    def __str__(self) -> str:
        """ string for representing the Language object. """
        return self.name
    
    def get_absolute_url(self):
        return reverse("language-detail", kwargs={"id": self.id})
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message = "Language already exists (case insensitive match)"
            ),
        ]
        
class Book(models.Model):
    """ Model representing a book (but not a specific copy of a book). """
    title = models.CharField(max_length=200, help_text='Enter the title of the book')
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    
    genre = models.ManyToManyField('Genre', help_text='Select a genre for this book')
    
    language = models.ForeignKey('Language', on_delete=models.RESTRICT, null=True) #one to many relationship with Language
    
    
    def __str__(self) -> str:
        """ string for representing the Book object. """
        return self.title
    
    def get_absolute_url(self):
        """ Returns the url to access a detail record for this book. """
        return reverse("book-detail", kwargs={"pk": self.pk})
    
    
class BookInstance(models.Model):
    """ Model representing a specific copy of a book (i.e. that can be borrowed from the library). """ 
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )   
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')
    
    class Meta:
        ordering = ['due_back']
        
    def __str__(self) -> str:
        """ string for representing the Model object. """
        return f'{self.guid} ({self.book.title})'
    
class Author(models.Model):
    """ Model representing an author. """
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self) -> str:
        """ string for representing the Model object. """
        return f'{self.last_name}, {self.first_name}'
    
    def get_absolute_url(self):
        """ Returns the url to access a particular author instance. """
        return reverse("author-detail", kwargs={"id": self.id})
    
    class Meta:
        ordering = ['last_name', 'first_name']