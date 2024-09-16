from django.contrib import admin
from catalog.models import Author, Book, BookInstance, Genre, Language

# Register your models here.

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Author)
admin.site.register(Book)   
# admin.site.register(BookInstance)

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'guid')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'guid')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )