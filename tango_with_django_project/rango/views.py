from django.shortcuts import render
from rango.models import Category
from rango.models import Page


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
    except Category.DoesNotExist:
        # Do nothing here
        pass

    return render(request, 'rango/category.html', context_dict)
