from django.urls import path

from . import views
from .views import MyLoginView
from django.contrib.auth.views import LogoutView

app_name = 'SPR'
urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='SPR:login'), name='logout'),
    path("", views.index, name="index"),
    path("full_operations_page/", views.full_operations_page, name="full_operations_page"),
    path("full_operations_list_update/", views.full_operations_list_update, name="full_operations_list_update"),
    path("cur_operations_page/", views.cur_operations_page, name="cur_operations_page"),
    path("cur_operations_list_update/<week>/", views.cur_operations_list_update, name="cur_operations_list_update"),
    path("update_operation_status/<sch_operation_id>/<status>/", views.update_operation_status, name="update_operation_status"),
    path("repair_operations_editor/<operation_id>/<field>/<data>/", views.repair_operations_editor, name="repair_operations_editor"),
    path("sch_repair_operations_editor/<operation_id>/<field>/<data>/", views.sch_repair_operations_editor, name="sch_repair_operations_editor")
]