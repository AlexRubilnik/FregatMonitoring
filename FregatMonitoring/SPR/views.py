from django.shortcuts import render
from django.template import loader
import datetime
from datetime import date, timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models import Q

from django.http import HttpResponse, JsonResponse
from .models import Locations, Equipment, Nodes, Sections, Works, Staff_positions, Repair_staff, Repair_schedule, Repair_schedule_fact, Scheduled_operations


def getRepairStaff_by_user(user):
    staff = Repair_staff.objects.get(username=user)
    return staff


class MyLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('SPR:index') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Неправильное имя пользователя или пароль!')
        return self.render_to_response(self.get_context_data(form=form))


@login_required
def index(request):
    staff = getRepairStaff_by_user(request.user)

    if staff.position.name.split(' ')[0] in ('Слесарь', 'Мастер', 'Инженер'):
        return cur_operations_page(request)
    elif staff.position.name.split('  ')[0] in('Зам. тех директора по АСУиИТ',):
        return full_operations_page(request)


@login_required
def full_operations_page(request):
    '''Отображует страницу с полным списком оборудования и работ по каждому узлу каждой единицы оборудования'''
    staff = getRepairStaff_by_user(request.user)
    template = loader.get_template('SPR/full_operations_list_page.html')
    context={'user_staff': staff}
    return HttpResponse(template.render(context, request))


@login_required
def cur_operations_page(request):
    '''Отображует страницу со списком работ, запланированных для данного пользователя на эту неделю'''
    cur_year, cur_week, cur_day = datetime.datetime.now().isocalendar()  #return tuple(year, week, weekday)
    if cur_day != 1:
        start_cur_week_date = datetime.datetime.now() - datetime.timedelta(days = cur_day-1)  
    else:
        start_cur_week_date = datetime.datetime.now()
    finish_cur_week_date = start_cur_week_date + datetime.timedelta(days = 6)
    staff = getRepairStaff_by_user(request.user)
    template = loader.get_template('SPR/cur_operations_page.html')
    context={'user_staff': staff,
             'week': cur_week,
             'start_date': start_cur_week_date.strftime('%d.%m.%Y'),
             'finish_date': finish_cur_week_date.strftime('%d.%m.%Y')}
    return HttpResponse(template.render(context, request))


@login_required
def full_operations_list_update(request, mode):
    '''Загружает весь график ППР'''
    cur_year, cur_week, cur_day = datetime.datetime.now().isocalendar()  #return tuple(year, week, weekday)
    works = Works.objects.all()

    full_eqp_list = []
    for work in works:
        node = Nodes.objects.get(id=work.node.id)
        sect = Sections.objects.get(id=node.section.id)
        eqp = Equipment.objects.get(id=sect.equipment.id)
        loc = Locations.objects.get(id=eqp.location.id)
        staff_pos = Staff_positions.objects.get(id=work.staff_position.id)
        week_cols_plan=dict()
        week_cols_fact=dict()
        week_cols_mix=dict()
        try:
            weeks_plan = Repair_schedule.objects.get(operation=work) 
            weeks_fact = Repair_schedule_fact.objects.get(operation=work) 
            for i in range(1, 53): 
                week_plan = getattr(weeks_plan, f'_{i}')
                week_fact = getattr(weeks_fact, f'_{i}')
                if mode =='plan':
                    if  week_plan == 1:
                        week_cols_plan[f'_{i}'] = 'yellow'
                    else:
                        week_cols_plan[f'_{i}'] = 'white'
                if mode == 'mix':
                    if week_plan == 1: 
                        wp = "y"
                    else:
                        wp = "w"
                    
                    if week_fact == 0:
                        wf = "w"
                    elif week_fact == 1:
                        wf = "y"
                    elif week_fact == 2:
                        wf = "gr"
                    else:
                        wf = "r"
                    
                    week_cols_mix[f'_{i}'] = f'{wp}_{wf}'

        except: #нету графика для этой операции
            for i in range(0,52):
                week_cols_plan[f"_{i+1}"]="white"
                week_cols_fact[f"_{i+1}"]="white"
                week_cols_mix[f"_{i+1}"]="w_w"

        if mode == 'plan':
            week_cols = week_cols_plan
        elif mode == 'fact':
            week_cols = week_cols_fact
        elif mode == 'mix':
            week_cols = week_cols_mix
        full_eqp_list.append({**{"id" : work.id,
                              "loc": loc.name, 
                              "eqp": eqp.name, 
                              "sect": sect.name, 
                              "node": node.name, 
                              "staff_pos": staff_pos.name,
                              "per": work.periodicity_days,
                              "tools": work.tools,
                              "risk": work.risk,
                              "work": work.operation_content,
                              "last": work.last_service,
                              "next": work.next_service},**week_cols})

    return JsonResponse(full_eqp_list, safe=False)


@login_required
def cur_operations_list_update(request, week):
    '''Загружает задания по графику ППР для данного пользователя на текущую неделю'''
    
    cur_year, cur_week, cur_day = datetime.datetime.now().isocalendar()  #return tuple(year, week, weekday)
    delta_week = cur_week - int(week) 
    if cur_day != 1:
        start_cur_week_date = datetime.datetime.now() - datetime.timedelta(days = cur_day-1)  #текущая неделя
        start_asked_week_date = datetime.datetime.now() - datetime.timedelta(days = cur_day-1+(delta_week*7))  #неделя, которую смотрит пользователь
    else:
        start_cur_week_date = datetime.datetime.now()
        start_asked_week_date = datetime.datetime.now() - datetime.timedelta(days = delta_week*7) 
    finish_cur_week_date = start_cur_week_date + datetime.timedelta(days = 6)    
    finish_asked_week_date = start_asked_week_date + datetime.timedelta(days = 6)

    start_cur_year = Q(start_date__gte=f'{cur_year-1}-12-25')
    finish_last_week = Q(finish_date__lt=start_cur_week_date)
    expired = Q(current_status=0)
    #Запрашиваем все просроченные операии за все недели этого года, предшествующие текущей
    expired_operations=Scheduled_operations.objects.filter(start_cur_year & finish_last_week & expired) #Все пророченные работы по графику ППР, запланированные на предыдущие недели этого года
    for op in expired_operations:
        op.current_status = 3   #Если у операции стоит статус 0(ожидает выполнения), меняем статус на "просрочена"
        op.save()
        sch_fact = Repair_schedule_fact.objects.get(operation_id=op.operation.id) 
        op_year, op_week, op_day = op.start_date.isocalendar() #на какую неделю запланирована операция
        if getattr(sch_fact, f'_{op_week}') != 3:
            setattr(sch_fact, f'_{op_week}', 3) #меняем статус в фактическом графике ППР
            sch_fact.save()

    operations = Repair_schedule.objects.all()
    for operation in operations: 
        op = getattr(operation, f'_{week}')
        if op ==1 : #ищем работы, которые нужно запланировать на запрашиваемую пользователем неделю
            if len(Scheduled_operations.objects.filter(operation=operation.operation, start_date=start_asked_week_date)) == 0: #если работы ещё нет в запланированных
                sch_op = Scheduled_operations(operation=operation.operation, start_date=start_asked_week_date, finish_date=finish_asked_week_date) #создаём экземпляр в запланированных работах
                sch_op.save()
            else:
                sch_op = Scheduled_operations.objects.get(operation=operation.operation, start_date=start_asked_week_date)
                if sch_op.current_status == 1: #если выполняется
                    print(sch_op.start_timestamp)
                    print(datetime.datetime.now(timezone.utc))
                    elapsed_time = round((datetime.datetime.now(timezone.utc) - sch_op.start_timestamp ).total_seconds()/60)
                    sch_op.elapsed_time_min = elapsed_time
                    sch_op.save()

    sch_operations = Scheduled_operations.objects.filter(start_date = start_asked_week_date) #Все работы по графику ППР, запланированные на просматриваемую пользователем неделю
    full_eqp_list = []
    for op in sch_operations:
        work = op.operation
        node = Nodes.objects.get(id=work.node.id)
        sect = Sections.objects.get(id=node.section.id)
        eqp = Equipment.objects.get(id=sect.equipment.id)
        loc = Locations.objects.get(id=eqp.location.id)
        staff_pos = Staff_positions.objects.get(id=work.staff_position.id)
        try:
            staff = op.staff.name+" "+op.staff.surname
        except:
            staff = ""
        
        start_ts = datetime.datetime.strftime(op.start_timestamp+datetime.timedelta(hours=3), "%d-%m-%Y %H:%M:%S") if op.start_timestamp is not None else None
        finish_ts = datetime.datetime.strftime(op.finish_timestamp+datetime.timedelta(hours=3), "%d-%m-%Y %H:%M:%S") if op.finish_timestamp is not None else None
        full_eqp_list.append({"sch_op_id": op.id,
                              "id" : work.id,
                              "loc": loc.name, 
                              "eqp": eqp.name, 
                              "sect": sect.name, 
                              "node": node.name, 
                              "staff_pos": staff_pos.name,
                              "staff": staff,
                              "tools": work.tools,
                              "work": work.operation_content,
                              "status" : op.current_status,
                              "comment": op.comment,
                              "start_timestamp": start_ts,
                              "finish_timestamp": finish_ts})

    return JsonResponse(full_eqp_list, safe=False)


@login_required
def update_operation_status(request, sch_operation_id, week, status):
    '''Меняет статус выполнения запланированных операций'''
    staff = getRepairStaff_by_user(request.user)
    sch_op = Scheduled_operations.objects.get(id=sch_operation_id)
    if sch_op.staff==None or staff == sch_op.staff:
        if status == 'start':
            sch_op.start_timestamp = datetime.datetime.now(timezone.utc)
            sch_op.staff = staff
            sch_op.current_status = 1
        elif status == 'cancel':
            sch_op.start_timestamp = None
            sch_op.finish_timestamp = None
            sch_op.elapsed_time_min = None
            sch_op.staff = None
            sch_op.current_status = 0
        elif status == 'finish':
            sch_op.finish_timestamp = datetime.datetime.now(timezone.utc)
            elapsed_time = round((datetime.datetime.now(timezone.utc) - sch_op.start_timestamp ).total_seconds()/60)
            sch_op.elapsed_time_min = elapsed_time
            sch_op.current_status = 2
            sch_fact = Repair_schedule_fact.objects.get(operation_id=sch_op.operation.id) 
            setattr(sch_fact, f'_{week}', 2) #меняем статус в фактическом графике ППР
            sch_fact.save()
        sch_op.save()
        return HttpResponse("available")
    
    return HttpResponse(f"{sch_op.staff.name.split(' ')[0]} {sch_op.staff.surname.split(' ')[0]}")


@login_required
def repair_operations_editor(request, operation_id, field, data):
    '''Получает и пишет в БД изменения в графике ППР'''
    op = Works.objects.get(id=operation_id)
    if field == 'risk':
        op.risk = data
    if field == 'per':
        op = Works.objects.get(id=operation_id)
        op.periodicity_days = data
    if field == 'tools':
        op = Works.objects.get(id=operation_id)
        op.tools = data
    if field == 'work':
        op = Works.objects.get(id=operation_id)
        op.operation_content = data
    if field[0] == '_':
        try:
            op = Repair_schedule.objects.get(operation=op)
        except:
            op = Repair_schedule(operation=op)
        if data == 'white':
            exec(f'op.{field} = 0')
        elif data == 'yellow':
            exec(f'op.{field} = 1')
    op.save()
    return HttpResponse(request)


@login_required
def sch_repair_operations_editor(request, operation_id, field, data):
    '''Получает и пишет в БД изменения в выполняемых операциях'''
    op = Scheduled_operations.objects.get(id=operation_id)
    if field == 'comment':
        op.comment = data
        
    op.save()
    return HttpResponse(request)


@login_required
def week_report_page(request):
    '''Отображает страницу отчёта за предыдущую неделю'''
    template = loader.get_template('SPR/week_report_page.html')
    staff = getRepairStaff_by_user(request.user)

    cur_year, cur_week, cur_day = datetime.datetime.now().isocalendar()  #return tuple(year, week, weekday)
    start_last_week_date = datetime.datetime.now() - datetime.timedelta(days = cur_day-1+7)  
    finish_last_week_date = start_last_week_date + datetime.timedelta(days = 6)

    operations = Scheduled_operations.objects.filter(start_date=start_last_week_date)
    op_scheduled = operations
    op_completed = [op for op in operations if op.current_status==2]
    elapsed_time = sum([op.elapsed_time_min for op in op_completed])
    num_of_staff = len(set([op.staff for op in op_completed]))

    context={'user_staff': staff,
             'week': cur_week-1,
             'start_date':  start_last_week_date.strftime('%d.%m.%Y'),
             'finish_date': finish_last_week_date.strftime('%d.%m.%Y'),
             'op_scheduled': len(op_scheduled),
             'op_completed': len(op_completed),
             'elapsed_time': elapsed_time,
             'num_of_staff': num_of_staff
            }
    return HttpResponse(template.render(context, request))


@login_required
def uncompleted_list_update(request, week):
    cur_year, cur_week, cur_day = datetime.datetime.now().isocalendar()  #return tuple(year, week, weekday)
    delta_week = cur_week - int(week)
    start_week_date = datetime.datetime.now() - datetime.timedelta(days = cur_day-1+(7*delta_week))  
    operations = Scheduled_operations.objects.filter(start_date=start_week_date)
    op_scheduled = operations
    op_completed = [op for op in operations if op.current_status==2] #выполненные
    elapsed_time = sum([op.elapsed_time_min for op in op_completed])
    num_of_staff = len(set([op.staff for op in op_completed]))
    context={'op_scheduled': len(op_scheduled),
             'op_completed': len(op_completed),
             'elapsed_time': elapsed_time,
             'num_of_staff': num_of_staff
            }
    ops = [op for op in operations if op.current_status!=2] #просроченные
    ops_list=[]
    for op in ops:
        work = op.operation
        node = Nodes.objects.get(id=work.node.id)
        sect = Sections.objects.get(id=node.section.id)
        eqp = Equipment.objects.get(id=sect.equipment.id)
        loc = Locations.objects.get(id=eqp.location.id)
        ops_list.append({"sch_op_id": op.id,
                        "id" : work.id,
                        "loc": loc.name, 
                        "eqp": eqp.name, 
                        "sect": sect.name, 
                        "node": node.name, 
                        "work": work.operation_content,
                        "status" : op.current_status,
                        "comment": op.comment,
                        })

    return JsonResponse([ops_list, context], safe=False)