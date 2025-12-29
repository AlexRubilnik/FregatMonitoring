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
    path("full_operations_list_update/<mode>/", views.full_operations_list_update, name="full_operations_list_update"),
    path("cur_operations_page/", views.cur_operations_page, name="cur_operations_page"),
    path("cur_operations_list_update/<week>/", views.cur_operations_list_update, name="cur_operations_list_update"),
    path("update_operation_status/<sch_operation_id>/<week>/<status>/", views.update_operation_status, name="update_operation_status"),
    path("repair_operations_editor/<operation_id>/<field>/<data>/", views.repair_operations_editor, name="repair_operations_editor"),
    path("sch_repair_operations_editor/<operation_id>/<field>/<data>/", views.sch_repair_operations_editor, name="sch_repair_operations_editor"),
    path("week_report_page/", views.week_report_page, name="week_report_page"),
    path("uncompleted_list_update/<week>/", views.uncompleted_list_update, name="uncompleted_list_update"),
    path("equipment_journal_page/", views.equipment_journal_page, name="equipment_journal_page"),
    path("equipment_service_page/", views.equipment_service_page, name="equipment_service_page"),
    path("update_equipment_tree/<loc>/<eqp>/<sect>/<node>/",views.update_equipment_tree, name="update_equipment_tree"),
    path("last_operations_list/<loc>/<eqp>/<sect>/<node>/", views.last_operations_list, name="last_operations_list"),
    path("add_new_repair_operation_to_bd/", views.add_new_repair_operation_to_bd, name="add_new_repair_operation_to_bd"),
    path("delete_repair_operation_from_bd/<op_id>/", views.delete_repair_operation_from_db, name="delete_repair_operation_from_db"),
    path("add_new_entity_to_bd/", views.add_new_entity_to_bd, name="add_new_entity_to_bd"),
    path("delete_entity_from_db/<entity_type_str>/<ent_id>/", views.delete_entity_from_db, name="delete_entity_from_db"),
]