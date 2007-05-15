from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.db.models import signals
from django.dispatch import dispatcher
from hrproj.hr import models 


def get_perm(name):
    try:
        return Permission.objects.get(name=name)
    except Permission.DoesNotExist:
        print "Permission '%s' not found. Re-run syncdb on completion." % name
        return None

def init_group():
    """ Set up a group for easy permissions management """
    print "Setting up group"
    group, created = Group.objects.get_or_create(name='member')
    perms = [
            get_perm("Can add user"), 
            get_perm("Can change user"), 
            get_perm("Can add reader"), 
            get_perm("Can change reader"), 
            get_perm("Can add reading occasion"), 
            get_perm("Can change reading occasion"), 
            get_perm("Can delete reading occasion"), 
            get_perm("Can add tag"), 
            get_perm("Can change tag"), 
            get_perm("Can add book"), 
            get_perm("Can change book"),]
    for p in perms:
        if p:
            group.permissions.add(p)
        else:
            print "dud perm"

    print "Setting up group 'member'"

dispatcher.connect(init_group, sender=models, signal=signals.post_syncdb)
