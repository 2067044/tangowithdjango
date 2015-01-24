from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
    return render(request, 'rango/index.html', context_dict)


def about(request):
    return render(request, 'rango/about.html', {})


def category(request, category_name_slug):
    context_dict = {}

    try:
        # Try to get a category with this slug and add
        # it to the context variable or throw an exception
        category_object = Category.objects.get(slug=category_name_slug)
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


def register(request):
    # Boolean value to keep track of registration success;
    # changes to true if registration is successful
    registered = False

    # If method == post; we would like to process the data
    if request.method == 'POST':
        # Get form information for both user and userProfile
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save user's data to database
            user = user_form.save()

            # Next we hash the password
            user.set_password(user.password)
            user.save()

            # Handle UserProfile; since we need to set the user attribute ourselves, we
            # set the commit to false
            profile = profile_form.save(commit=False)
            profile.user = user

            # Has a profile picture been provided? If so, save
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Finally save
            profile.save()

            registered = True  # Update boolean value

        # Invalid form or some other problems; print problems to termnal
        else:
            print user_form.errors, profile_form.errors

    # Not http post
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render template depending on context
    return render(request,
                  'rango/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
                  )


def user_login(request):
    if request.method == 'POST':
        # Info obtained from the login form
        username = request.POST['username']
        password = request.POST['password']

        # Let django decide whether user/pass pair is correct;
        # a User object is returned
        user = authenticate(username=username, password=password)

        # If the user object returned is not None
        if user:
            # Is the account active; it could've been disabled
            if user.is_active:
                # Login the user if account is valid and active
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your account has been deactivated')
        # Bad login details
        else:
            print "Invalid login details: %s, %s" % (username, password)

            # Django built in messages framework for a message that will last a single refresh
            # if incorrect login details
            messages.error(request, '>>> Error! Incorrect username or password. <<<')
            return HttpResponseRedirect('/rango/login/')

    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    # Since we know that the user is logged in, simply log them out
    logout(request)

    # Show the homepage
    return HttpResponseRedirect('/rango/')







