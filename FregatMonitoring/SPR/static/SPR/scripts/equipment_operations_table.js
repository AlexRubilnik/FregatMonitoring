var marker_run = false;

const windowInnerWidth = document.documentElement.clientWidth
const windowInnerHeight = document.documentElement.clientHeight
table = document.getElementById("equipment-operations-table")
table.style.maxWidth = String(windowInnerWidth)+"px"
table.style.maxHeight =String( windowInnerHeight-250)+"px"

function equipment_list_update(){ 
  let loc = document.getElementById('location').value; 
  let url = new URL("/SPR/equipment_page/", window.location.origin);
  url.searchParams.set('location', String(loc));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
        let eqp_list_div = document.getElementById('equipment_filters');
        let sect_list_div = document.getElementById('section_filters'); 
        let node_list_div = document.getElementById('node_filters');
        eqp_list_div.innerHTML = "Оборудование: " + this.responseText;
        if(sect_list_div){
          sect_list_div.innerHTML=""
        }
        if(node_list_div){
          node_list_div.innerHTML=""
        }
        last_operations_list_update()
    }
  };
  
  delete(XHR);       
}

function sections_list_update(){ 
  let eqp = document.getElementById('equipment').value; 
  let url = new URL("/SPR/equipment_page/", window.location.origin);
  url.searchParams.set('equipment', String(eqp));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      let sect_list_div = document.getElementById('section_filters');
      let node_list_div = document.getElementById('node_filters');
      sect_list_div.innerHTML = "Раздел: " + this.responseText;
      if(node_list_div){
        node_list_div.innerHTML=""
      }
      last_operations_list_update()
    }
  };
  delete(XHR);      
}

function nodes_list_update(){ 
  let sect = document.getElementById('section').value; 
  let url = new URL("/SPR/equipment_page/", window.location.origin);
  url.searchParams.set('section', String(sect));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      let node_list_div = document.getElementById('node_filters');
      node_list_div.innerHTML = "Узел: " + this.responseText;
      last_operations_list_update()
    }
  };
  delete(XHR);      
}

function last_operations_list_update(){ 
  if(document.getElementById('location') != null){
    loc = Number(document.getElementById('location').value);
  } else {
    loc = "-1"
  }
  if(document.getElementById('equipment') != null){
    eqp = Number(document.getElementById('equipment').value);
  } else {
    eqp = "-1"
  }
  if(document.getElementById('section') != null){
    sect = Number(document.getElementById('section').value);
  } else {
    sect = "-1"
  }
  if(document.getElementById('node') != null){
    node = Number(document.getElementById('node').value);
  } else {
    node = "-1"
  } 
 
  data_download_marker_on_off(false); //Показываем маркер "Подождите. Идёт загрузка данных..."
  marker_run=true; //Запускаем бегущий маркер
  charts_tables_on_off(true); //Убираем таблицы и графики
 
  var XHR = new XMLHttpRequest()
  request_str = "/SPR/last_operations_list/"+String(loc)+"/"+String(eqp)+"/"+String(sect)+"/"+String(node)+"/";    
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
      document.getElementById("equipment-operations-block").style['opacity'] = hidden_t
  } catch {}
}


//Build Tabulator
function RenderLog(TableData){
  let table_data = []
  for (let i = 0; i < TableData.length; i++){   
      let row = { 
        sch_op_id: TableData[i].sch_op_id,
        id : TableData[i].id,
        loc : TableData[i].loc,
        eqp : TableData[i].eqp,
        sect : TableData[i].sect,
        node : TableData[i].node,
        staff_pos : TableData[i].staff_pos,
        staff: TableData[i].staff,
        work : TableData[i].work,
        comment : TableData[i].comment,
        start: TableData[i].start_timestamp,
        finish: TableData[i].finish_timestamp,
        elapsed_time: TableData[i].elapsed_time
      }   
      table_data.push(row)

  }
  
  var table = new Tabulator("#equipment-operations-table", {
  layout:window.innerWidth > 800 ? "fitColumns" : "fitData",
  placeholder:"Нет данных",
  data: table_data,
  title:"Последние операции",
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
            {title:"Исполнитель", field:"staff", hozAlign:"center", width:140, formatter:"textarea"},
            {title:"Комментарий", field:"comment", cssClass: "columns_12px", hozAlign:"center", width:200, formatter:"textarea"},
            {title:"Начало", field:"start", hozAlign:"center", width:140, formatter:"datetime", formatterParams:{
              inputFormat:"dd-MM-yyyy HH:mm:ss",
              outputFormat:"dd-MM-yyyy HH:mm:ss",
              invalidPlaceholder:"(invalid date)",
              }},
            {title:"Окончание", field:"finish", hozAlign:"center", width:140, formatter:"datetime", formatterParams:{
              inputFormat:"dd-MM-yyyy HH:mm:ss",
              outputFormat:"dd-MM-yyyy HH:mm:ss",
              invalidPlaceholder:"(invalid date)",
              }},
            {title:"Время(мин.)", field:"elapsed_time", hozAlign:"center", width:140, formatter:"textarea"},
          ],

  });

  return table
} //RenderTable

//table = last_operations_list_update()
