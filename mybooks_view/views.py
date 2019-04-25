from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
import requests


#@login_required
class BookListView(generic.ListView):
    #model = Book

    def get_queryset(self):
        pass


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
            result += get_booklist(cookies, next_page_flag=True, next_page=books_responce['meta']['next'])
        return result


    payload = {'email': 'gorkycow@gmail.com', 'password': '!QAZ2wsx'}
    auth_url='https://mybook.ru/api/auth/'
    auth_response = requests.post(auth_url, payload)
    cover_url = 'https://i1.mybook.io/c/88x128/'
    
    books_list = get_booklist(auth_response.cookies)


    return render(
        request,
        'index.html',
        context={'books_list': books_list, 'cover_url': cover_url},
    )
