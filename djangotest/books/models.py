from django.db import models

# Create your models here.
class Publisher(models.Model):
    name = models.CharField(maxlength = 30)
    address = models.CharField(maxlength = 50)
    city = models.CharField(maxlength = 60)
    state_province = models.CharField(maxlength = 30)
    country = models.CharField(maxlength = 50)
    website = models.URLField()

    def __str__(self):
        return self.name

    class Admin:
        pass

class Author(models.Model):
    salutation = models.CharField(maxlength = 10)
    first_name = models.CharField(maxlength = 30)
    last_name = models.CharField(maxlength = 40)
    email = models.EmailField()
    headshot = models.ImageField(upload_to = '/tmp')

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Admin:
        pass

class Book(models.Model):
    title = models.CharField(maxlength = 100)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)
    publication_date = models.DateField()

    def __str__(self):
        return self.title

    class Admin:
        list_display    = ('title', 'publisher', 'publication_date')
        list_filter     = ('publisher', 'publication_date')
        ordering        = ('-publication_date',)
        search_fields   = ('title',)
