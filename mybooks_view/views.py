from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
import django.contrib.auth.urls
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from .forms import LoginForm, LogoutForm


def login(request):
    """
    Presents login form
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            payload = {'email': request.POST['username'], 'password': request.POST['password']}
            auth_url='https://mybook.ru/api/auth/'
            auth_response = requests.post(auth_url, payload)
            if auth_response.status_code == 200:
                response = HttpResponseRedirect(reverse('books'))
                response.set_cookie('session', value=auth_response.cookies['session'])
                response.set_cookie('csrftoken', value=auth_response.cookies['csrftoken'])
                response.set_cookie('uid', value=auth_response.cookies['uid'])
                return response
            else:
                form = LoginForm(request.POST)
                form.add_error('password',  auth_response.text)
            
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def logout(request):
    """
    Presents logout form
    """
    if request.method == 'POST':
        response = HttpResponseRedirect(reverse('login'))
        response.delete_cookie('session')
        response.delete_cookie('uid')
        return response
    else:
        form = LogoutForm()
    return render(request, 'registration/logged_out.html', {'form': form})


def books_list(request):
    """
    Presents list of books from https://mybook.ru/api/bookuserlist/
    """
    def build_booklist(books_responce):
        """
        Builds information from API responce to custom dict
        """
        result = []
        if books_responce.json()['objects']:
            for entry in books_responce.json()['objects']:
                result.append(
                    {
                        'name': entry['book']['name'],
                        'author': entry['book']['authors_names'],
                        'cover': entry['book']['default_cover'],
                    }
                )
            return result
        else:
            return None
    
    def get_booklist(cookies, next_page_flag=False, next_page=None):
        """
        Recursively gets books from https://mybook.ru/api/bookuserlist/ 
        until responce have ['meta']['next']
        :param cookies: authentication cookies
        :type cookies: dict
        :param next_page_flag: flag for get_net_page mode
        :type next_page_flag: bool
        :param next_page: url for next page
        :type next_page: str
        """
        site_name = 'https://mybook.ru'
        headers = {'Accept': 'application/json; version=5'}
        books_url = site_name + '/api/bookuserlist/'
        result = []
        if next_page_flag:
            books_response = requests.get(next_page, cookies=cookies, headers=headers)
            result += build_booklist(books_response)
        else:
            books_response = requests.get(books_url, cookies=cookies, headers=headers)
            result += build_booklist(books_response)
        if books_response.json()['meta']['next']:
            next_page_url = site_name + books_response.json()['meta']['next']
            result += get_booklist(cookies, next_page_flag=True, next_page=next_page_url)
        if books_response.status_code == 200:
            return result
        else:
            return -1

    session = request.COOKIES.get('session')
    csrftoken = request.COOKIES.get('csrftoken')
    uid = request.COOKIES.get('uid')
    if session and csrftoken and uid:
        cover_url = 'https://i1.mybook.io/c/88x128/'
        books_list = get_booklist({'session': session, 'csrftoken': csrftoken, 'uid': uid})
        if books_list == -1:
            response = HttpResponseRedirect(reverse('login'))
            response.delete_cookie('session')
            response.delete_cookie('uid')
            return response
        else:
            return render(
                request,
                'index.html',
                context={'books_list': books_list, 'cover_url': cover_url},
            )
    else:
        response = HttpResponseRedirect(reverse('login'))
        response.delete_cookie('session')
        response.delete_cookie('uid')
        return response
