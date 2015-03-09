import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()

# Import this after Django has been loaded and after django.setup() has been called
from rango.models import Category, Page

# Only seven so that some pages can have the same number of views
# Good for testing whether web page behaves well
# Could have used a random number generator but that would yield different
# test data each time the population script gets run => hard to replicate test cases
# We can easily adjust around with the values from a single point -> this dictionary
page_view_dict = {
    0: 10,
    1: 15,
    2: 30,
    3: 45,
    4: 50,
    5: 6,
    6: 131,
    7: 22
}


def populate():
    python_cat = add_cat(name='Python', views=128, likes=64)

    add_page(cat=python_cat,
        title="Official Python Tutorial",
        url="http://docs.python.org/2/tutorial/",
        views=page_view_dict[2])

    add_page(cat=python_cat,
        title="How to Think like a Computer Scientist",
        url="http://www.greenteapress.com/thinkpython/",
        views=page_view_dict[2])

    add_page(cat=python_cat,
        title="Learn Python in 10 Minutes",
        url="http://www.korokithakis.net/tutorials/python/",
       views=page_view_dict[0])

    django_cat = add_cat(name="Django", views=64, likes=32)

    add_page(cat=django_cat,
        title="Official Django Tutorial",
        url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/",
        views=page_view_dict[7])

    add_page(cat=django_cat,
        title="Django Rocks",
        url="http://www.djangorocks.com/",
        views=page_view_dict[6])

    add_page(cat=django_cat,
        title="How to Tango with Django",
        url="http://www.tangowithdjango.com/",
        views=page_view_dict[3])

    frame_cat = add_cat(name="Other Frameworks", views=32, likes=16)

    add_page(cat=frame_cat,
        title="Bottle",
        url="http://bottlepy.org/docs/dev/",
        views=page_view_dict[4])

    add_page(cat=frame_cat,
        title="Flask",
        url="http://flask.pocoo.org",
        views=page_view_dict[1])

    # My category
    my_cat = add_cat(name="Kristian Sonev | 2067044", views=0, likes=0)
    add_page(my_cat, title="Github", url="https://github.com/2067044", views=page_view_dict[5])
    add_page(my_cat, title="PythonAnywhere", url="http://2067044.pythonanywhere.com/rango", views=page_view_dict[5])

    # Give the user feedback on what we have added
    for cat in Category.objects.all():
        for page in Page.objects.filter(category=cat):
            print "- {0} - {1} ".format(str(cat), str(page))


# This function uses a view parameter, however if we change the number of views in the
# population script we get page duplicates. Flush the database
# each time the population script is ran? Or simply use YAML or JSON fixtures / FactoryBoy
def add_page(cat, title, url, views):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    return p


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


# Start population
if __name__ == '__main__':
    print 'Starting rango population script...'
    populate()
    print 'Population complete.'
