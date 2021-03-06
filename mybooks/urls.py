"""mybooks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views
from mybooks_view import views as myviews


urlpatterns = [
    path('admin/', admin.site.urls),
    path('books_list/', include('mybooks_view.urls'), name='books_list'),
    path('', RedirectView.as_view(url='/books_list/', permanent=True)),
    path('accounts/login/', myviews.login, name='login'),
    path('accounts/logout/', myviews.logout, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
