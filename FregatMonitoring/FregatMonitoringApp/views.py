from django import template
from django.db.models.query_utils import subclasses
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import context, loader
from django.urls import reverse
from django.db.models import F

from rest_framework.parsers import JSONParser

from .models import Floattable, Tagtable, Automelts, AutoMeltsInfo
from .models import Melttypes, Meltsteps, Substeps
from .serializers import FloattableSerializer, AutomeltsSerializer

def index(request):
    #template = loader.get_template('FregatMonitoringApp/base.html')
    #context = None
    #return HttpResponse(template.render(context, request))
    return Furnace_1_info(request)

def error_message(request):
    template = loader.get_template('FregatMonitoringApp/ErrorMessage.html')
    context = None
    return HttpResponse(template.render(context, request))

def sorry_page(request):
    template = loader.get_template('FregatMonitoringApp/SorryPage.html')
    context = None
    return HttpResponse(template.render(context, request))

def Furnace_1_info(request):
    
    #горелка
    
    power_sp = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\HY_F711')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\HY_F711')[0].tagindex]
    gas_flow = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\FL710_NG')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\FL710_NG')[0].tagindex]
    air_flow = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\FL710_AIR')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\FL710_AIR')[0].tagindex]
    o2_flow =  [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\O1Flow')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\O1Flow')[0].tagindex]
    alpha = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\Alpha_p1')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\Alpha_p1')[0].tagindex]
    lambd = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\Lambda_p1')[0].tagindex).order_by('-dateandtime')[0].val,2),
    Tagtable.objects.filter(tagname='MEASURES\Lambda_p1')[0].tagindex]
    standby = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='GENERAL\F710_LOCK')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='GENERAL\F710_LOCK')[0].tagindex]
    power_mode = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\HS1_F710')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='IO\HS1_F710')[0].tagindex]
    

    #горячий газоход
    hotflue_p = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PI_701')[0].tagindex).order_by('-dateandtime')[0].val,1),
    Tagtable.objects.filter(tagname='MEASURES\PI_701')[0].tagindex]
    hotflue_t = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_703B')[0].tagindex).order_by('-dateandtime')[0].val,1),
    Tagtable.objects.filter(tagname='MEASURES\TI_703B')[0].tagindex]
    
    #фильтр
    filter_dp = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PDI_720')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\PDI_720')[0].tagindex] 
    t_before_filter = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_704')[0].tagindex).order_by('-dateandtime')[0].val,1), 
    Tagtable.objects.filter(tagname='MEASURES\TI_704')[0].tagindex]
    
    #дымосос
    exhauster_dp = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PDI_724')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\PDI_724')[0].tagindex]
    exhauster_pc = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\SI_U720')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='MEASURES\SI_U720')[0].tagindex]

    #дроссели
    hot_flue_gate = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\ZI_701')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\ZI_701')[0].tagindex]
    over_door_gate = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\p1_mct2_rez')[0].tagindex).order_by('-dateandtime')[0].val - 512),
    Tagtable.objects.filter(tagname='MEASURES\p1_mct2_rez')[0].tagindex]
    exhauster_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\p1_mct7_rez')[0].tagindex).order_by('-dateandtime')[0].val - 1792,
    Tagtable.objects.filter(tagname='MEASURES\p1_mct7_rez')[0].tagindex]
    round_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\p1_mct1_rez')[0].tagindex).order_by('-dateandtime')[0].val - 256,
    Tagtable.objects.filter(tagname='MEASURES\p1_mct1_rez')[0].tagindex]
    filter3_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\p1_mct5_rez')[0].tagindex).order_by('-dateandtime')[0].val - 1280,
    Tagtable.objects.filter(tagname='MEASURES\p1_mct5_rez')[0].tagindex]
    drain_gate = ["открыт" if not Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='VALVES\XV701_ZL')[0].tagindex).order_by('-dateandtime')[0].val else "закрыт",
    Tagtable.objects.filter(tagname='VALVES\XV701_ZL')[0].tagindex]

    #дельта
    over_door_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_712Y')[0].tagindex).order_by('-dateandtime')[0].val
    cold_air_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_712X')[0].tagindex).order_by('-dateandtime')[0].val
    deltaT = round(over_door_t - cold_air_t,1)

    #печь
    furnace_rotation = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\SY_KL710')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\SY_KL710')[0].tagindex]
    furnace_current = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\SI_KL710')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\SI_KL710')[0].tagindex]
    loading_door_half = ["открыта" if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='VALVES\XVF710P_ZL')[0].tagindex).order_by('-dateandtime')[0].val == 0 else "закрыта",
    Tagtable.objects.filter(tagname='VALVES\XVF710P_ZL')[0].tagindex]
    
    #поезд - не прописан в History
    #train_move = "Едет" if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MOTORS\H750_FB')[0].tagindex).order_by('-dateandtime')[0].val else "Стоит"
    #train_fwd = "вперёд" if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MOTORS\H750_FWB')[0].tagindex).order_by('-dateandtime')[0].val else "назад"
    #train_fwd = train_fwd if train_move else "---"

    #шзм - не прописан в History
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
    Automelt_info = Automelts.objects.filter(furnace_no=1)
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
        melt_step = Meltsteps.objects.filter(melt = meltid).filter(step_num = Automelt_info[0].melt_step)[0].step_name
    except:
        melt_step = "---"
    step_total_time = Automelt_info[0].step_total_time
    step_time_remain = step_total_time - Automelt_info[0].step_time_remain
    deltat_stp = Automelt_info[0].deltat

    template = loader.get_template('FregatMonitoringApp/furnace_info.html')
    context = {'furnace_num': 1,
               'power_sp': power_sp,
               'gas_flow': gas_flow,
               'air_flow': air_flow,
               'o2_flow': o2_flow,
               'alpha': alpha,
               'lambda': lambd,
               'standby': standby,
               'power_mode': power_mode,
               'filter_dp': filter_dp,
               'exhauster_dp': exhauster_dp,
               't_before_filter': t_before_filter,
               'hotflue_p': hotflue_p,
               'hotflue_t': hotflue_t,
               'exhauster_pc': exhauster_pc,
               'hot_flue_gate': hot_flue_gate,
               'over_door_gate': over_door_gate,
               'exhauster_gate': exhauster_gate,
               'round_gate': round_gate,
               'filter3_gate': filter3_gate,
               'drain_gate': drain_gate,    
               'over_door_t': over_door_t,
               'cold_air_t': cold_air_t,
               'deltaT': deltaT,
               'furnace_rotation': furnace_rotation,
               'furnace_current': furnace_current,
               'loading_door_half': loading_door_half,
               'auto_mode': auto_mode,
               'melt_type' : melt_type,
               'melt_step' : melt_step,
               'step_total_time' : step_total_time,
               'step_time_remain' : step_time_remain,
               'deltat_stp' : deltat_stp,
               'shzm_position': shzm_position,
              }

    return HttpResponse(template.render(context, request))

def Furnace_2_info(request):
    
    #горелка
    power_sp = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\HY_F710')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\HY_F710')[0].tagindex]
    gas_flow = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_810B')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\TI_810B')[0].tagindex]
    air_flow = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_810C')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\TI_810C')[0].tagindex]
    o2_flow =  [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\O2Flow')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\O2Flow')[0].tagindex]
    alpha = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\Alpha')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\Alpha')[0].tagindex]
    lambd = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\Lambda')[0].tagindex).order_by('-dateandtime')[0].val,2),
    Tagtable.objects.filter(tagname='MEASURES\Lambda')[0].tagindex]
    standby = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='GENERAL\F711_LOCK')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='GENERAL\F711_LOCK')[0].tagindex]
    power_mode = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='IO\HS1_F711')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='IO\HS1_F711')[0].tagindex]
    

    #горячий газоход
    hotflue_p = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PI_702')[0].tagindex).order_by('-dateandtime')[0].val,1),
    Tagtable.objects.filter(tagname='MEASURES\PI_702')[0].tagindex]
    hotflue_t = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_705A')[0].tagindex).order_by('-dateandtime')[0].val,1),
    Tagtable.objects.filter(tagname='MEASURES\TI_705A')[0].tagindex]
    
    #фильтр
    filter_dp = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PDI_725')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\PDI_725')[0].tagindex] 
    t_before_filter = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_708')[0].tagindex).order_by('-dateandtime')[0].val,1), 
    Tagtable.objects.filter(tagname='MEASURES\TI_708')[0].tagindex]
    
    #дымосос
    exhauster_dp = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PDI_729')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\PDI_729')[0].tagindex]
    exhauster_pc = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\SI_U721')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='MEASURES\SI_U721')[0].tagindex]

    #дроссели
    hot_flue_gate = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\PY_702')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\PY_702')[0].tagindex]
    over_door_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\ZI_704')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='MEASURES\ZI_704')[0].tagindex]
    exhauster_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\ZI_706')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='MEASURES\ZI_706')[0].tagindex]
    round_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\\xvi_v_cech')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='MEASURES\\xvi_v_cech')[0].tagindex]
    filter3_gate = [Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\XVI_708')[0].tagindex).order_by('-dateandtime')[0].val,
    Tagtable.objects.filter(tagname='MEASURES\XVI_708')[0].tagindex]
    drain_gate = ["открыт" if not Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='VALVES\XV702_ZL')[0].tagindex).order_by('-dateandtime')[0].val else "закрыт",
    Tagtable.objects.filter(tagname='VALVES\XV702_ZL')[0].tagindex]

    #дельта
    over_door_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_711Y')[0].tagindex).order_by('-dateandtime')[0].val
    cold_air_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_711X')[0].tagindex).order_by('-dateandtime')[0].val
    deltaT = round(over_door_t - cold_air_t,1)

    #печь
    furnace_rotation = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\SY_KL711')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\SY_KL711')[0].tagindex]
    furnace_current = [round(Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\SI_KL711')[0].tagindex).order_by('-dateandtime')[0].val),
    Tagtable.objects.filter(tagname='MEASURES\SI_KL711')[0].tagindex]
    loading_door_half = ["открыта" if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='VALVES\XVF711P_ZL')[0].tagindex).order_by('-dateandtime')[0].val == 0 else "закрыта",
    Tagtable.objects.filter(tagname='VALVES\XVF711P_ZL')[0].tagindex]
    
    #поезд - не прописан в History
    #train_move = "Едет" if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MOTORS\H750_FB')[0].tagindex).order_by('-dateandtime')[0].val else "Стоит"
    #train_fwd = "вперёд" if Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MOTORS\H750_FWB')[0].tagindex).order_by('-dateandtime')[0].val else "назад"
    #train_fwd = train_fwd if train_move else "---"

    #шзм - не прописан в History
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
    Automelt_info = Automelts.objects.filter(furnace_no=2)
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
        melt_step = Meltsteps.objects.filter(melt = meltid).filter(step_num = Automelt_info[0].melt_step)[0].step_name
    except:
        melt_step = "---"
    step_total_time = Automelt_info[0].step_total_time
    step_time_remain = step_total_time - Automelt_info[0].step_time_remain
    deltat_stp = Automelt_info[0].deltat

    template = loader.get_template('FregatMonitoringApp/furnace_info.html')
    context = {'furnace_num': 2,
               'power_sp': power_sp,
               'gas_flow': gas_flow,
               'air_flow': air_flow,
               'o2_flow': o2_flow,
               'alpha': alpha,
               'lambda': lambd,
               'standby': standby,
               'power_mode': power_mode,
               'filter_dp': filter_dp,
               'exhauster_dp': exhauster_dp,
               't_before_filter': t_before_filter,
               'hotflue_p': hotflue_p,
               'hotflue_t': hotflue_t,
               'exhauster_pc': exhauster_pc,
               'hot_flue_gate': hot_flue_gate,
               'over_door_gate': over_door_gate,
               'exhauster_gate': exhauster_gate,
               'round_gate': round_gate,
               'filter3_gate': filter3_gate,
               'drain_gate': drain_gate,    
               'over_door_t': over_door_t,
               'cold_air_t': cold_air_t,
               'deltaT': deltaT,
               'furnace_rotation': furnace_rotation,
               'furnace_current': furnace_current,
               'loading_door_half': loading_door_half,
               'auto_mode': auto_mode,
               'melt_type' : melt_type,
               'melt_step' : melt_step,
               'step_total_time' : step_total_time,
               'step_time_remain' : step_time_remain,
               'deltat_stp' : deltat_stp,
               'shzm_position': shzm_position,
              }

    return HttpResponse(template.render(context, request))

def AutoMeltTypes_info(request, meltID_1):

    melt_type_list_1 = Melttypes.objects.filter(melt_furnace=1) #Выбираем типы плавок для первой печи(для второй такие же)
    melt_type_list_2 = Melttypes.objects.filter(melt_furnace=2)

    melt_type_name = Melttypes.objects.filter(melt_id=meltID_1)[0].melt_name #Узнаём, как называется этот тип плавки
    meltID_2 = Melttypes.objects.filter(melt_name=melt_type_name, melt_furnace=2)[0].melt_id #По имени вытаскиваем id аналогичной плавки для второй печи

     
    melt_steps_list_1 = Meltsteps.objects.filter(melt=meltID_1) #Выбираем шаги для нужных плавок
    melt_steps_list_2 = Meltsteps.objects.filter(melt=meltID_2)
    
    #Выбираем подшаги для каждого шага каждой плавки
    substeps_list_1 = list() 
    for melt_step in melt_steps_list_1: 
        for substep in [Substeps.objects.filter(step=melt_step.step_id)]:
            substeps_list_1.extend(substep)

    substeps_list_2 = list()
    for melt_step in melt_steps_list_2: 
        for substep in [Substeps.objects.filter(step=melt_step.step_id)]:
            substeps_list_2.extend(substep)

    template = loader.get_template('FregatMonitoringApp/AutoMeltTypes_info.html')
    context = {
        'melts_id': [meltID_1, meltID_2],
        'melt_types_1': melt_type_list_1,
        'melt_types_2': melt_type_list_2,
        'melt_steps_1': melt_steps_list_1,
        'melt_steps_2': melt_steps_list_2,
        'substeps_1' : substeps_list_1,
        'substeps_2' : substeps_list_2
    }

    return HttpResponse(template.render(context, request))

def AutoMelts_SetPoints(request):
    
    template = loader.get_template('FregatMonitoringApp/AutoMeltsSetPoints.html')
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

def AutoMeltsSaveSettings(request, meltID_1, meltID_2): #сохраняет изменение режимов автоплаки в базе
    
    melt_steps_list = Meltsteps.objects.filter(melt__in=[meltID_1, meltID_2]) #Выбираем шаги для нужных плавок

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

    return HttpResponseRedirect(reverse('FregatMonitoringApp:Automelts_info', args=(meltID_1,)))

def AutoMeltsSaveSetpoints(request, furnace_num): #сохраняет изменение уставки Дельты в базе
    try:
        try: 
            float(request.POST["DeltaT"+str(furnace_num)+"_stp"]) #"Это число вообще?"
        except:
            return error_message(request) #Ой, что-то пошло не так
        Melt = Automelts.objects.filter(furnace_no = furnace_num)[0]
        Melt.deltat = request.POST["DeltaT"+str(furnace_num)+"_stp"]
    except: #не удалось записать в базу
        return error_message(request) #Ой, что-то пошло не так
    else:
        Melt.save() 

    return HttpResponseRedirect(reverse('FregatMonitoringApp:AutoMeltsSetPoints'))



#----------ОТОБРАЖЕНИЯ ЧЕРЕЗ СЕРИАЛАЙЗЕРЫ-------------------
def Furnace_info_s(request, SignalIndex): # API для обновления данных на экране "Печь 1(2)"
    
    tag_val = Floattable.objects.filter(tagindex=SignalIndex).order_by('-dateandtime')[:1]

    serializer = FloattableSerializer(tag_val, many=True)

    #----Исключения 1 печь----------------
    if SignalIndex == 13: #нагрузка на печь
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 51: #вращение печи
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 52: #дроссель горячего газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],0)
    if SignalIndex == 25: #температура гор.газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 26: #температура перед фильтром
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 115: #лямбда
        serializer.data[0]['val'] = round(serializer.data[0]['val'],2)
    if SignalIndex == 85: #сливной дроссель
        serializer.data[0]['val'] = "открыт" if not serializer.data[0]['val'] else "закрыт"
    if SignalIndex == 117: #дроссель круглый
        serializer.data[0]['val'] = serializer.data[0]['val']-256
    if SignalIndex == 118: #дроссель над дверью
        serializer.data[0]['val'] = serializer.data[0]['val']-512
    if SignalIndex == 121: #дроссель на 3 фильтр
        serializer.data[0]['val'] = serializer.data[0]['val']-1280
    if SignalIndex == 123: #дроссель дымососа
        serializer.data[0]['val'] = serializer.data[0]['val']-1792

    #----Исключения 1 печь----------------
    if SignalIndex == 14: #нагрузка на печь
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 17: #вращение печи
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 75: #дроссель горячего газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],0)
    if SignalIndex == 27: #температура гор.газохода
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 31: #температура перед фильтром
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)
    if SignalIndex == 63: #лямбда
        serializer.data[0]['val'] = round(serializer.data[0]['val'],2)
    if SignalIndex == 81: #сливной дроссель
        serializer.data[0]['val'] = "открыт" if not serializer.data[0]['val'] else "закрыт"
    if SignalIndex == 9: #перепад на дымососе
        serializer.data[0]['val'] = round(serializer.data[0]['val'])
    if SignalIndex == 12: #разряжение в гор. газоходе
        serializer.data[0]['val'] = round(serializer.data[0]['val'],1)

    return JsonResponse(serializer.data, safe=False)

def Furnace_info_a(request, FurnaceNo): # API для обновления данных о автоплавке на экране "Печь 1(2)"

    melt_inst = Automelts.objects.filter(furnace_no=FurnaceNo)[0]
    melt_type_inst = Melttypes.objects.filter(melt_num = melt_inst.melt_type)[0]
    step_type_inst = Meltsteps.objects.filter(step_num = melt_inst.melt_step).filter(melt = melt_type_inst.melt_id)[0]

    #дельта
    if FurnaceNo == 1:
        over_door_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_712Y')[0].tagindex).order_by('-dateandtime')[0].val
        cold_air_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_712X')[0].tagindex).order_by('-dateandtime')[0].val
    elif FurnaceNo == 2:
        over_door_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_711Y')[0].tagindex).order_by('-dateandtime')[0].val
        cold_air_t = Floattable.objects.filter(tagindex=Tagtable.objects.filter(tagname='MEASURES\TI_711X')[0].tagindex).order_by('-dateandtime')[0].val
    deltaT = over_door_t - cold_air_t
    
    AMmodel = AutoMeltsInfo(
        furnace_no = FurnaceNo,
        auto_mode = "Автомат" if melt_inst.auto_mode else "Ручной",
        melt_name = melt_type_inst.melt_name,
        step_name = step_type_inst.step_name,
        step_total_time = melt_inst.step_total_time,
        step_time_remain = melt_inst.step_total_time - melt_inst.step_time_remain,
        deltat = round(deltaT,1),
        deltat_stp = melt_inst.deltat
    )

    serializer = AutomeltsSerializer(AMmodel)

    return JsonResponse(serializer.data, safe=False)