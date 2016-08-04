from django.conf.urls import url
from front import views

urlpatterns = [
    url('^', views.Index.as_view()),
]
