from datetime import datetime
import re
from threading import Thread
from Queue import Queue

from django.contrib.auth.models import User
from django.db import models, transaction

from hrproj.lib import amazon

NO_VALUE = object()

def calc_slug(name):
    """ Calculates a slug from a name.
    """
    no_spaces = re.sub(r"\s+", "-", name.lower())
    return re.sub(r"[^-\w]", "", no_spaces)[:50]

class Tag(models.Model):
    name = models.CharField(maxlength=200, unique=True)
    slug = models.SlugField(prepopulate_from=('name',), unique=True)

    class Admin:
        pass

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return "/tags/%s/" % self.slug

    def save(self):
        """ Ensures the slug is set.
        """
        if self.name and not self.slug:
            self.slug = calc_slug(self.name)
        return super(Tag, self).save()

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(maxlength=200)
    author = models.CharField(maxlength=200)
    isbn = models.CharField('ISBN', maxlength=15)
    summary = models.TextField(maxlength=2000)
    tags = models.ManyToManyField(Tag, blank=True)
    slug = models.SlugField(prepopulate_from=('title',), unique=True)
    amazon_checked = models.DateTimeField(null=True, blank=True)
    amazon_small_url = models.URLField(null=True, blank=True)
    amazon_large_url = models.URLField(null=True, blank=True)
    amazon_buy_url = models.URLField(null=True, blank=True)

    __most_recent = NO_VALUE

    class Admin:
        list_display = ('title', 'author')
        fields = (
            (None, {
                'fields': ('title', 'author', 'isbn', 'tags', 'summary')
            }),
            ('Advanced', {
                'classes': 'collapse',
                'fields': ('slug', 'amazon_checked', 'amazon_small_url',
                    'amazon_large_url', 'amazon_buy_url')
            }),
        )

    class Meta:
        ordering = ('author', 'title')

    def fetch_amazon_data(self):
        """ Fetch amazon data for this book
        """
        try:
            result = amazon.searchByASIN(self.isbn)[0]
            self.amazon_buy_url = result.URL
            self.amazon_small_url = result.ImageUrlSmall
            self.amazon_large_url = result.ImageUrlLarge
            self.amazon_checked = datetime.now()
            print "Data retrieved OK"
        except amazon.AmazonError, e:
            print "Amazon i/f returned error: %s" % e

    def get_absolute_url(self):
        return "/books/%s/" % self.slug

    @property 
    def most_recent(self):
        """ Gets most recent reading occasion, if there is one.
        """

        if self.__most_recent == NO_VALUE:
            self.__most_recent = None
            ro_list = ReadingOccasion.objects.filter(book=self.id).order_by('-finished')
            if ro_list.count():
                self.__most_recent = ro_list[0]
        return self.__most_recent

    def save(self):
        """ Ensures the slug is set.
        """
        if self.title and not self.slug:
            self.slug = calc_slug(self.title)
        if self.should_check_amazon:
            self.fetch_amazon_data()
        super(Book, self).save()

    @property
    def should_check_amazon(self):
        """ Whether a check of Amazon is required. 
        """
        if not self.amazon_checked:
            return True
        interval = datetime.now() - self.amazon_checked
        print interval.days
        return interval.days >= 1

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Reader(models.Model):
    user = models.ForeignKey(User, edit_inline=models.STACKED, max_num_in_admin=1)
    bio = models.TextField(core=True, maxlength=2000)
    picture = models.ImageField(upload_to="photos/%Y%m%d", blank=True)

    __most_recent = NO_VALUE

    def get_absolute_url(self):
        return "/readers/%s/" % self.user.username

    @property 
    def most_recent(self):
        """ Gets most recent reading occasion, if there is one.
        """
        if self.__most_recent == NO_VALUE:
            self.__most_recent = None
            ro_list = ReadingOccasion.objects.filter(reader=self.id).order_by('-finished')
            if ro_list.count():
                self.__most_recent = ro_list[0]
        return self.__most_recent
    
    @property
    def name(self):
        return self.user.get_full_name()

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ReadingOccasion(models.Model):
    reader = models.ForeignKey(Reader)
    book = models.ForeignKey(Book, edit_inline=models.STACKED, num_in_admin=1)
    finished = models.DateField(core=True)
    reading_time = models.FloatField(core=True, max_digits=5, decimal_places=2, blank=True)
    notes = models.TextField(maxlength=2000, blank=True)

