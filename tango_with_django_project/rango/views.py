from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from bing_search import run_query


def index(request):
    # Category model query
    # Get all categories and order in descending order
    # according to likes; then pick the first 5 (e.g. top 5 categories)
    category_list = Category.objects.order_by('-likes')[:5]

    # Get top 5 most viewed pages
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list,
                    'pages': pages_list
                    }

    # COOKIE HANDLING
    # SERVER SIDE COOKIES
    visits = request.session.get('visits')
    if not visits:
        visits = 1

    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # Append 1 to the cookie value
            visits += 1
            reset_last_visit_time = True

    else:
        # Cookie last_visit does not exist so create it
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits

    context_dict['visits'] = visits
    response = render(request, 'rango/index.html', context_dict)
    return response

    # ------------- CLIENT SIDE COOKIES --------------------
    # Get visits cookie; if it exists -> cast to int, otherwise default at 1
    # ALL COOKIE VALUES ARE RETURNED AS STRINGS; CAST THEM!
    # visits = int(request.COOKIES.get('visits', '1'))
    #
    # reset_last_visit_time = False
    # context_dict['visits'] = visits
    # response = render(request, 'rango/index.html', context_dict)
    # if 'last_visit' in request.COOKIES:
    #     last_visit = request.COOKIES['last_visit']
    #     # Cast the last visit to a python datetime object
    #     last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
    #
    #     # If it has been more than a day since the last visit, increment visits
    #     if (datetime.now() - last_visit_time).days < 0:
    #         visits += 1
    #         # .. flag that the last_visits cookie needs to be updated
    #         reset_last_visit_time = True
    # else:
    #     # Cookie last_visit does not exist so flag that it should be set
    #     reset_last_visit_time = True
    #     context_dict['visits'] = visits
    #
    #     response = render(request, 'rango/index.html', context_dict)
    #
    # if reset_last_visit_time:
    #     # Here it does not matter what type we pass in; it will be automatically cast to a string
    #     response.set_cookie('last_visit', datetime.now())
    #     response.set_cookie('visits', visits)


def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 9

    return render(request, 'rango/about.html', {'visits': count})


def category(request, category_name_slug):
    context_dict = {}

    try:
        # Try to get a category with this slug and add
        # it to the context variable or throw an exception
        category_object = Category.objects.get(slug=category_name_slug)
        category_object.views += 1
        category_object.save()
        context_dict['category_name'] = category_object.name

        # Get all associated category pages
        pages = Page.objects.filter(category=category_object)
        context_dict['pages'] = pages

        # Used in the tempalte to verify that the category exists
        context_dict['category'] = category_object

        # Needed the category slug so that we can pass it to the add_page view
        context_dict['category_slug'] = category_name_slug

    except Category.DoesNotExist:
        # Do nothing here
        pass

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            cat = form.save(commit=True)
            print "DEBUG :: =>  Added form (name: '%s', slug: '%s')" % (cat, cat.slug)  # DEBUG INFO
            return index(request)  # Calling the index view from here; Essentially a redirect or not?
        else:
            print form.errors  # Print what went wrong in the terminal

    # If the request was not post display the form to create a new category...
    else:
        form = CategoryForm()

    # Bad form or no form details provided
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    # Try to get category object; if fail set category to none
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)  # Commit false -> does not immediately save to db
                page.category = cat
                page.views = 0
                page.save()  # Need this because Commit false
                print "DEBUG :: =>  Added page (title: '%s', url: '%s', cat: '%s')" % (page, page.url, cat)  # DEBUG INFO
                return category(request, category_name_slug)

        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'cat': cat}
    return render(request, 'rango/add_page.html', context_dict)


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})














