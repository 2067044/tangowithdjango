from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm


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
    return render(request, 'rango/about.html')


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




