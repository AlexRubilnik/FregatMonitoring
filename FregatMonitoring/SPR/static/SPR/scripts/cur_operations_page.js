var marker_run = false;

cur_staff = document.getElementById("user_position").innerText; //должность пользователя
cur_staff_=cur_staff.replaceAll(' ', '').replaceAll('\n', '') //без пробелов

if (cur_staff_ == 'СлесарьКИПиА'){
  document.getElementById('week_minus').style.display="none";
  document.getElementById('week_plus').style.display="none";
}

function btn_week_minus(){
  cur_week = document.getElementById('week').innerText;
  if( cur_week>1){
    document.getElementById('week').innerText = String(Number(cur_week)-1);
    let st_d = document.getElementById('start_date').innerText;
    let new_st_d = new Date(st_d.slice(-4,) +"-"+st_d.slice(3,5)+"-"+st_d.slice(0,2));
    new_st_d.setDate(new_st_d.getDate()  - 7);
    let f_d = document.getElementById('finish_date').innerText;
    let new_f_d= new Date(f_d.slice(-4,) +"-"+f_d.slice(3,5)+"-"+f_d.slice(0,2));
    new_f_d.setDate(new_f_d.getDate()  - 7);
    let st_d_d_0 ="";
    let st_d_m_0 ="";
    let f_d_d_0 ="";
    let f_d_m_0 ="";
    if(new_st_d.getDate()<10){
      st_d_d_0 = "0"
    } 
    if(new_st_d.getMonth()<9){
      st_d_m_0 = "0"
    } 
    if(new_f_d.getDate()<10){
      f_d_d_0 = "0"
    } 
    if(new_f_d.getMonth()<9){
      f_d_m_0 = "0"
    } 
    document.getElementById('start_date').innerText =  st_d_d_0 + new_st_d.getDate()+"."+st_d_m_0+String(Number(new_st_d.getMonth())+1)+"."+new_st_d.getFullYear();
    document.getElementById('finish_date').innerText =  f_d_d_0 + new_f_d.getDate()+"."+f_d_m_0+String(Number(new_f_d.getMonth())+1)+"."+new_f_d.getFullYear();
    cur_operations_list_update();
  }
}
function btn_week_plus(){
  cur_week = document.getElementById('week').innerText;
  if(cur_week < 52){
    document.getElementById('week').innerText = String(Number(cur_week)+1);
    let st_d = document.getElementById('start_date').innerText;
    let new_st_d = new Date(st_d.slice(-4,) +"-"+st_d.slice(3,5)+"-"+st_d.slice(0,2));
    new_st_d.setDate(new_st_d.getDate()  + 7);
    let f_d = document.getElementById('finish_date').innerText;
    let new_f_d= new Date(f_d.slice(-4,) +"-"+f_d.slice(3,5)+"-"+f_d.slice(0,2));
    new_f_d.setDate(new_f_d.getDate()  + 7);
    let st_d_d_0 ="";
    let st_d_m_0 ="";
    let f_d_d_0 ="";
    let f_d_m_0 ="";
    if(new_st_d.getDate()<10){
      st_d_d_0 = "0"
    } 
    if(new_st_d.getMonth()<9){
      st_d_m_0 = "0"
    } 
    if(new_f_d.getDate()<10){
      f_d_d_0 = "0"
    } 
    if(new_f_d.getMonth()<9){
      f_d_m_0 = "0"
    } 
    document.getElementById('start_date').innerText =  st_d_d_0 + new_st_d.getDate()+"."+st_d_m_0+String(Number(new_st_d.getMonth())+1)+"."+new_st_d.getFullYear();
    document.getElementById('finish_date').innerText =  f_d_d_0 + new_f_d.getDate()+"."+f_d_m_0+String(Number(new_f_d.getMonth())+1)+"."+new_f_d.getFullYear();
    cur_operations_list_update();
  }  
}


function cur_operations_list_update(){ 
  week = Number(document.getElementById('week').innerText);
  data_download_marker_on_off(false); //Показываем маркер "Подождите. Идёт загрузка данных..."
  marker_run=true; //Запускаем бегущий маркер
  charts_tables_on_off(true); //Убираем таблицы и графики
 
  var XHR = new XMLHttpRequest()
      request_str = "/SPR/cur_operations_list_update/"+String(week)+"/";    
      let q_flag = false;

      XHR.open('GET', request_str, true);
      //XHR.timeout = 2000;
      XHR.send();

  XHR.onreadystatechange = function() {
      if (this.readyState == 4) {
             //запрос завершён
      }           
      if (this.readyState != 4) return;

      if (this.status != 200) {
        marker_run=false; //Останавливаем бегущий маркер
        data_download_marker_on_off(true); //Скрываем маркер "Подождите. Идёт загрузка данных..."
        alert('Произошла ошибка при загрузке данных!')
        return;
      }  
        
      data = JSON.parse(this.responseText); 
      marker_run=false; //Останавливаем бегущий маркер
      data_download_marker_on_off(true); //Скрываем маркер "Подождите. Идёт загрузка данных..."
      charts_tables_on_off(false); //Показываем таблицы и графики
      table = RenderLog(data)   
      table.tableBuilt = function(table){
      };

  };
  delete(XHR);  
     
}


function update_status_btn(cell, status, another_staff){
  staff = document.getElementById("user_staff").innerText;
  if (another_staff!="" && another_staff!="available"){//Уже выполняет или выполнил другой сотрудник
    alert('Операцию уже выполняет '+another_staff+'. Обновите страницу!')
    return
  }
  if (another_staff=="available"){
    if (status=='start'){ 
      cell.setValue("<btn name='work_start_btn' id='work_start_btn'>Завершить операцию</btn>");
      cell.getRow().getCell('cancel').setValue("<btn name='work_start_btn' id='work_start_btn'>Отказаться</btn>");
      cell.getRow().getCell('cur_status').setValue("<p style='color: black;'>Выполняет: </p>"+ staff);
    } 
    if (status=='stop'){ 
      cell.setValue("");
      cell.getRow().getCell('cancel').setValue("")
      cell.getRow().getCell('cur_status').setValue(cur_status="<p style='color: green;'>Выполнил: </p>"+ staff);
    } 
    if (status=='cancel'){ 
      cell.setValue("");
      cell.getRow().getCell('start').setValue("<btn name='work_start_btn' id='work_start_btn'>Начать операцию</btn>");
      cell.getRow().getCell('cur_status').setValue("<p style='color: orange;'>Ожидает выполнения</p>");
    } 
  } 
}

function update_operation_status(cell, sch_op_id, week, status){ 

    var XHR = new XMLHttpRequest()
    request_str = "/SPR/update_operation_status/"+sch_op_id+"/"+week+"/"+status+"/";
    XHR.open('GET', request_str, true);
    XHR.send();
    let upd_status = undefined;
    XHR.onreadystatechange = function() {
        if (this.status != 200) {
          alert('Произошла ошибка при обновлении данных!')
        }  
        if (this.status == 200) {
          operation_staff = this.responseText 
          update_status_btn(cell, status, operation_staff)
        } 
    };
   
    delete(XHR);
    return
};

function update_repair_operation_data(work_id, field, new_data){ 

  var XHR = new XMLHttpRequest()
  request_str = "/SPR/sch_repair_operations_editor/"+work_id+"/"+field+"/"+new_data+"/";
  XHR.open('GET', request_str, true);
  XHR.send();
  let upd_status = undefined;
  XHR.onreadystatechange = function() {
      if (this.status != 200) {
        alert('Произошла ошибка при обновлении данных!')
        upd_status = false;
      }  
      if (this.status == 200) {
        upd_status = true   
      } 
  };
 
  delete(XHR);
  return upd_status
};

function data_download_marker_on_off(hidden){
  //Скрываем маркер "Подождите. Идёт загрузка данных..."
  document.getElementById("data-download-marker").hidden = hidden
  document.getElementById("ddm1").hidden = hidden
  document.getElementById("ddm2").hidden = hidden
  document.getElementById("ddm3").hidden = hidden
}

setInterval(function data_download_marker_run(){
  //Бегущий маркер "Подождите. Идёт загрузка данных..."
  if(marker_run) {
      if(document.getElementById("ddm1").hidden==true){ //все точки скрыты
          document.getElementById("ddm1").hidden = false //показываем первую
      } else if(document.getElementById("ddm2").hidden==true) {
          document.getElementById("ddm2").hidden = false //показываем вторую
      } else if(document.getElementById("ddm3").hidden==true) {
          document.getElementById("ddm3").hidden = false //показываем третью
      } else { 
          document.getElementById("ddm1").hidden = true //скрываем все
          document.getElementById("ddm2").hidden = true //скрываем все
          document.getElementById("ddm3").hidden = true //скрываем все
      }
  }
}, 500);


function charts_tables_on_off(hidden){ //Прячет содержимое страницы при загрузке новых данных
  var hidden_t = "1"
  if (hidden) {hidden_t="0"}
  try{
      document.getElementById("cur-operations-block").style['opacity'] = hidden_t
  } catch {}
}


var start_btn = function(e, cell){
    week = Number(document.getElementById("week").innerText);
    cur_status = cell.getValue();
    if(cur_status=="<btn name='work_start_btn' id='work_start_btn'>Начать операцию</btn>"){
        start_operation = confirm("Подтвердите, что хотите начать обслуживание")
        if (start_operation){
            sch_op_id = cell.getRow().getCells()[0].getValue()
            update_operation_status(cell, sch_op_id, week, 'start') 
        }
    }
    if(cur_status=="<btn name='work_start_btn' id='work_start_btn'>Завершить операцию</btn>"){
        start_operation = confirm("Подтвердите, что хотите закончить обслуживание")
        if (start_operation){
            sch_op_id = cell.getRow().getCells()[0].getValue()
            update_operation_status(cell, sch_op_id, week, 'finish')
        }
    }

}

var cancel_btn = function(e, cell){
    week = Number(document.getElementById("week").innerText);
    stop_operation = confirm("Подтвердите, что хотите отменить обслуживание")
        if (stop_operation){
            sch_op_id = cell.getRow().getCells()[0].getValue();
            update_operation_status(cell, sch_op_id, week, 'cancel');
        }
}

var per_dateEditor = function(cell, onRendered, success, cancel){
  //cell - the cell component for the editable cell
  //onRendered - function to call when the editor has been rendered
  //success - function to call to pass thesuccessfully updated value to Tabulator
  //cancel - function to call to abort the edit and return to a normal cell

  //create and style input
  var cellValue = cell.getValue()
  var row_id = cell.getRow().getCells()[0].getValue() //получаем id операции
  input = document.createElement("input");
  input.style.padding = "4px";
  input.style.width = "100%";
  input.style.boxSizing = "border-box";

  input.value = cellValue;

  onRendered(function(){
      input.focus();
      input.style.height = "100%";
  });

  function onChange(){
      if(input.value != cellValue){
          staff = document.getElementById("user_staff").innerText;
          if (input.value == ""){
            success(input.value+" ");
          }else {
            success(staff+": "+input.value);
          }
      }else{
          cancel();
      }
  }

  //submit new value on blur or change
  input.addEventListener("blur", onChange);

  //submit new value on enter
  input.addEventListener("keydown", function(e){
      if(e.keyCode == 13){
        onChange()        
      }
      if(e.keyCode == 27){
          cancel();
      }
  });

  return input;
};


//Build Tabulator
function RenderLog(TableData){
  cur_staff = document.getElementById("user_staff").innerText;
  cur_staff_=cur_staff.replaceAll(' ', '').replaceAll('\n', '') //без пробелов
  let table_data = []
  for (let i = 0; i < TableData.length; i++){   
      stat = TableData[i].status;
      staff = TableData[i].staff;
      staff_= staff.replaceAll(' ', '').replaceAll('\n', '') //без пробелов
      let btn="";
      let cancel_btn="";
      if (stat == 0){ //ожидает выполнения
        btn = "<btn name='work_start_btn' id='work_start_btn'>Начать операцию</btn>"
        cancel_btn="";
      }
      else if(stat == 1 && (staff_==cur_staff_)){ //выполняется
        btn = "<btn name='work_start_btn' id='work_start_btn'>Завершить операцию</btn>";  
        cancel_btn = "<btn name='work_start_btn' id='work_start_btn'>Отказаться</btn>";
      }
      else if(stat == 2){ //Выполнена
        btn = ""
        cancel_btn="";
      }
      else if(stat == 3){ //Просрочена
        btn = ""
        cancel_btn="";
      }

      cur_status = "<p style='color: orange;'>Ожидает выполнения</p>";
      if (TableData[i].staff != "" && stat==1) {
        cur_status="<p style='color: black;'>Выполняет:</p>"+ staff + "<p>c "+TableData[i].start_timestamp+"</p>";
      }
      if (TableData[i].staff != "" && stat==2) {
        cur_status="<p style='color: green;'>Выполнил:</p>"+ staff + "<p>c "+TableData[i].start_timestamp+"</p><p>по "+TableData[i].finish_timestamp+"</p>";
      }
      if (stat==3) {
        cur_status = "<p style='color: red;'>Просрочена</p>";
      }
      let row = { 
        sch_op_id: TableData[i].sch_op_id,
        id : TableData[i].id,
        loc : TableData[i].loc,
        eqp : TableData[i].eqp,
        sect : TableData[i].sect,
        node : TableData[i].node,
        staff_pos : TableData[i].staff_pos,
        staff: TableData[i].staff,
        tools : TableData[i].tools,
        work : TableData[i].work,
        cur_status: cur_status,
        start : btn,
        cancel : cancel_btn,
        comment : TableData[i].comment,
      }   
      table_data.push(row)

  }
  
  var table = new Tabulator("#cur-operations-table", {
  placeholder:"Нет данных",
  data: table_data,
  title:"Перечень оборудования",
  layout:"fitColumns",
  groupBy:["loc", "eqp", "sect"],
  groupStartOpen:true,
  groupToggleElement:"header",
          columns: [
            {title:"sch_op_id", field:"sch_op_id", hozAlign:"center", width:20, formatter:"textarea", visible:false},
            {title:"ID", field:"id", hozAlign:"center", width:20, formatter:"textarea"},
            {title:"Участок", field:"loc", hozAlign:"center", width:180, formatter:"textarea", visible: false},
            {title:"Оборудование", field:"eqp", hozAlign:"right", sorter:"number", width:100, formatter:"textarea", visible: false},
            {title:"Раздел", field:"sect", hozAlign:"center", width:180, formatter:"textarea", visible: false},
            {title:"Узел", field:"node", hozAlign:"center", width:140, formatter:"textarea"},
            {title:"Работа", field:"work", hozAlign:"center", width:520, formatter:"textarea"},
            {title:"Исполнитель", field:"staff_pos", hozAlign:"center", width:140, formatter:"textarea"},
            {title:"Инструмент", field:"tools", hozAlign:"center", width:140, formatter:"textarea"},
            {title:"Комментарий", field:"comment", cssClass: "columns_12px", hozAlign:"center", width:200, formatter:"textarea", editor:per_dateEditor},
            {title:"Статус", field: "cur_status", cssClass: "columns_12px", formatter: "html" , width:150, hozAlign:"center"},
            {title:"", field: "start", formatter: "html" , width:150, hozAlign:"center", cellClick:start_btn},
            {title:"", field: "cancel", formatter: "html" , width:100, hozAlign:"center", cellClick:cancel_btn},
          ],

  });
  table.on("cellEdited", function(cell){
    //cell - cell component
    col_name = cell.getColumn().getField()
    var row_id = cell.getRow().getCells()[0].getValue() //получаем id операции
    if(col_name=="comment"){
      update_repair_operation_data(row_id, col_name, cell.getValue()); 
    }  
  });

  return table
} //RenderTable

document.getElementById('week_minus').onclick=btn_week_minus;
document.getElementById('week_plus').onclick=btn_week_plus;
table = cur_operations_list_update()
