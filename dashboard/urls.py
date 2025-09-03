from django.urls import path
from . import views 

urlpatterns = [
#    //path('', views.login_page, name='account'), 
    path('',views.dashboard_page,name='dashboard'),
    path("ai_page/",views.ai_page,name='ai_page'),
    path("bias_detector/",views.bias_detector,name='bias_detector'),
    path("fact/",views.fact,name="fact"),
]