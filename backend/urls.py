from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('fetch-stock-data/', views.get_data, name='fetch_stock_data'),
    path('findAll/', views.find_all, name='findAll'),
    path('validate/',views.validate,name='validate'),
]
