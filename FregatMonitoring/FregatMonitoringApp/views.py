from ast import Str
from calendar import month
from datetime import datetime, timedelta, date
import itertools
from multiprocessing import context
from os import curdir 

from django.db.models.query_utils import subclasses
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.db.models import F
from django.shortcuts import get_object_or_404

from .models import Automelts, Avtoplavka_status, Avtoplavka_setpoints, Autoplavka_log, AutoMeltsInfo, Daily_gases_consumption 
from .models import Floattable, Gases_consumptions_per_day, Melttypes, Meltsteps, Substeps, Tagtable, Rarefaction_P2, Bottling
from .models import CurrentBottling, Furnace1_errors_log, Furnace2_errors_log, Melts
from .serializers import FloattableSerializer, AutomeltsSerializer, RarefactionP2Serializer

from . import furnace_errors
from .furnace_errors import furnace1_errors_list, furnace2_errors_list

class MyLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('FregatMonitoringApp:index') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Неправильное имя пользователя или пароль!')
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def index(request):
    return furnace_1_info(request)

@login_required
def reports_page(request):
    template = loader.get_template('FregatMonitoringApp/reports_page.html')
    context = None

    return HttpResponse(template.render(context, request))

@login_required
def gases_usage_report(request, **kwards): #Загружает первоначальный шаблон отчёт с данными по умолчанию   
    template = loader.get_template('FregatMonitoringApp/gases_usage_report.html')
    
    if(kwards.get('report_type') == 'gases_usage_daily'): #Выбран посуточный отчёт
        start_period = (datetime.now()-timedelta(hours=30*24) ).strftime('%Y-%m-%dT%H:%M')#предыдущий месяц
        stop_period = datetime.now().strftime('%Y-%m-%dT%H:%M')#текущий момент
    elif(kwards.get('report_type') == 'gases_usage_per_day'): #Выбран почасовой отчёт
        start_period = (datetime.now()-timedelta(hours=24)).replace(hour=8,minute=0).strftime('%Y-%m-%dT%H:%M')#предыдущие сутки c 8.00
        stop_period = datetime.now().replace(hour=8,minute=0).strftime('%Y-%m-%dT%H:%M')#текущие сутки до 8.00
 
    context={
        'report_type': kwards.get('report_type'),
        'Start_time': start_period,
        'Stop_time': stop_period,
    }

    return HttpResponse(template.render(context, request))

@login_required
def get_gases_usage_data_hourly(request, **kwards):
    '''Выдаёт данные по запросу клиента за выбранный период по часам. 
       Считает почасовые расходы газов, на основе данных о мгновенных расходах, которые регистрируются в таблице БД FloatTable каждые 10 секунд'''
    
    if request.method == 'GET':
        start_period = datetime.strptime(request.GET['start'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') 
        stop_period = datetime.strptime(request.GET['stop'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') 
    
    def hourly_db_request(tag_name: Str, start_per, stop_per): #запрос к БД для подсчёта почасового расхода газа(или кислорода) за период
        tag_ind = Tagtable.objects.filter(tagname=tag_name)[0].tagindex #индекс интересующего сигнала
        response_1 = Gases_consumptions_per_day.objects.raw(
            ''' SELECT ROW_NUMBER() OVER(ORDER BY CONCAT(DATEFROMPARTS(DATEPART(year, CAST(DTm AS datetime)), DATEPART(month, CAST(DTm AS datetime)), 
					                                                   DATEPART(day, CAST(DTm AS datetime))
							                                          ), ' ', DATEPART(hour, CAST(DTm AS datetime)),':59')) AS id, 
                       CONCAT(DATEFROMPARTS(DATEPART(year, CAST(DTm AS datetime)), DATEPART(month, CAST(DTm AS datetime)), 
					                        DATEPART(day, CAST(DTm AS datetime))
							               ), ' ', DATEPART(hour, CAST(DTm AS datetime)),':59') AS data, 
                       SUM(TimeDiffVal) AS consumption,
                       (CASE TagName  
                          WHEN 'MEASURES\FL710_NG' THEN 'Gas_P1'
                          WHEN 'MEASURES\TI_810B' THEN 'Gas_P2'
                          WHEN 'MEASURES\O1Flow' THEN 'O2_P1'
                          WHEN 'MEASURES\O2Flow' THEN 'O2_P2'
                          WHEN 'MEASURES\OX_OX800' THEN 'O2_Furma'
                       END) AS GasName 

                FROM(
                     SELECT DATEADD(ms,Millitm,DateAndTime) AS DTm,
                            TagIndex, 
                            (CAST(Val as float)/3600)*DATEDIFF(MILLISECOND,
                                                               DateAdd(ms,Millitm,DateAndTime),
            	                                               DateAdd(ms,
                                                                       LAG(Millitm,1,NULL) OVER (PARTITION BY TagIndex ORDER BY DateAndTime DESC),
            			                                               LAG(DateAndTime,1,NULL) OVER (PARTITION BY TagIndex ORDER BY DateAndTime DESC)
            			                                               )
            	                                               )/1000 as TimeDiffVal
                     FROM [FRGV202X\Production].[FX_Hist].[db_owner].[FloatTable]
                     WHERE TagIndex=%s  AND DateAndTime > %s AND DateAndTime < %s
                     ) a            
                INNER JOIN [FRGV202X\Production].[FX_Hist].[db_owner].[TagTable] b ON a.TagIndex=b.TagIndex
                GROUP BY TagName, CONCAT(DATEFROMPARTS(DATEPART(year, CAST(DTm AS datetime)), DATEPART(month, CAST(DTm AS datetime)), 
					                     DATEPART(day, CAST(DTm AS datetime))
							            ), ' ', DATEPART(hour, CAST(DTm AS datetime)),':59')
                ORDER BY TagName, CAST(CONCAT(DATEFROMPARTS(DATEPART(year, CAST(DTm AS datetime)), DATEPART(month, CAST(DTm AS datetime)), 
					                    DATEPART(day, CAST(DTm AS datetime))
							            ), ' ', DATEPART(hour, CAST(DTm AS datetime)),':59') AS datetime);'''
        , [tag_ind, start_per, stop_per])

        return response_1


    gas_furnace_1_consumption = hourly_db_request('MEASURES\FL710_NG', start_period, stop_period)
    gas_furnace_2_consumption = hourly_db_request('MEASURES\TI_810B', start_period, stop_period)
    o2_furnace_1_consumption = hourly_db_request('MEASURES\O1Flow', start_period, stop_period)
    o2_furnace_2_consumption = hourly_db_request('MEASURES\O2Flow', start_period, stop_period)
    furma_consumption = hourly_db_request('MEASURES\OX_OX800', start_period, stop_period)

    consumptions = list()
    consumptions.append(("furnace_1_Gas", gas_furnace_1_consumption))
    consumptions.append(("furnace_1_O2", o2_furnace_1_consumption))
    consumptions.append(("furnace_2_Gas", gas_furnace_2_consumption))
    consumptions.append(("furnace_2_O2", o2_furnace_2_consumption))
    consumptions.append(("furma", furma_consumption ))

    series = list()
    for i in range(len(consumptions)):
        series.append([[consumptions[i][0]], []])
        for j in range(0, len(consumptions[i][1])):
            point={"date":str(consumptions[i][1][j].data), "value":round(consumptions[i][1][j].consumption, 2)}
            series[i][1].append(point)

    return JsonResponse(series, safe=False)
    
@login_required
def get_gases_usage_data_daily(request, **kwards):
    '''Выдаёт данные по запросу клиента за выбранный период по дням. Достаёт данные из заранее подготовленной таблицы в БД: DailyGasesConsumption.
       Таблица содержит суточные расходы газов, рассчитанные (на основе данных о мгновенных расходах) хранимой процедурой по заданию ежедневно в 23:59'''
      
    if request.method == 'GET':
        start_period = datetime.strptime(request.GET['start'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d') 
        stop_period = datetime.strptime(request.GET['stop'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d') 
    else:    
        start_period = (datetime.now()-timedelta(hours=30*24) ).strftime('%Y-%m-%d')#предыдущий месяц
        stop_period = datetime.now().strftime('%Y-%m-%d')#текущий момент
    
    gas_furnace_1_consumption = Daily_gases_consumption.objects.filter(gasname = 'Gas_P1').filter(data__range=(start_period,stop_period)).order_by('data')
    gas_furnace_2_consumption = Daily_gases_consumption.objects.filter(gasname = 'Gas_P2').filter(data__range=(start_period,stop_period)).order_by('data')
    o2_furnace_1_consumption = Daily_gases_consumption.objects.filter(gasname = 'O2_P1').filter(data__range=(start_period,stop_period)).order_by('data')
    o2_furnace_2_consumption = Daily_gases_consumption.objects.filter(gasname = 'O2_P2').filter(data__range=(start_period,stop_period)).order_by('data')
    furma_consumption = Daily_gases_consumption.objects.filter(gasname = 'O2_Furma').filter(data__range=(start_period,stop_period)).order_by('data')

    consumptions = list()
    consumptions.append(("furnace_1_Gas", gas_furnace_1_consumption))
    consumptions.append(("furnace_1_O2", o2_furnace_1_consumption))
    consumptions.append(("furnace_2_Gas", gas_furnace_2_consumption))
    consumptions.append(("furnace_2_O2", o2_furnace_2_consumption))
    consumptions.append(("furma", furma_consumption ))

    series = list()
    for i in range(len(consumptions)):
        series.append([[consumptions[i][0]], []])
        for j in range(0, len(consumptions[i][1])):
            ts = datetime.strptime(str(consumptions[i][1][j].data), "%Y-%m-%d")
            point={"date":str(consumptions[i][1][j].data), "timestamp":ts.timestamp()*1000, "value":round(consumptions[i][1][j].daily_consumption, 2)}
            point={"date":str(consumptions[i][1][j].data), "value":round(consumptions[i][1][j].daily_consumption, 2)}
            series[i][1].append(point)

    return JsonResponse(series, safe=False)

@login_required
def furnace_base_trends(request, furnace_no, **kwards):  #отображает шаблон экрана трендов для печи
    template = loader.get_template('FregatMonitoringApp/furnace_trends_page.html')
    if(kwards.get('start_time') is not None and kwards.get('stop_time') is not None):
        start_period = kwards.get('start_time') 
        stop_period = kwards.get('stop_time')
    else:    
        start_period = (datetime.now()-timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')#предыдущий час
        stop_period = datetime.now().strftime('%Y-%m-%dT%H:%M')#текущий момент
    context = {
        'Furnace_No': furnace_no,
        'Start_time': start_period,
        'Stop_time': stop_period
    }
    return HttpResponse(template.render(context, request))

@login_required
def furnace_errors_log(request, furnace_no, **kwards): #отображает шаблон журнала ошибок для печи
    template = loader.get_template('FregatMonitoringApp/furnace_errors_log_page.html')
    if(kwards.get('start_time') is not None and kwards.get('stop_time') is not None):
        start_period = kwards.get('start_time') 
        stop_period = kwards.get('stop_time')
    else:    
        start_period = (datetime.now()-timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')#предыдущий час
        stop_period = datetime.now().strftime('%Y-%m-%dT%H:%M')#текущий момент
    context = {
        'Furnace_No': furnace_no,
        'Start_time': start_period,
        'Stop_time': stop_period
    }
    return HttpResponse(template.render(context, request))

@login_required
def furnace_errors_log_data(request, furnace_no):
    if request.method == 'GET':
        start_period = request.GET['start']
        stop_period = request.GET['stop']

    start_period = datetime.strptime(start_period, '%Y-%m-%dT%H:%M')
    stop_period = datetime.strptime(stop_period, '%Y-%m-%dT%H:%M')

    def load_furnace_errors_log_by_period(furnace_no, period_start, period_stop, **kwards):
        #возвращает ошибки по печи за определённый период времени
        if furnace_no == 1:
            errors_arr = Furnace1_errors_log.objects.filter(timestamp__range=(period_start,period_stop)).order_by('timestamp')
        elif furnace_no == 2:
            errors_arr = Furnace2_errors_log.objects.filter(timestamp__range=(period_start,period_stop)).order_by('timestamp')
        return errors_arr

    log_strings = list()
    err_query = load_furnace_errors_log_by_period(furnace_no, start_period, stop_period)

    for i in range(len(list(err_query))):
        try: #приведение метки времени в красивый вид
            #защита от ситуации, когда %f(миллисекунды в дате) = .0000. Тогда БД возвращает дату без них и не совпадает формат
            timestamp = datetime.strptime(str(err_query[i].timestamp), '%Y-%m-%d %H:%M:%S.%f+00:00').strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = datetime.strptime(str(err_query[i].timestamp), '%Y-%m-%d %H:%M:%S+00:00').strftime("%Y-%m-%d %H:%M:%S")
        
        if furnace_no == 1:
            errors = furnace1_errors_list(err_query[i])
        elif furnace_no == 2:
            errors = furnace2_errors_list(err_query[i])
        
        for j in range(len(errors)):
            log_strings.append({
                        "timestamp" : timestamp,
                        "error" : errors[j],
                        "ng_press" : err_query[i].ng_press,
                        "o2_press" : err_query[i].o2_press,
                        "ng_flow" : err_query[i].ng_flow,
                        "o2_flow" : err_query[i].o2_flow,
                        "air_flow" : err_query[i].air_flow,
            })

    return JsonResponse(log_strings, safe=False)

@login_required
def furnace_base_trends_data(request, furnace_no): #готовит и отправляет данные сигналов для трендов за указанный период времени
    if request.method == 'GET':
        start_period = request.GET['start']
        stop_period = request.GET['stop']

    def LoadSignalValuesByPeriod(signal_name, period_start, period_stop, **kwards):
        #возвращает выборку значений сигналов с метками времени за определённый период времени
        minus_mod = kwards.get('minus') if kwards.get('minus') is not None else 0 #опция для сигналов положения дросселей, которые нужно дешифровать, отнимая определённое число
        signal_value = Floattable.objects.annotate(value=F('val')-minus_mod).filter(
                        tagindex=Tagtable.objects.filter(tagname=signal_name)[0].tagindex
                        ).filter(dateandtime__range=(period_start,period_stop)).order_by('dateandtime')
        return signal_value

    def LoadRarefactionValuesByPeriod(furnace_no, rarefaction_point_name, period_start, period_stop, **kwards):
        #возвращает выборку значений разряжений с метками времени за определённый период времени
        #if furnace_no == 2: - раскомментировать, когда появится шкаф разряжений для 1 печи
        signal_value = Rarefaction_P2.objects.annotate(dateandtime=F('timestamp')).annotate(value=F(rarefaction_point_name)).filter(timestamp__range=(period_start,period_stop)
            ).order_by('dateandtime')

        return signal_value
    #Список сигналов, отображаемых на тренде. Чтобы добавить новый сигнал, нужно внести для него строку в этот блок
    signals = list()

    #сигналы для первой печи
    if furnace_no == 1:
        signals.append(("Мощность", LoadSignalValuesByPeriod('MEASURES\HY_F711', start_period, stop_period)))
        signals.append(("Ток двигателя", LoadSignalValuesByPeriod('MEASURES\SI_KL710', start_period, stop_period)))
        signals.append(("Расход газа", LoadSignalValuesByPeriod('MEASURES\FL710_NG', start_period, stop_period)))
        signals.append(("Расход О2", LoadSignalValuesByPeriod('MEASURES\O1Flow', start_period, stop_period)))
        signals.append(("Расход воздуха", LoadSignalValuesByPeriod('MEASURES\FL710_AIR', start_period, stop_period)))
        signals.append(("Альфа", LoadSignalValuesByPeriod('MEASURES\Alpha_p1', start_period, stop_period)))
        signals.append(("Лямбда", LoadSignalValuesByPeriod('MEASURES\Lambda_p1', start_period, stop_period)))
        signals.append(("Круглый дроссель", LoadSignalValuesByPeriod('MEASURES\p1_mct1_rez', start_period, stop_period, minus=256)))
        signals.append(("На 3 фильтр", LoadSignalValuesByPeriod('MEASURES\p1_mct5_rez', start_period, stop_period, minus=1280)))
        signals.append(("Над дверью", LoadSignalValuesByPeriod('MEASURES\p1_mct2_rez', start_period, stop_period, minus=512)))
        signals.append(("Горячий дроссель", LoadSignalValuesByPeriod('MEASURES\ZI_701', start_period, stop_period)))
        signals.append(("dP на фильтре", LoadSignalValuesByPeriod('MEASURES\PDI_720', start_period, stop_period)))
        signals.append(("dP на дымососе", LoadSignalValuesByPeriod('MEASURES\PDI_724', start_period, stop_period)))
        signals.append(("Частота дымососа", LoadSignalValuesByPeriod('MEASURES\SI_U720', start_period, stop_period)))
        signals.append(("Т перед фильтром", LoadSignalValuesByPeriod('MEASURES\TI_704', start_period, stop_period)))

        signals.append(("Разряжение т.3", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point1', start_period, stop_period)))
        signals.append(("Разряжение в ГГ", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point6', start_period, stop_period)))

        signals.append(("Т над дверью", LoadSignalValuesByPeriod('MEASURES\TI_712Y', start_period, stop_period))) #эти два сигнала должны быть в списке последними
        signals.append(("Т воздух цех", LoadSignalValuesByPeriod('MEASURES\TI_712X', start_period, stop_period))) #эти два сигнала должны быть в списке последними

    elif furnace_no == 2:
        signals.append(("Мощность", LoadSignalValuesByPeriod('MEASURES\HY_F710', start_period, stop_period)))
        signals.append(("Ток двигателя", LoadSignalValuesByPeriod('MEASURES\SI_KL711', start_period, stop_period)))
        signals.append(("Расход газа", LoadSignalValuesByPeriod('MEASURES\TI_810B', start_period, stop_period)))
        signals.append(("Расход О2", LoadSignalValuesByPeriod('MEASURES\O2Flow', start_period, stop_period)))
        signals.append(("Расход воздуха", LoadSignalValuesByPeriod('MEASURES\TI_810C', start_period, stop_period)))
        signals.append(("Альфа", LoadSignalValuesByPeriod('MEASURES\Alpha', start_period, stop_period)))
        signals.append(("Лямбда", LoadSignalValuesByPeriod('MEASURES\Lambda', start_period, stop_period)))
        signals.append(("Круглый дроссель", LoadSignalValuesByPeriod('MEASURES\\xvi_v_cech', start_period, stop_period)))
        signals.append(("На 3 фильтр", LoadSignalValuesByPeriod('MEASURES\XVI_708', start_period, stop_period)))
        signals.append(("Над дверью", LoadSignalValuesByPeriod('MEASURES\ZI_704', start_period, stop_period)))
        signals.append(("Горячий дроссель", LoadSignalValuesByPeriod('MEASURES\ZI_702', start_period, stop_period)))
        signals.append(("dP на фильтре", LoadSignalValuesByPeriod('MEASURES\PDI_725', start_period, stop_period)))
        signals.append(("dP на дымососе", LoadSignalValuesByPeriod('MEASURES\PDI_729', start_period, stop_period)))
        signals.append(("Частота дымососа", LoadSignalValuesByPeriod('MEASURES\SI_U721', start_period, stop_period)))
        signals.append(("Т перед фильтром", LoadSignalValuesByPeriod('MEASURES\TI_708', start_period, stop_period)))

        #signals.append(("Разряжение т.1", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point1', start_period, stop_period)))
        #signals.append(("Разряжение т.2", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point2', start_period, stop_period)))
        signals.append(("Разряжение т.3", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point3', start_period, stop_period)))
        signals.append(("Разряжение т.4", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point4', start_period, stop_period)))
        signals.append(("Разряжение т.5", LoadRarefactionValuesByPeriod(furnace_no, 'rf_fur2_point5', start_period, stop_period))) 
        signals.append(("Разряжение в ГГ",  LoadSignalValuesByPeriod('MEASURES\PI_702', start_period, stop_period)))
        #signals.append(("Разряжение в печи", LoadRarefactionValuesByPeriod(furnace_no, 'rf_in_furnace', start_period, stop_period))) 
        signals.append(("Разряжение в печи_ск.ср.", LoadRarefactionValuesByPeriod(furnace_no, 'rf_in_furnace_filtr', start_period, stop_period))) 
        signals.append(("Разряжение в циклоне", LoadRarefactionValuesByPeriod(furnace_no, 'rf_in_ciclone_2pech', start_period, stop_period)))

        signals.append(("Т над дверью", LoadSignalValuesByPeriod('MEASURES\TI_711Y', start_period, stop_period))) #эти два сигнала должны быть в списке последними
        signals.append(("Т воздух цех", LoadSignalValuesByPeriod('MEASURES\TI_711X', start_period, stop_period))) #эти два сигнала должны быть в списке последними

    detalization = 1

    series = list()
    for i in range(len(signals)):
        if signals[i][0] not in {"Т над дверью","Т воздух цех"}: #для случая вычисления разности(или другой операции) между двумя сигналами
            series.append([[signals[i][0]], []])
            for j in range(0, len(signals[i][1]), detalization):
                try:
                    dat = datetime.strptime(str(signals[i][1][j].dateandtime), '%Y-%m-%d %H:%M:%S.%f+00:00')
                except:
                    dat = datetime.strptime(str(signals[i][1][j].dateandtime), '%Y-%m-%d %H:%M:%S+00:00')
                try:
                    if signals[i][0] in ("Разряжение в печи_ск.ср.", "Разряжение в ГГ"):
                        point={"date":dat.timestamp()*1000, "value":round(signals[i][1][j].value*100, 2)} #Умножение на коэффициент для масштабирования на графике
                    else:
                        point={"date":dat.timestamp()*1000, "value":round(signals[i][1][j].value, 2)}
                except:
                    pass #для случаев, когда таких сигналов не было в БД
                series[i][1].append(point)
        elif signals[i][0] in {"Т над дверью"}: #исключение для вычисления дельты температур
            series.append([["Дельта Т"], []])
            for a,b in itertools.zip_longest(signals[i][1], signals[i+1][1]): #шагаем сразу по двум спискам. Для ускорения вычислений
                try:
                    dat = datetime.strptime(str(a.dateandtime), '%Y-%m-%d %H:%M:%S.%f+00:00')
                except:
                    dat = datetime.strptime(str(a.dateandtime), '%Y-%m-%d %H:%M:%S+00:00')
                point={"date":dat.timestamp()*1000, "value":round(a.value-b.value, 2)}
                series[i][1].append(point)



    return JsonResponse(series, safe=False)

@login_required
def error_message(request):
    template = loader.get_template('FregatMonitoringApp/error_message.html')
    context = None
    return HttpResponse(template.render(context, request))

@login_required
def sorry_page(request):
    template = loader.get_template('FregatMonitoringApp/sorry_page.html')
    context=None
    return HttpResponse(template.render(context, request))

@login_required
def furnace_1_info(request):
    
    def cur_signal_value(signal_name: str, **kwards):
        """ Возвращает текущее значение сигнала по его имени в БД

            Принимает название сигнала, 
                      kwards['minus'] - коррекция для сигналов дросселей, которые шифруются определённым образом      
        """

        if kwards.get('minus') == None:
            kwards['minus'] = 0

        return [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname=signal_name)[0].tagindex).order_by('-dateandtime')[0].val - kwards['minus'],
    Tagtable.objects.filter(tagname=signal_name)[0].tagindex]
    
    #Положение ШЗМ
    try:
        if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\ZSL_PK710')[0].tagindex).order_by('-dateandtime')[0].val:
            shzm_position = "У поля"
        elif Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\ZSH_PK710')[0].tagindex).order_by('-dateandtime')[0].val:
            shzm_position = "У 1 печи"
        elif Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\ZSHH_PK710')[0].tagindex).order_by('-dateandtime')[0].val:
            shzm_position = "У 2 печи"
    except:
        shzm_position = "---"
    
    #автоплавка
    Automelt_info = Avtoplavka_status.objects.filter(furnace_no=1)
    Automelt_sp_info = Avtoplavka_setpoints.objects.filter(furnace_no=1)

    auto_mode = "Автомат" if Automelt_info[0].auto_mode else "Ручной"
    try:
        meltid = Melttypes.objects.filter(melt_num = Automelt_info[0].melt_type).filter(melt_furnace = Automelt_info[0].furnace_no)[0].melt_id
    except:
        meltid = "---"
    try:
        melt_type = Melttypes.objects.filter(melt_id = meltid)[0].melt_name
    except:
        melt_type = "---"
    try:
        melt_step = Meltsteps.objects.filter(melt = meltid).filter(step_num = Automelt_info[0].current_step)[0].step_name
    except:
        melt_step = "---"
    step_total_time = Automelt_info[0].step_total_time
    step_time_remain = step_total_time - Automelt_info[0].step_time_remain
    deltat_stp = Automelt_info[0].delta_t_stp 
    power_sp_base = Automelt_sp_info[0].power_sp #базовая уставка мощности (без учёта возможного снижения)
    try:
        hotflue_p_sp = Automelt_info[0].hotflue_p_sp #Уставка разряжения в ГГ
    except:
        pass
    try:
        melt_no = Automelt_info[0].melt_no
    except:
        melt_no = "---"

    #разряжения
    rf_fur = Rarefaction_P2.objects.order_by('-timestamp')[0]

    template = loader.get_template('FregatMonitoringApp/furnace_info.html')
    context = {'furnace_num': 1,

               #горелка
               'power_sp': cur_signal_value('MEASURES\HY_F711'), #текущая мощность(с учётом возможного снижения)
               'power_sp_base': power_sp_base, #базовая уставка мощности (без учёта возможного снижения)
               'gas_flow': cur_signal_value('MEASURES\FL710_NG'),
               'air_flow': cur_signal_value('MEASURES\FL710_AIR'),
               'o2_flow': cur_signal_value('MEASURES\O1Flow'),
               'alpha': cur_signal_value('MEASURES\Alpha_p1'),
               'lambda': cur_signal_value('MEASURES\Lambda_p1'),
               'standby': cur_signal_value('GENERAL\F710_LOCK'),
               'power_mode': cur_signal_value('IO\HS1_F710'),

               #фильтр
               'filter_dp': cur_signal_value('MEASURES\PDI_720'),
               't_before_filter': cur_signal_value('MEASURES\TI_704'),

               #дымосос
               'exhauster_dp': cur_signal_value('MEASURES\PDI_724'),
               'exhauster_pc': cur_signal_value('MEASURES\SI_U720'),
               
               #горячий газоход
               'hotflue_p': rf_fur.rf_fur2_point6, #временно датчик заведён в шкаф разряжений 2 печи на 6 канал
               'hotflue_p_sp': hotflue_p_sp, #уставка разряжения в ГГ
               'hotflue_t': cur_signal_value('MEASURES\TI_703B'),

               #дроссели
               'hot_flue_gate': cur_signal_value('MEASURES\ZI_701'),
               'over_door_gate': cur_signal_value('MEASURES\p1_mct2_rez',minus=512),
               'exhauster_gate': cur_signal_value('MEASURES\p1_mct7_rez',minus=1792),
               'round_gate': cur_signal_value('MEASURES\p1_mct1_rez',minus=256),
               'filter3_gate': cur_signal_value('MEASURES\p1_mct5_rez',minus=1280),
               'drain_gate': cur_signal_value('VALVES\XV701_ZL'),  

                #дельта
               'over_door_t': cur_signal_value('MEASURES\TI_712Y'),
               'cold_air_t': cur_signal_value('MEASURES\TI_712X'),
               'deltaT': cur_signal_value('MEASURES\TI_712Y')[0]  - cur_signal_value('MEASURES\TI_712X')[0],

               #печь
               'furnace_rotation': cur_signal_value('MEASURES\SY_KL710'),
               'furnace_current': cur_signal_value('MEASURES\SI_KL710'),
               'loading_door_half': cur_signal_value('VALVES\XVF710P_ZL'),
               
               #автоплавка
               'auto_mode': auto_mode,
               'melt_type' : melt_type,
               'melt_step' : melt_step,
               'step_total_time' : step_total_time,
               'step_time_remain' : step_time_remain,
               'deltat_stp' : deltat_stp,
               'melt_no': melt_no,

               #разряжения
               #'rf_fur_point1': rf_fur.rf_fur2_point1, #точка 1
               #'rf_fur_point2': rf_fur.rf_fur2_point2, #точка 2
               'rf_fur_point3': rf_fur.rf_fur2_point1, #точка 3 - временно датчик с точки 1 печи 2
               #'rf_fur_point4': rf_fur.rf_fur2_point4, #точка 4
               #'rf_fur_point5': rf_fur.rf_fur2_point5, #точка 5


               #Положение ШЗМ
               'shzm_position': shzm_position,
               'weight_in_shzm': cur_signal_value('MEASURES\WI_710'),
              }

    return HttpResponse(template.render(context, request))

@login_required
def furnace_2_info(request):
    
    def cur_signal_value(signal_name: str, **kwards):
        """ Возвращает текущее значение сигнала по его имени в БД

            Принимает название сигнала, 
                      kwards['minus'] - коррекция для сигналов дросселей, которые шифруются определённым образом      
        """

        if kwards.get('minus') == None:
            kwards['minus'] = 0

        return [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname=signal_name)[0].tagindex).order_by('-dateandtime')[0].val - kwards['minus'],
    Tagtable.objects.filter(tagname=signal_name)[0].tagindex]
    
    #Положение ШЗМ
    try:
        if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\ZSL_PK710')[0].tagindex).order_by('-dateandtime')[0].val:
            shzm_position = "У поля"
        elif Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\ZSH_PK710')[0].tagindex).order_by('-dateandtime')[0].val:
            shzm_position = "У 1 печи"
        elif Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\ZSHH_PK710')[0].tagindex).order_by('-dateandtime')[0].val:
            shzm_position = "У 2 печи"
    except:
        shzm_position = "---"
    
    #автоплавка
    Automelt_info = Avtoplavka_status.objects.filter(furnace_no=2)
    Automelt_sp_info = Avtoplavka_setpoints.objects.filter(furnace_no=2)

    auto_mode = "Автомат" if Automelt_info[0].auto_mode else "Ручной"
    try:
        meltid = Melttypes.objects.filter(melt_num = Automelt_info[0].melt_type).filter(melt_furnace = Automelt_info[0].furnace_no)[0].melt_id
    except:
        meltid = "---"
    try:
        melt_type = Melttypes.objects.filter(melt_id = meltid)[0].melt_name
    except:
        melt_type = "---"
    try:
        melt_step = Meltsteps.objects.filter(melt = meltid).filter(step_num = Automelt_info[0].current_step)[0].step_name
    except:
        melt_step = "---"
    step_total_time = Automelt_info[0].step_total_time
    step_time_remain = step_total_time - Automelt_info[0].step_time_remain
    deltat_stp = Automelt_info[0].delta_t_stp 
    power_sp_base = Automelt_sp_info[0].power_sp #базовая уставка мощности (без учёта возможного снижения)
    try:
        hotflue_p_sp = Automelt_info[0].hotflue_p_sp #Уставка разряжения в ГГ
    except:
        pass
    try:
        melt_no = Automelt_info[0].melt_no
    except:
        melt_no = "---"


    #разряжения
    rf_fur = Rarefaction_P2.objects.order_by('-timestamp')[0]

    template = loader.get_template('FregatMonitoringApp/furnace_info.html')
    context = {'furnace_num': 2,

               #горелка
               'power_sp': cur_signal_value('MEASURES\HY_F710'), #текущая мощность(с учётом возможного снижения)
               'power_sp_base': power_sp_base, #базовая уставка мощности (без учёта возможного снижения)
               'gas_flow': cur_signal_value('MEASURES\TI_810B'),
               'air_flow': cur_signal_value('MEASURES\TI_810C'),
               'o2_flow': cur_signal_value('MEASURES\O2Flow'),
               'alpha': cur_signal_value('MEASURES\Alpha'),
               'lambda': cur_signal_value('MEASURES\Lambda'),
               'standby': cur_signal_value('GENERAL\F711_LOCK'),
               'power_mode': cur_signal_value('IO\HS1_F711'),

               #фильтр
               'filter_dp': cur_signal_value('MEASURES\PDI_725'),
               't_before_filter': cur_signal_value('MEASURES\TI_708'),

               #дымосос
               'exhauster_dp': cur_signal_value('MEASURES\PDI_729'),
               'exhauster_pc': cur_signal_value('MEASURES\SI_U721'),
               
               #горячий газоход
               'hotflue_p': cur_signal_value('MEASURES\PI_702') ,
               'hotflue_p_sp': hotflue_p_sp, #уставка разряжения в ГГ
               'hotflue_t': cur_signal_value('MEASURES\TI_705A'),

               #дроссели
               'hot_flue_gate': cur_signal_value('MEASURES\PY_702'),
               'over_door_gate': cur_signal_value('MEASURES\ZI_704'),
               'exhauster_gate': cur_signal_value('MEASURES\ZI_706'),
               'round_gate': cur_signal_value('MEASURES\\xvi_v_cech'),
               'filter3_gate': cur_signal_value('MEASURES\XVI_708'),
               'drain_gate': cur_signal_value('VALVES\XV702_ZL'),  

                #дельта
               'over_door_t': cur_signal_value('MEASURES\TI_711Y'),
               'cold_air_t': cur_signal_value('MEASURES\TI_711X'),
               'deltaT': cur_signal_value('MEASURES\TI_711Y')[0]  - cur_signal_value('MEASURES\TI_711X')[0],

               #печь
               'furnace_rotation': cur_signal_value('MEASURES\SY_KL711'),
               'furnace_current': cur_signal_value('MEASURES\SI_KL711'),
               'loading_door_half': cur_signal_value('VALVES\XVF711P_ZL'),

               #автоплавка
               'auto_mode': auto_mode,
               'melt_type' : melt_type,
               'melt_step' : melt_step,
               'step_total_time' : step_total_time,
               'step_time_remain' : step_time_remain,
               'deltat_stp' : deltat_stp,
               'melt_no': melt_no,

               #разряжения
               'rf_fur_point1': rf_fur.rf_fur2_point1, #точка 1
               'rf_fur_point2': rf_fur.rf_fur2_point2, #точка 2
               'rf_fur_point3': rf_fur.rf_fur2_point3, #точка 3
               'rf_fur_point4': rf_fur.rf_fur2_point4, #точка 4
               'rf_fur_point5': rf_fur.rf_fur2_point5, #точка 5

               #Положение ШЗМ
               'shzm_position': shzm_position,
               'weight_in_shzm': cur_signal_value('MEASURES\WI_710'),
              }

    return HttpResponse(template.render(context, request))

@login_required
def bottling_page(request):
    template = loader.get_template('FregatMonitoringApp/bottling_page.html')

    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def bottling_page_data(request):
    "Грузит страницу журнала розливов"

    template = loader.get_template('FregatMonitoringApp/bottling_journal_page.html')
    grades_list = sorted([i[0] for i in set(Bottling.objects.values_list('grade')) if i[0]!=None])
    context = {'grades_list': grades_list}
    return HttpResponse(template.render(context, request))

@login_required
def current_bottling_page(request):
    "Грузит страницу текущего розлива"

    template = loader.get_template('FregatMonitoringApp/current_bottling_page.html')
    current_bundle = CurrentBottling.objects.get()
    current_bottling_journal = Bottling.objects.filter(lot=current_bundle.lot).filter(proddate__gte=str(current_bundle.proddate.strftime("%Y"))+'-01-01 00:00:00')

    context = {'cur_bundle': current_bundle.bundle,
               'cur_grade': current_bundle.grade,
               'cur_lot': current_bundle.lot,
               'cur_weight': current_bundle.weight,
               'cur_proddate': current_bundle.proddate.strftime("%d-%m-%Y %H:%M:%S"),
               'bottling_year': str(current_bundle.proddate.strftime("%Y"))
    }
    return HttpResponse(template.render(context, request))

@login_required
def bottling_journal_data(request):
    '''Выдаёт журнал розлива по четырём фильтрам: Год, № розлива, марка сплава, дата розлива. Если один, несколько или все фильтры
    не заданные - выдаёт полную выборку из БД за последний год'''

    if request.method == 'GET':
        bottling_year = request.GET.get('bottling_year', None)
        bottling_lot = request.GET.get('bottling_lot', None) 
        bottling_grade = request.GET.get('bottling_grade', None)

    if not(bottling_year) and not(bottling_lot) and not(bottling_grade): #Если ни один фильтр не задан
        bottling_year = datetime.today().year #выводим всё за текущий год
        
    journal = Bottling.objects
    
    if bottling_year is not None:
        journal=journal.filter(proddate__gte = str(bottling_year)+'-01-01 00:00:00').filter(proddate__lte = str(int(bottling_year)+1)+'-01-01 00:00:00') 
    if bottling_lot is not None:
        journal = journal.filter(lot=bottling_lot+'/'+bottling_year[2:])
    if bottling_grade is not None:
        journal = journal.filter(grade=bottling_grade)

    journal_entrys = list()
    for i in range(len(list(journal))):
        entry = journal[i]
        try:
            weight = entry.weight[:-3]
            if(weight[0]=='0'):
                weight = weight[1:]
        except:
            weight = entry.weight
        if entry.grade != None:   
            journal_entrys.append({
                "grade":entry.grade,
                "lot":entry.lot,
                "data":entry.proddate,
                "bundle":entry.bundle,
                "weight":weight
            })
        
    return JsonResponse(journal_entrys, safe=False)

@login_required
def shzm_page(request):
    template = loader.get_template('FregatMonitoringApp/shzm_page.html')

    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def shzm_journal_page(request):
    "Грузит страницу журнала загрузок"
    context = {}
    template = loader.get_template('FregatMonitoringApp/shzm_journal_page.html')
    return HttpResponse(template.render(context, request))

@login_required
def shzm_journal_page_data(request):
    '''Выдаёт данные о загрузках печей по трём фильтрам: № печи, № плавки, временной промежуток. Если один, несколько или все фильтры
    не заданные - выдаёт полную выборку за последний месяц'''

    if request.method == 'GET':
        start_period = request.GET.get('start', None)
        stop_period = request.GET.get('stop', None) 
        furnace_no = request.GET.get('furnace_no', None)
        melt_number = request.GET.get('melt_number', None) 

    if start_period is None:
        start_period = (datetime.now()-timedelta(hours=30*24)).strftime('%Y-%m-%dT%H:%M')#предыдущий месяц
    else:
        start_period = datetime.strptime(start_period, '%Y-%m-%dT%H:%M')
    if  stop_period is None:
        stop_period = datetime.now().strftime('%Y-%m-%dT%H:%M')#текущий момент  
    else:
        stop_period = datetime.strptime(stop_period, '%Y-%m-%dT%H:%M')

    log = Melts.objects.filter(startmelt__range=(start_period, stop_period)).order_by("-startmelt")
    if furnace_no is not None:
        log = log.filter(furnace=furnace_no)
    if melt_number is not None:
        log = log.filter(meltno=melt_number)
 
    log_entrys=list()
    for i in range(len(list(log))):
        try: 
            #защита от ситуации, когда %f(миллисекунды в дате) = .0000. Тогда БД возвращает дату без них и не совпадает формат
            startmelt = datetime.strptime(str(log[i].startmelt), '%Y-%m-%d %H:%M:%S.%f+00:00').strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            startmelt = datetime.strptime(str(log[i].startmelt), '%Y-%m-%d %H:%M:%S+00:00').strftime("%Y-%m-%d %H:%M:%S")

        log_entrys.append({             
            "startmelt": startmelt,
            "meltno": log[i].meltno,
            "furnace_no": log[i].furnace,
            "total": log[i].total/100,
            "pasta": log[i].pasta/100,
            "coal": log[i].coal/100,
            "soda": log[i].soda/100,
            "iron": log[i].iron/100,
            "dust": log[i].dust/100,
            "oxides": log[i].oxides/100,
            "slurry": log[i].slurry/100,
            "fraction": log[i].fraction/100,
            "pbmat": log[i].pbmat/100,
        })
    
    return JsonResponse(log_entrys, safe=False)

@login_required
def auto_melts_types_info(request, melt_id_1):

    melt_type_list = Melttypes.objects.filter(melt_furnace=1) #Выбираем типы плавок для первой печи(для второй такие же)

    melt_type_name = Melttypes.objects.filter(melt_id=melt_id_1)[0].melt_name #Узнаём, как называется этот тип плавки
    melt_id_2 = Melttypes.objects.filter(melt_name=melt_type_name, melt_furnace=2)[0].melt_id #По имени вытаскиваем id аналогичной плавки для второй печи

     
    melt_steps_list_1 = Meltsteps.objects.filter(melt=melt_id_1) #Выбираем шаги для нужных плавок
    melt_steps_list_2 = Meltsteps.objects.filter(melt=melt_id_2)
    
    #Выбираем подшаги для каждого шага каждой плавки
    substeps_list_1 = list() 
    for melt_step in melt_steps_list_1: 
        for substep in [Substeps.objects.filter(step=melt_step.step_id)]:
            substeps_list_1.extend(substep)

    substeps_list_2 = list()
    for melt_step in melt_steps_list_2: 
        for substep in [Substeps.objects.filter(step=melt_step.step_id)]:
            substeps_list_2.extend(substep)

    template = loader.get_template('FregatMonitoringApp/auto_melts_types_info.html')
    context = {
        'melt_name': melt_type_name,
        'melts_id': [melt_id_1, melt_id_2],
        'melt_types': melt_type_list,
        'melt_steps_1': melt_steps_list_1,
        'melt_steps_2': melt_steps_list_2,
        'substeps_1' : substeps_list_1,
        'substeps_2' : substeps_list_2
    }

    return HttpResponse(template.render(context, request))

@login_required
def auto_melts_log(request):

    template = loader.get_template('FregatMonitoringApp/auto_melts_log_page.html')
    context = {
    }

    return HttpResponse(template.render(context, request))

@login_required
def auto_melts_log_data(request):
    '''Выдаёт данные о ходе автоматических плавок по трём фильтрам: № печи, № плавки, временной промежуток. Если один, несколько или все фильтры
    не заданные - выдаёт полную выборку за последний месяц'''

    if request.method == 'GET':
        start_period = request.GET.get('start', None)
        stop_period = request.GET.get('stop', None) 
        furnace_no = request.GET.get('furnace_no', None)
        melt_number = request.GET.get('melt_number', None) 

    if start_period is None or stop_period is None:
        start_period = (datetime.now()-timedelta(hours=30*24)).strftime('%Y-%m-%dT%H:%M')#предыдущий месяц
        stop_period = datetime.now().strftime('%Y-%m-%dT%H:%M')#текущий момент  
    else:
        start_period = datetime.strptime(start_period, '%Y-%m-%dT%H:%M')
        stop_period = datetime.strptime(stop_period, '%Y-%m-%dT%H:%M')

    log = Autoplavka_log.objects.filter(date_time__range=(start_period, stop_period))
    if furnace_no is not None:
        log = log.filter(furnace_no=furnace_no)
    if melt_number is not None:
        log = log.filter(melt_number=melt_number)
 
    log_entrys=list()
    for i in range(len(list(log))):
        cur_melt = Melttypes.objects.filter(melt_num = log[i].melt_type, melt_furnace = log[i].furnace_no)[0]
        cur_step = Meltsteps.objects.filter(step_num = log[i].current_step, melt = cur_melt.melt_id)[0]

        try:
            if log[i].auto_mode: #отображаем имя шага только когда был автоматический режим
                cur_sstep = Substeps.objects.filter(sub_step_num = log[i].current_substep, step = cur_step.step_id)[0]
            else:
                cur_sstep = "" 
        except:
            cur_sstep = ""
        
        if log[i].auto_mode:
            cur_mode = "Автоматический режим"
        else:
            cur_mode = "Ручной режим"

        try: 
            #защита от ситуации, когда %f(миллисекунды в дате) = .0000. Тогда БД возвращает дату без них и не совпадает формат
            log_dt = datetime.strptime(str(log[i].date_time), '%Y-%m-%d %H:%M:%S.%f+00:00').strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            log_dt = datetime.strptime(str(log[i].date_time), '%Y-%m-%d %H:%M:%S+00:00').strftime("%Y-%m-%d %H:%M:%S")

        log_entrys.append({
            "furnace_no": log[i].furnace_no,
            "melt_number": log[i].melt_number,
            "melt_type": cur_melt.melt_name ,
            "current_step": cur_step.step_name if log[i].auto_mode else "", #отображаем имя стадии только когда был автоматический режим
            "current_substep": cur_sstep.sub_step_num if cur_sstep != "" else "",
            "auto_mode": cur_mode,
            "date_time": log_dt,
            "power_sp": cur_sstep.power_sp if cur_sstep != "" else "",
            "rotation_sp": cur_sstep.rotation_sp if cur_sstep != "" else "",
            "alpha_sp": cur_sstep.alpha_sp if cur_sstep != "" else "",
            "sub_step_time": cur_sstep.sub_step_time if cur_sstep != "" else "",
        })
    
    return JsonResponse(log_entrys, safe=False)

@login_required
def auto_melts_add_substep(request, melt_type, melt_step):
    """Добавляет подшаг к заданному шагу по типу плавки(названию) сразу для обеих печей
       request - запрос,
       melt_type - Тип плавки (по названию), к которой будет добавляться подшаг. Добавляем в одинаковые типы плавок для обеих печей
       melt_step - порядковый номер шага, к которому будет добавлять подшаг
    """

    melt_1 = Melttypes.objects.get(melt_name=melt_type, melt_furnace=1) #вытаскиваем плавку по типу(названию) для первой печи
    melt_2 = Melttypes.objects.get(melt_name=melt_type, melt_furnace=2) #вытаскиваем плавкупо типу(названию) для первой печи

    step_1 = Meltsteps.objects.get(step_num=melt_step, melt=melt_1.melt_id) #вытаскиваем шаг по номеру для первой печи для заданного типа плавки
    step_2 = Meltsteps.objects.get(step_num=melt_step, melt=melt_2.melt_id) #вытаскиваем шаг по номеру для второй печи для заданного типа плавки

    num_of_substeps_1 = Substeps.objects.filter(step=step_1.step_id).count() #считаем сколько в этом шаге подшагов
    num_of_substeps_2 = Substeps.objects.filter(step=step_2.step_id).count() #считаем сколько в этом шаге подшагов

    substep_melt_1 = Substeps(step=step_1, sub_step_num=num_of_substeps_1+1, sub_step_time=0)
    substep_melt_1.save()
    substep_melt_2 = Substeps(step=step_2, sub_step_num=num_of_substeps_2+1, sub_step_time=0)
    substep_melt_2.save()

    return auto_melts_types_info(request, melt_1.melt_id) 

@login_required
def auto_melts_del_substep(request, melt_type, melt_step, melt_substep):
    '''Удаляет подшаг у заданного шага по типу плавки(названию) сразу для обеих печей
       request - запрос,
       melt_type - Тип плавки (по названию), к которой будет добавляться подшаг. Добавляем в одинаковые типы плавок для обеих печей
       melt_step - порядковый номер шага, к которому будет добавлять подшаг
       melt_substep - порядковый номер подшага, который нужно удалить
    '''

    melt_1 = Melttypes.objects.get(melt_name=melt_type, melt_furnace=1) #вытаскиваем плавку по типу(названию) для первой печи
    melt_2 = Melttypes.objects.get(melt_name=melt_type, melt_furnace=2) #вытаскиваем плавкупо типу(названию) для первой печи

    step_1 = Meltsteps.objects.get(step_num=melt_step, melt=melt_1.melt_id) #вытаскиваем шаг по номеру для первой печи для заданного типа плавки
    step_2 = Meltsteps.objects.get(step_num=melt_step, melt=melt_2.melt_id) #вытаскиваем шаг по номеру для второй печи для заданного типа плавки

    num_of_substeps_1 = Substeps.objects.filter(step=step_1.step_id).count() #считаем сколько в этом шаге подшагов
    num_of_substeps_2 = Substeps.objects.filter(step=step_2.step_id).count() #считаем сколько в этом шаге подшагов

    Substeps.objects.filter(step=step_1, sub_step_num = melt_substep).delete()
    Substeps.objects.filter(step=step_2, sub_step_num = melt_substep).delete()

    if melt_substep < num_of_substeps_1: #если удалённый подшаг был не последним в этом шаге
        for m_sst in range(melt_substep+1, num_of_substeps_1+1): # для каждого из последующих шагов
            substep_1 = Substeps.objects.get(step=step_1, sub_step_num = m_sst)
            substep_1.sub_step_num -= 1 #уменьшаем его порядковый номер на 1, чтобы скорректировать нумерацию с учётом удалённого шага
            substep_1.save()
    
    if melt_substep < num_of_substeps_2: #если удалённый подшаг был не последним в этом шаге
        for m_sst in range(melt_substep+1, num_of_substeps_2+1): # для каждого из последующих шагов
            substep_2 = Substeps.objects.get(step=step_2, sub_step_num = m_sst)
            substep_2.sub_step_num -= 1 #уменьшаем его порядковый номер на 1, чтобы скорректировать нумерацию с учётом удалённого шага
            substep_2.save()

    return auto_melts_types_info(request, melt_1.melt_id) 

@login_required
def auto_melts_setpoints(request):
    
    template = loader.get_template('FregatMonitoringApp/auto_melts_setpoints.html')

    try:
        deltaT1_stp = Automelts.objects.filter(furnace_no=1)[0].deltat
        deltaT2_stp = Automelts.objects.filter(furnace_no=2)[0].deltat
    except:
        return error_message(request) #Ой, что-то пошло не так
    
    context={
        'deltaT1_stp':deltaT1_stp,
        'deltaT2_stp':deltaT2_stp,
    }
    return HttpResponse(template.render(context, request))

@login_required
def auto_melts_save_settings(request, melt_id_1, melt_id_2): #сохраняет изменение режимов автоплаки в базе
    
    melt_steps_list = Meltsteps.objects.filter(melt__in=[melt_id_1, melt_id_2]) #Выбираем шаги для нужных плавок

    #Выбираем подшаги для каждого шага каждой плавки
    for melt_step in melt_steps_list: 
        for substep in Substeps.objects.filter(step=melt_step.step_id):
            try:
                substep.sub_step_time = request.POST["Time_substepid_"+str(substep.substep_id)] if request.POST["Time_substepid_"+str(substep.substep_id)]!="" else None
                substep.power_sp = request.POST["Power_substepid_"+str(substep.substep_id)] if request.POST["Power_substepid_"+str(substep.substep_id)]!="" else None
                substep.rotation_sp = request.POST["Rotation_substepid_"+str(substep.substep_id)] if request.POST["Rotation_substepid_"+str(substep.substep_id)]!="" else None
                substep.alpha_sp = request.POST["Alpha_substepid_"+str(substep.substep_id)] if request.POST["Alpha_substepid_"+str(substep.substep_id)]!="" else None
            except (KeyError, substep.DoesNotExist):
                return error_message(request) #Ой, что-то пошло не так
            else:
                substep.save()

    return HttpResponseRedirect(reverse('FregatMonitoringApp:auto_melts_types_info', args=(melt_id_1,)))

@login_required
def auto_melts_save_setpoints(request, furnace_num): #сохраняет изменение уставки Дельты в базе
    try:
        try: 
            float(request.POST["DeltaT"+str(furnace_num)+"_stp"]) #"Это число вообще?"
        except:
            return error_message(request) #Ой, что-то пошло не так
        Melt1 = Automelts.objects.filter(furnace_no = furnace_num)[0]  #Пишем в старую таблицу. Теперь это рудимент. Для поддержки старых версий программ ПЛК
        Melt1.deltat = request.POST["DeltaT"+str(furnace_num)+"_stp"]

        Melt = Avtoplavka_setpoints.objects.get(furnace_no = furnace_num)  #Новая таблица уставок. Передача идёт через эту таблицу
        Melt.delta_t_stp = request.POST["DeltaT"+str(furnace_num)+"_stp"]
    except: #не удалось записать в базу
        return error_message(request) #Ой, что-то пошло не так
    else:
        Melt1.save() 
        Melt.save() 

    return HttpResponseRedirect(reverse('FregatMonitoringApp:auto_melts_setpoints'))


#----------ОТОБРАЖЕНИЯ ЧЕРЕЗ СЕРИАЛАЙЗЕРЫ-------------------

def furnace_info_s(request, signal_index): # API для обновления данных на экране "Печь 1(2)"
    
    #В общем виде ищем последнее значение в таблице для каждого сигнала
    tag_val = Floattable.objects.filter(tagindex=signal_index).order_by('-dateandtime')[:1]

    serializer = FloattableSerializer(tag_val, many=True)

    # если значение сигнала нужно пред-обработать, обрабатываем значение уже внутри сериалайзера
    #----Исключения 1 печь----------------
    if signal_index == 13: #нагрузка на печь
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 51: #вращение печи
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 52: #дроссель горячего газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 25: #температура гор.газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 26: #температура перед фильтром
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 115: #лямбда
        serializer.data[0]['val'] = round(serializer.data[0]['val'],2)
    if signal_index == 85: #сливной дроссель
        serializer.data[0]['val'] = "открыт" if not serializer.data[0]['val'] else "закрыт"
    if signal_index == 117: #дроссель круглый
        serializer.data[0]['val'] = serializer.data[0]['val']-256
    if signal_index == 118: #дроссель над дверью
        serializer.data[0]['val'] = serializer.data[0]['val']-512
    if signal_index == 121: #дроссель на 3 фильтр
        serializer.data[0]['val'] = serializer.data[0]['val']-1280
    if signal_index == 123: #дроссель дымососа
        serializer.data[0]['val'] = serializer.data[0]['val']-1792

    #----Исключения 2 печь----------------
    if signal_index == 14: #нагрузка на печь
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 17: #вращение печи
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 75: #дроссель горячего газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 27: #температура гор.газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 31: #температура перед фильтром
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if signal_index == 63: #лямбда
        serializer.data[0]['val'] = round(serializer.data[0]['val'],2)
    if signal_index == 81: #сливной дроссель
        serializer.data[0]['val'] = "открыт" if not serializer.data[0]['val'] else "закрыт"
    if signal_index == 9: #перепад на дымососе
        serializer.data[0]['val'] = round(serializer.data[0]['val'])
    if signal_index == 12: #разряжение в гор. газоходе
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)

    #----Исключения ШЗМ---------------
    if signal_index == 48: #вес в бункере ШЗМ
        serializer.data[0]['val'] = round(serializer.data[0]['val'],2)

    return JsonResponse(serializer.data, safe=False)


def furnace_info_a(request, furnace_no): # API для обновления данных о автоплавке на экране "Печь 1(2)"

    try:
        melt_inst = Avtoplavka_status.objects.filter(furnace_no=furnace_no)[0]
        melt_no_inst = melt_inst.melt_no
    except:
        melt_inst = None
        melt_type_inst = None
        step_type_inst = None
        melt_no_inst = None

    try:    
        melt_inst_sp= Avtoplavka_setpoints.objects.filter(furnace_no=furnace_no)[0]
    except:
        melt_inst_sp = None

    try:
        melt_type_inst = Melttypes.objects.filter(melt_num = melt_inst.melt_type)[0]
    except:
        melt_type_inst = None

    try:
        step_type_inst = Meltsteps.objects.filter(step_num = melt_inst.current_step).filter(melt = melt_type_inst.melt_id)[0]
    except:
        step_type_inst = None

    #дельта
    if furnace_no == 1:
        over_door_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_712Y')[0].tagindex).order_by('-dateandtime')[0].val
        cold_air_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_712X')[0].tagindex).order_by('-dateandtime')[0].val
    elif furnace_no == 2:
        over_door_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_711Y')[0].tagindex).order_by('-dateandtime')[0].val
        cold_air_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_711X')[0].tagindex).order_by('-dateandtime')[0].val
    deltaT = over_door_t - cold_air_t
    
    AMmodel = AutoMeltsInfo(
        furnace_no = furnace_no,
        auto_mode = "---" if melt_inst is None else "Автомат" if melt_inst.auto_mode else "Ручной",
        melt_name = "---" if melt_type_inst is None else melt_type_inst.melt_name,
        step_name = "---" if step_type_inst is None else step_type_inst.step_name,
        step_total_time = "---" if melt_inst is None else melt_inst.step_total_time,
        step_time_remain = "---" if melt_inst is None else melt_inst.step_total_time - melt_inst.step_time_remain,
        deltat = round(deltaT,1),
        deltat_stp = "---" if melt_inst is None else melt_inst.delta_t_stp,
        power_sp_base = "---" if melt_inst is None else melt_inst_sp.power_sp,
        hotflue_p_sp = 0.0 if melt_inst.hotflue_p_sp is None else round(melt_inst.hotflue_p_sp, 1),
        aspiration_p_sp = 0.0 if melt_inst.aspiration_p_sp is None else round(melt_inst.aspiration_p_sp< 1),
        melt_no = 0 if melt_no_inst is None else melt_no_inst
    )

    serializer = AutomeltsSerializer(AMmodel)

    return JsonResponse(serializer.data, safe=False)


def furnace_info_r(request, furnace_no): # API для обновления данных о разряжениях на экране "Печь 1(2)"
    #furnace_no - подвязать, когда будут разряжения на печи 1
    rf_fur = Rarefaction_P2.objects.order_by('-timestamp')[0]

    serializer = RarefactionP2Serializer(rf_fur)
 
    return JsonResponse(serializer.data, safe=False)
