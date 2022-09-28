from http.client import HTTPResponse
from django.shortcuts import render

def index(request):
    return render(request, 'calculator/index.html')

def calculate(request):
    return render(request, 'calculator/calculator.html')

#def calculate(request):
    #q = request.GET['query']
    #return HTTPResponse('q')
