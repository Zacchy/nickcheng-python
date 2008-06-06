from django.db import models
from datetime import datetime

# Create your models here.
class Category(models.Model):
    name = models.CharField(maxlength = 55, default = '')
    slug = models.SlugField(maxlength = 200, prepopulate_from = ('name',), default = '')
    
    class Admin:
        pass
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/blog/category/%s/" % (self.slug)
    
class Options(models.Model):
    name = models.CharField(maxlength = 64, default = '')
    value = models.TextField()
    
    class Admin:
        pass
    
    def __str__(self):
        return self.name
    
class Users(models.Model):
    name = models.CharField(maxlength = 60, default = '')
    password = models.CharField(maxlength = 64, default = '')
    nicename = models.CharField(maxlength = 50, default = '')
    email = models.EmailField(default = '')
    url = models.URLField(verify_exists = False, default = '')
    registerdate = models.DateTimeField(default = datetime.now())
    activation_key = models.CharField(maxlength = 60, default = '')
    status = models.IntegerField(default = 0)
    display_name = models.CharField(maxlength = 250, default = '')
    
    class Admin:
        pass
    
    def __str__(self):
        return self.name
    
class Posts(models.Model):
    author = models.IntegerField(default = 0)
    pub_date = models.DateTimeField(default = datetime.now())
    pub_date_gmt = models.DateTimeField(default = datetime.now())
    content = models.TextField()
    title = models.TextField()
    category = models.IntegerField(default = 0)
    summary = models.TextField()
    status = models.CharField(maxlength = 20, default = 'publish')
    comment_status = models.CharField(maxlength = 20, default = 'open')
    password = models.CharField(maxlength = 20, default = '')
    slug = models.CharField(maxlength = 200, default = '')
    modified = models.DateTimeField(default = datetime(1900, 1, 1, 0, 0))
    modified_gmt = models.DateTimeField(default = datetime(1900, 1, 1, 0, 0))
    ping_status = models.CharField(maxlength = 20, default = 'open')
    type = models.CharField(maxlength = 20, default = 'post')
    comment_count = models.IntegerField(default = 0)
    
    class Admin:
        ordering = ('-pub_date',)
        list_filter = ('author', 'pub_date')
        search_fields = ('title', 'content')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return "/blog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)
    
class Comments(models.Model):
    post_ID = models.IntegerField(default = 0)
    author = models.CharField(maxlength = 60, default = '')
    author_email = models.EmailField(default = '')
    author_url = models.URLField(verify_exists = False, default = '')
    author_IP = models.IPAddressField(default = '')
    date = models.DateTimeField(default = datetime.now())
    date_gmt = models.DateTimeField(default = datetime.now())
    content = models.TextField()
    approved = models.IntegerField(default = 1)
    agent = models.CharField(maxlength = 255, default = '')
    type = models.CharField(maxlength = 20, default = '')
    user_id = models.IntegerField(default = 0)
    
    class Admin:
        pass
    
    def __str__(self):
        return self.author
    
#    def get_absolute_url(self):
#        return '/blog/