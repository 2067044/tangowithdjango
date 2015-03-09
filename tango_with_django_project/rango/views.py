from django.shortcuts import render
from django.shortcuts import redirect
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm, EditUserForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from models import UserProfile
from bing_search import run_query
from django.contrib.auth.models import User
import json


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

    # Used for return results
    context_dict['result_list'] = None
    context_dict['query'] = None

    # strip() removes any html tags
    #
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Running a Bing search to get the results list
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        # Try to get a category with this slug and add
        # it to the context variable or throw an exception
        category_object = Category.objects.get(slug=category_name_slug)
        category_object.views += 1
        category_object.save()
        context_dict['category_name'] = category_object.name

        # Get all associated category pages
        pages = Page.objects.filter(category=category_object).order_by("-views")
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


def track_url(request):
    '''
    This method tracks how many times a page has been visited.
    :param request: incoming request data
    :return:
    '''

    url = '/rango/'
    # If we have a get and there is a page id in the
    # get request, try updating the page views
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def register_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            return redirect("/rango/")
        else:
            print profile_form.errors
    else:
        profile_form = UserProfileForm()
    return render(request, "rango/ProfileRegistration.html", {'profile_form': profile_form})

@login_required
def edit_profile(request):
    context_dict = {}

    if request.method == 'POST':
        user_form = EditUserForm(data=request.POST, instance=request.user)
        profile_form = UserProfileForm(data=request.POST, instance=request.user.userprofile)

        if profile_form.is_valid and user_form.is_valid:
            profile = profile_form.save(commit=False)
            user = user_form.save(commit=False)
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            user.save()
            profile.save()
        else:
            print user_form.errors
            print profile_form.errors
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    context_dict['user_form'] = user_form
    context_dict['profile_form'] = profile_form
    context_dict['picture'] = request.user.userprofile.picture
    return render(request, "rango/profile.html", context_dict)


@login_required
def browse_profiles(request):
    all_users = User.objects.all()
    return render(request, 'rango/browse_profiles.html', {'users': all_users})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)


# Helper function for getting categories starting with a particular string
def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        return cat_list


# View responsible for dynamically suggesting categories to users
def suggest_category(request):
        cat_list = []
        starts_with = ''

        # Pull the data from an ajax script
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)
        response = {}
        results = []
        for k in cat_list:
            results.append({'name': k.name, 'url': "/rango/category/" + k.slug})
        response['data'] = results

        return HttpResponse(json.dumps(results), content_type="application/json")














