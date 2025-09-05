var marker_run = false;

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
    uncompleted_list_update();
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
    uncompleted_list_update();
  }  
}


function uncompleted_list_update(){ 
  week = Number(document.getElementById('week').innerText);
  data_download_marker_on_off(false); //Показываем маркер "Подождите. Идёт загрузка данных..."
  marker_run=true; //Запускаем бегущий маркер
  charts_tables_on_off(true); //Убираем таблицы и графики
 
  var XHR = new XMLHttpRequest()
      request_str = "/SPR/uncompleted_list_update/"+String(week)+"/";    
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
      document.getElementById("op_scheduled").innerHTML = data[1].op_scheduled
      document.getElementById("op_completed").innerHTML = data[1].op_completed
      document.getElementById("elapsed_time").innerHTML = data[1].elapsed_time
      document.getElementById("elapsed_time_avg").innerHTML = data[1].elapsed_time_avg
      document.getElementById("num_of_staff").innerHTML = data[1].num_of_staff
      marker_run=false; //Останавливаем бегущий маркер
      data_download_marker_on_off(true); //Скрываем маркер "Подождите. Идёт загрузка данных..."
      charts_tables_on_off(false); //Показываем таблицы и графики
      table = RenderLog(data[0])   
      table.tableBuilt = function(table){
      };

  };
  delete(XHR);  
     
}


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


//Build Tabulator
function RenderLog(TableData){
  let table_data = []
  for (let i = 0; i < TableData.length; i++){   
      stat = TableData[i].status;
      staff = TableData[i].staff;

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
        work : TableData[i].work,
        cur_status: cur_status,
        comment : TableData[i].comment,
      }   
      table_data.push(row)

  }
  
  var table = new Tabulator("#week-report-table", {
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
            {title:"Комментарий", field:"comment", cssClass: "columns_12px", hozAlign:"center", width:200, formatter:"textarea"},
            {title:"Статус", field: "cur_status", cssClass: "columns_12px", formatter: "html" , width:150, hozAlign:"center"},
          ],

  });

  return table
} //RenderTable

document.getElementById('week_minus').onclick=btn_week_minus;
document.getElementById('week_plus').onclick=btn_week_plus;
table = uncompleted_list_update()
