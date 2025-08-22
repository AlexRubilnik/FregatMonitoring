'''Скрипт для переноса графиков ППР из Exel'''
import pyodbc

service = 'АСУТП'
freq_days = ''
risk = ''

locations = list() #участки
equipments = list() #оборудование
sections = list() #разделы
nodes = list() #узлы
works = list() #работы
tools = list() #инструменты
staff_positions = list() #должности персонала выполняющего работу
time_min = list() #плановое время (мин.)

def check_location_in_DB(conn, loc):
    sql_query = f"SELECT Id, Name FROM Locations WHERE Name='{loc}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0] #узнаём id
    else:
        return -1

def add_loc_to_BD(conn, loc):
    sql_query = f"INSERT INTO Locations (Name) VALUES ('{loc}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()

def check_equipment_in_DB(conn, eqp, loc_id):
    sql_query = f"SELECT Id, Name FROM Equipment WHERE Name='{eqp}' AND Location_id='{loc_id}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0] #узнаём id
    else:
        return -1

def add_eqp_to_BD(conn, eqp, loc_id):
    sql_query = f"INSERT INTO Equipment (Name, Location_id) VALUES ('{eqp}', '{loc_id}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()

def check_sec_in_DB(conn, sec, eqp_id):
    sql_query = f"SELECT Id, Name FROM Sections WHERE Name='{sec}' AND Equipment_id='{eqp_id}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0] #узнаём id
    else:
        return -1

def add_sec_to_BD(conn, sec, eqp_id):
    sql_query = f"INSERT INTO Sections (Name, Equipment_id) VALUES ('{sec}', '{eqp_id}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()

def check_node_in_DB(conn, node, sec_id):
    sql_query = f"SELECT Id, Name FROM Nodes WHERE Name='{node}' AND Section_id='{sec_id}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0] #узнаём id
    else:
        return -1

def add_node_to_BD(conn, node, sec_id):
    sql_query = f"INSERT INTO Nodes (Name, Section_id) VALUES ('{node}', '{sec_id}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()

def check_work_in_DB(conn, work, node_id):
    sql_query = f"SELECT Id, Operation_content FROM Repair_operations WHERE Operation_content LIKE '{work}' AND Node_id='{node_id}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0] #узнаём id
    else:
        return -1

def add_work_to_BD(conn, work, tools, time_min, staff_pos_id, freq_days, node_id, risk):
    sql_query = f"INSERT INTO Repair_operations (Operation_content, Tools, Time_min, Staff_position_id, Periodicity_days, Node_id, Risk) VALUES ('{work}', '{tools}', '{time_min}', '{staff_pos_id}', '{freq_days}', '{node_id}', '{risk}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()

def check_staff_pos_in_DB(conn, staff_pos, serv_id):
    sql_query = f"SELECT Id, Name FROM Staff_positions WHERE Name='{staff_pos}' AND Service_id='{serv_id}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0] #узнаём id
    else:
        return -1

def add_staff_pos_to_BD(conn, staff_pos, serv_id):
    sql_query = f"INSERT INTO Staff_positions (Name, Service_id) VALUES ('{staff_pos}', '{serv_id}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()


server = 'FRGV202X\PRODUCTION'
database = 'SPR'
user = 'Operator'
pwd = 'fregat'
connectionString = f'DRIVER={{SQL Server Native Client 11.0}};SERVER={server};DATABASE={database};UID={user};PWD={pwd}'
conn = pyodbc.connect(connectionString)

#Ищем службу в БД
sql_query = f"SELECT Id, Name FROM Services WHERE Name='{service}'"
cursor = conn.cursor()
cursor.execute(sql_query)
res = cursor.fetchall()
if len(res) > 0:
    serv_id = res[0][0] #узнаём id
else: #не нашли - добавляем
    sql_query = f"INSERT INTO Services (Name) VALUES ('{service}')"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()
    sql_query = f"SELECT Id, Name FROM Services WHERE Name='{service}'"
    cursor = conn.cursor()
    cursor.execute(sql_query)
    res = cursor.fetchall()
    try:
        if len(res) > 0:
            serv_id = res[0][0] #узнаём id
        else:
            assert False, f'Не могу добавить службу'
    except Exception as err:
        print(err)

with open('Z:\\Администрация\\03-Производственный Отдел\\8. РЕМОНТНЫЕ СЛУЖБЫ\\АСУТП\\ППР 2025г АСУТП.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for n, line in enumerate(lines):
        s = line.split(';')
        try:
            locations.append(s[1])
            equipments.append(s[3])
            sections.append(s[4])
            nodes.append(s[5])
            works.append(s[6])
            tools.append(s[7])
            staff_positions.append(s[11])
            time_min.append(s[15])

        except:
            print(f'Ошибка парсинга строки {n+1}')

    #print(works)
    for n, work in enumerate(works):
        loc = locations[n] #участок
        eqp = equipments[n] #оборудование
        sec = sections[n] #раздел
        node = nodes[n] #узел
        tool = tools[n] #инструменты
        staff_pos = staff_positions[n] #должность
        time = time_min[n] #плановое время


        #проверяем есть ли в базе такой участок
        loc_id = check_location_in_DB(conn, loc)
        if loc_id == -1:
            add_loc_to_BD(conn, loc) #если нет - добавляем
            try:
                loc_id = check_location_in_DB(conn, loc) #Проверяем что добавили
                assert loc_id != -1, f'Не удалось добавить в базу {loc}'
            except Exception as err:
                print(err)

        #проверяем есть ли в базе такое оборудование на таком участке
        eqp_id = check_equipment_in_DB(conn, eqp, loc_id)
        if eqp_id == -1:
            add_eqp_to_BD(conn, eqp, loc_id) #если нет - добавляем
            try:
                eqp_id = check_equipment_in_DB(conn, eqp, loc_id) #Проверяем что добавили
                assert eqp_id != -1, f'Не удалось добавить в базу {eqp}'
            except Exception as err:
                print(err)

        #проверяем есть ли в базе такой раздел на таком оборудовании
        sec_id = check_sec_in_DB(conn, sec, eqp_id)
        if sec_id == -1:
            add_sec_to_BD(conn, sec, eqp_id) #если нет - добавляем
            try:
                sec_id = check_sec_in_DB(conn, sec, eqp_id) #Проверяем что добавили
                assert sec_id != -1, f'Не удалось добавить в базу {sec}'
            except Exception as err:
                print(err)

        #проверяем есть ли в базе такой узел на таком разделе
        node_id = check_node_in_DB(conn, node, sec_id)
        if node_id == -1:
            add_node_to_BD(conn, node, sec_id) #если нет - добавляем
            try:
                node_id = check_node_in_DB(conn, node, sec_id) #Проверяем что добавили
                assert node_id != -1, f'Не удалось добавить в базу {node}'
            except Exception as err:
                print(err)

        #проверяем есть ли в базе такая должность в этой службе
        staff_pos_id = check_staff_pos_in_DB(conn, staff_pos, serv_id)
        if staff_pos_id ==-1:
            add_staff_pos_to_BD(conn, staff_pos, serv_id) #если нет - добавляем
            try:
                staff_pos_id = check_staff_pos_in_DB(conn, staff_pos, serv_id) #Проверяем что добавили
                assert staff_pos_id != -1, f'Не удалось добавить в базу {staff_pos}'
            except Exception as err:
                print(err)

        #проверяем, есть ли в базе такая работа для такого узла
        work_id = check_work_in_DB(conn, work, node_id)
        if work_id == -1:
            add_work_to_BD(conn, work, tool, time, staff_pos_id, freq_days, node_id, risk)
            try:
                work_id = check_work_in_DB(conn, work, node_id) #Проверяем что добавили
                assert work_id != -1, f'Не удалось добавить в базу {work}'
            except Exception as err:
                print(err)



    #sql_query = f"INSERT INTO Locations (Name) VALUES ('{s[1]}')"

    #cursor.execute(sql_query)
    #conn.commit()