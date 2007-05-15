from django.db import connection
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import html 
from django.utils.datastructures import SortedDict
from django.views.generic.list_detail import object_list
from hrproj.hr.models import Tag, Book, Reader, ReadingOccasion


########
# Constants 
########
# Number of items on a page
PAGE_SIZE = 10

TAG_POPULARITY_QUERY = """ 
    select bt.tag_id, count(bt.*) 
      from hr_book_tags bt 
     inner join hr_readingoccasion ro on ro.book_id = bt.book_id
     group by bt.tag_id"""

TAG_POP_LEVELS = [(1, 0.2), (3, 0.60), (5, 1.2), (7, 2.0)]

########
# Helper Functions
########

def fetch_tag_counts():
    """ Returns a dictionary keyed by tag id, of the number of reading
        occasions each tag has been involved in.
    """
    cursor = connection.cursor()
    cursor.execute(TAG_POPULARITY_QUERY)
    result = {}
    for row in cursor.fetchall():
        result[row[0]] = row[1]
    cursor.close()
    return result

def get_page(request):
    """ Determines the current page number.
    """
    return int(request.GET.get('page', 1))

def level_for(popularity):
    for level, factor in TAG_POP_LEVELS:
        if popularity < factor:
            return level
    return 9

def tags_with_pop_level():
    """ Returns every tag, but with an extra attribute 'pop_level'.
        pop_level is an odd number between 1 and 9 inclusive, indicating the 
        popularity of the tag.
    """
    tag_counts = fetch_tag_counts()
    total = sum(tag_counts.values())
    all_tags = list(Tag.objects.all())
    for tag in all_tags:
        count = tag_counts.get(tag.id, 0)
        popularity = float(count) / total * len(all_tags)
        tag.pop_level = level_for(popularity)
    return all_tags

def standard_view(request, queryset, template_name, 
        template_object_name, **extra_context):
    """ Wrapper around the object_list generic view.
    """
    return object_list(request, queryset=queryset,
            allow_empty=True,
            template_name=template_name,
            template_object_name=template_object_name,
            page=get_page(request),
            paginate_by=PAGE_SIZE, 
            extra_context=extra_context)

########
# View Functions
########

def index(request):
    """ The main index page
    """
    read_occs = ReadingOccasion.objects.select_related().order_by('-finished',)[:10]
    tags = tags_with_pop_level()
    return render_to_response("index.html", dict(read_occs=read_occs, tags=tags), 
            RequestContext(request))

def reader_list(request):
    """ Shows the list of readers. 
        (at /readers/)
    """
    # This is unsorted
    queryset = Reader.objects.all().select_related()
    queryset = queryset.order_by('auth_user.first_name', 'auth_user.last_name')
    return standard_view(request, queryset, 'reader_list.html', 'reader')

def reader_detail(request, username):
    """ Details for a single reader. Includes a page of reading occasions.
        (e.g. /readers/fredp/)
    """
    reader = get_object_or_404(Reader, user__username=username)
    
    queryset = reader.readingoccasion_set.all()
    queryset = queryset.extra(select={'book_title': 'hr_book.title'})
    queryset = queryset.select_related().order_by("-finished")

    return standard_view(request, queryset, 'reader_detail.html',
            'readingoccasion', reader=reader)

def tag_list(request):
    """ Shows the list of tags. 
        (at /tags/)
    """
    queryset = Tag.objects.all().order_by('name')
    return standard_view(request, queryset, 'tag_list.html', 'tag')

def tag_detail(request, slug):
    """ Shows a single tag, including a list of books.
        (e.g. /tags/adventure/)
    """
    tag = get_object_or_404(Tag, slug=slug)
    queryset = Book.objects.all().filter(tags=tag).order_by('title')
    return standard_view(request, queryset, 'tag_detail.html', 'book', tag=tag)

def book_list(request):
    """ Shows the list of books. 
        (at /books/)
    """
    queryset = Book.objects.all().order_by('title')
    return standard_view(request, queryset, 'book_list.html', 'book')

def book_detail(request, slug):
    """ Shows a single book, including a list of reading occasions
        (e.g. /books/adventure/)
    """
    book = get_object_or_404(Book, slug=slug)
    queryset = ReadingOccasion.objects.all().filter(book = book).order_by('finished')
    return standard_view(request, queryset, 'book_detail.html', 'readingoccasion', book=book)

