from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
import django.contrib.auth.urls
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from .forms import LoginForm


#@login_required
class ModifyLoginView(views.LoginView):
    #model = Book

    def get_queryset(self):
        pass


def login(request):
    
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
            elif auth_response.status_code == 400:
                pass
            
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


#@login_required
def books_list(request):
    """
    Presents list of books from https://mybook.ru/api/bookuserlist/
    """
    # Генерация "количеств" некоторых главных объектов
    #num_books=Book.objects.all().count()
    #num_instances=BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    #num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    #num_authors=Author.objects.count()  # Метод 'all()' применен по умолчанию.
    
    # Отрисовка HTML-шаблона index.html с данными внутри 
    # переменной контекста context
    def build_booklist(books_responce):
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
        headers = {'Accept': 'application/json; version=5'}
        books_url = 'https://mybook.ru/api/bookuserlist/'
        result = []
        if next_page_flag:
            books_responce = requests.get(next_page, cookies=cookies, headers=headers)
            result += build_booklist(books_responce)
        else:
            books_responce = requests.get(books_url, cookies=cookies, headers=headers)
            result += build_booklist(books_responce)
        if books_responce.json()['meta']['next']:
            next_page_url = books_url + books_responce['meta']['next']
            result += get_booklist(cookies, next_page_flag=True, next_page=next_page_url)
        return result

    session = request.COOKIES.get('session')
    csrftoken = request.COOKIES.get('csrftoken')
    uid = request.COOKIES.get('uid')
    #payload = {'email': 'gorkycow@gmail.com', 'password': '!QAZ2wsx'}
    #auth_url='https://mybook.ru/api/auth/'
    #auth_response = requests.post(auth_url, payload)
    cover_url = 'https://i1.mybook.io/c/88x128/'
    
    books_list = get_booklist({'session': session, 'csrftoken': csrftoken, 'uid': uid})


    return render(
        request,
        'index.html',
        context={'books_list': books_list, 'cover_url': cover_url},
    )
