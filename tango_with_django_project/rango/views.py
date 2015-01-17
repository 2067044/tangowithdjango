from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    response_text = '<h1> Rango says hey there world </h1>' \
                    '<h3><a href="/rango/about/">About page</a></h3>'
    return HttpResponse(response_text)


def about(request):
    response_text = '<h1>Rango says here is the about page</h1>' \
                    '<h2>This tutorial has been put together by Kristian Sonev, 2067044</h2>' \
                    '<h3><a href="/rango/">Home</a></h3>'
    return HttpResponse(response_text)

