import os
import os.path
import sys

import yaml

os.environ['DJANGO_SETTINGS_MODULE'] = 'hrproj.settings'
from django.conf import settings
from django.contrib.auth.models import *
from hrproj.hr.models import *

# Set all ID numbers up by 10k to avoid clashes with sequence numbers
def add10k(num):
    return int(num) + 10000

def upload_picture(reader, data_dir):
    """ Uploads a picture for the reader, if one is found.
    """
    picture_file = os.path.join(data_dir, reader.user.username + '.jpeg')
    if not os.path.exists(picture_file):
        picture_file = os.path.join(data_dir, reader.user.username + '.jpg')
    if os.path.exists(picture_file):
        bytes = open(picture_file, 'rb').read()
        reader.save_picture_file(picture_file, bytes)

def load_readers(all_data, data_dir):
    member_group = Group.objects.get(name='member')
    for data in all_data:
        id = add10k(data['id'])
        if not User.objects.filter(id=id).count():
            u = User(id = id, username = data['username'])
            u.first_name, u.last_name = data['fullname'].split(' ', 1)
            u.set_password('passwod')
            u.is_staff = u.is_active = True
            u.is_superuser = False
            u.save()
            u.groups.add(member_group)

            r = Reader(bio = data['bio'], user=u)
            r.save()
            upload_picture(r, data_dir)

def load_books(all_data):
    for data in all_data:
        Book.objects.get_or_create(id=add10k(data['id']), 
                defaults=dict(
                    author = data['author'],
                    isbn = str(data['isbn']),
                    summary = data['summary'],
                    title = data['title']))

def load_tags(all_data):
    for data in all_data:
        tag, created = Tag.objects.get_or_create(id=add10k(data['id']),
                defaults=dict(
                    name = data['name']))
        if created:
            for book_id in data.get('books',[]):
                b = Book.objects.get(id=add10k(book_id))
                b.tags.add(tag)

def load_reading_occasions(all_data):
    for data in all_data:
        b = Book.objects.get(id = add10k(data['book_id']))
        u = User.objects.get(id = add10k(data['reader_id']))
        r = u.reader_set.all()[0]
        ReadingOccasion.objects.get_or_create(id=add10k(data['id']),
                defaults=dict(
                    book = b,
                    reader = r,
                    finished = data['date_read'],
                    reading_time = data['reading_time'],
                    notes = data['notes']))


def read_data(data_dir, filename):
    lines = file(os.path.join(data_dir, filename)).read()
    return yaml.load(lines).values()


def main(data_dir):
    load_readers(read_data(data_dir, 'readers.yml'), data_dir)
    load_books(read_data(data_dir, 'books.yml'))
    load_tags(read_data(data_dir, 'tags.yml'))
    load_reading_occasions(read_data(data_dir, 'readings.yml'))


if __name__ == '__main__':
    main(os.path.dirname(sys.argv[0]))
