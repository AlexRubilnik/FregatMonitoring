var marker_run = false;

const windowInnerWidth = document.documentElement.clientWidth
const windowInnerHeight = document.documentElement.clientHeight
table = document.getElementById("equipment-tree-table")
table.style.maxWidth = String(windowInnerWidth-50)+"px"
table.style.maxHeight =String( windowInnerHeight-550)+"px"
loc = document.getElementById('location').value
if(loc==""){ //При загрузке страницы
  equipment_list_update()
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function equipment_list_update(){ 
  let form = document.getElementById('new_operation_form'); //убираем форму добавления операции, если была открыта
  form.innerHTML = "";
  let form_1 = document.getElementById('new_entity_form'); //убираем форму добавления сущности, если была открыта
  form_1.innerHTML = "";
  let loc = document.getElementById('location').value; 
  let url = new URL("/SPR/equipment_service_page/", window.location.origin);
  url.searchParams.set('location', String(loc));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
        let eqp_list_div = document.getElementById('equipment_filters');
        let sect_list_div = document.getElementById('section_filters'); 
        let node_list_div = document.getElementById('node_filters');
        if(this.responseText==""){
          if(eqp_list_div){eqp_list_div.innerHTML=""}
        } else {
          eqp_list_div.innerHTML = "Оборудование: " + this.responseText;
        }
        if(sect_list_div){
          sect_list_div.innerHTML=""
        }
        if(node_list_div){
          node_list_div.innerHTML=""
        }
        download_equipment_tree()
    }
  };
  
  delete(XHR);       
}

function sections_list_update(){ 
  let form = document.getElementById('new_operation_form'); //убираем форму добавления операции, если была открыта
  form.innerHTML = "";
  let form_1 = document.getElementById('new_entity_form'); //убираем форму добавления сущности, если была открыта
  form_1.innerHTML = "";
  let eqp = document.getElementById('equipment').value; 
  if (eqp == ""){
    equipment_list_update()
    return
  }
  let url = new URL("/SPR/equipment_service_page/", window.location.origin);
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
      download_equipment_tree()
    }
  };
  delete(XHR);      
}

function nodes_list_update(){ 
  let form = document.getElementById('new_operation_form'); //убираем форму добавления операции, если была открыта
  form.innerHTML = "";
  let form_1 = document.getElementById('new_entity_form'); //убираем форму добавления сущности, если была открыта
  form_1.innerHTML = "";
  let sect = document.getElementById('section').value; 
  if (sect == ""){
    sections_list_update()
    return
  }
  let url = new URL("/SPR/equipment_service_page/", window.location.origin);
  url.searchParams.set('section', String(sect));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      let node_list_div = document.getElementById('node_filters');
      node_list_div.innerHTML = "Узел: " + this.responseText;
      download_equipment_tree()
    }
  };
  delete(XHR);      
}

function download_new_operation_form(){ 
  let url = new URL("/SPR/equipment_service_page/", window.location.origin);
  url.searchParams.set('new_operation', String(1));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      let form = document.getElementById('new_operation_form');
      form.innerHTML = this.responseText;
    }
  };
  delete(XHR);      
}

function download_new_entity_form(col_name, new_str_name){ 
  let url = new URL("/SPR/equipment_service_page/", window.location.origin);
  url.searchParams.set('new_entity', String(1));   
  url.searchParams.set('col_name', String(col_name));  
  url.searchParams.set('new_str_name', String(new_str_name));   
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      let form = document.getElementById('new_entity_form');
      form.innerHTML = this.responseText;
    }
  };
  delete(XHR);      
}

function last_operations_list_update(){
  //в equipment_operations_table.js node_form вызывает эту функцию. Обёртка, чтобы это работало и здесь
  download_equipment_tree()
}

function download_equipment_tree(){ 
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
  request_str = "/SPR/update_equipment_tree/"+String(loc)+"/"+String(eqp)+"/"+String(sect)+"/"+String(node)+"/";    
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

function update_repair_operation_data(work_id, field, new_data){ 

  var XHR = new XMLHttpRequest()
  if (new_data=="" && field=="tools"){new_data='None'}
  request_str = "/SPR/repair_operations_editor/"+work_id+"/"+field+"/"+new_data+"/";
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
}

function save_new_work_to_bd(){
  let node = document.getElementById('node').value; 
  let op_content = document.getElementById('op_content').value; 
  if (op_content.trim() == ""){
    alert("Заполните содержание работы!")
    return
  }
  let op_tool = document.getElementById('op_tool').value; 
  let staff_position = document.getElementById('staff_position').value; 
  if (staff_position.trim() == ""){
    alert("Выберите должность исполнителя!")
    return
  }
  let op_per = document.getElementById('op_per').value; 
  if (op_per.trim() == ""){
    alert("Задайте периодичность!")
    return
  }
  let risk = document.getElementById('risk').value; 
  if (risk.trim() == ""){
    alert("Укажите степень риска при невыполнении операции!")
    return
  }
  
  let url = new URL("/SPR/add_new_repair_operation_to_bd/", window.location.origin);
  url.searchParams.set('node', String(node));  
  url.searchParams.set('op_content', String(op_content));    
  url.searchParams.set('op_tool', String(op_tool));   
  url.searchParams.set('staff_position', String(staff_position));   
  url.searchParams.set('op_per', String(op_per)); 
  url.searchParams.set('risk', String(risk));    
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      download_equipment_tree();
    }
  };
  delete(XHR);      
}

function save_new_entity_to_bd(col_name){
  let parent = ""
  if (col_name == 'eqp'){
    parent = document.getElementById('location').value; 
    upd_f = equipment_list_update
  }
  else if (col_name == 'sect'){
    parent = document.getElementById('equipment').value; 
    upd_f = sections_list_update
  }
  else if (col_name == 'node'){
    parent = document.getElementById('section').value;
    upd_f = nodes_list_update
  }
  let entity_name = document.getElementById('new_'+col_name).value; 
  if (entity_name.trim() == ""){
    alert("Введите название участка!")
    return
  }
  
  let url = new URL("/SPR/add_new_entity_to_bd/", window.location.origin);
  url.searchParams.set('col_name', String(col_name));  
  url.searchParams.set('entity_name', String(entity_name));       
  url.searchParams.set('parent_id', String(parent));  
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      download_equipment_tree();
      upd_f();
      let form = document.getElementById('new_entity_form');
      form.innerHTML = "";
    }
  };
  delete(XHR);      
}

function delete_work_from_db(op_id){
  let del = false
  del = confirm("Вы действительно хотите удалить операцию №"+String(op_id)+"?");
  if (del == false){
    return
  }
  let url = new URL("/SPR/delete_repair_operation_from_bd/"+String(op_id)+"/", window.location.origin);
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      download_equipment_tree();
    }
  };
  delete(XHR); 
}

function delete_entity_from_db(entity_type, entity_type_str, ent_id){
  let del = false
  del = confirm("Вы действительно хотите удалить "+entity_type_str+" №"+String(ent_id)+"?");
  if (del == false){
    return
  }
  let url = new URL("/SPR/delete_entity_from_db/"+String(entity_type)+"/"+String(ent_id)+"/", window.location.origin);
  var XHR = new XMLHttpRequest()
  XHR.open('GET', url, true);
  XHR.send();

  XHR.onreadystatechange = function() { 
    if(this.readyState == 4){
      if (this.responseText!='deleted_sucsessfuly'){
       alert(this.responseText)
      }
      download_equipment_tree();
    }
  }
  delete(XHR); 
}

//Build Tabulator
function RenderLog(TableData){
  let table_data = []
  let table_mode = 0
  var per_dateEditor = function(cell, onRendered, success, cancel){
    //cell - the cell component for the editable cell
    //onRendered - function to call when the editor has been rendered
    //success - function to call to pass thesuccessfully updated value to Tabulator
    //cancel - function to call to abort the edit and return to a normal cell

    //create and style input
    var cellValue = cell.getValue()
    var row_id = cell.getRow().getCells()[1].getValue() //получаем id операции
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
            success(input.value);
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

  var week_formatter = function(cell, formatterParams){
    //cell - the cell component
    //formatterParams - parameters set for the column
    val = cell.getValue()
    if(val =="yellow" || val=="white" || val=="green"){
      cell.getElement().style.background = val
      return
    } else {
      return val; //return the contents of the cell;
    }
  };

  function weeks_editor(cell){
    if(cell.getValue()=="white"){
      cell.setValue("yellow");
    } else {
      cell.setValue("white");
    }
  }

  let week_cols = Array();
  for(let i=0; i<52; i++){
    week_cols.push({title:"_"+(i+1).toString(), field:"_"+(i+1).toString(), width:5, formatter:"color",
                    cellClick:function(e, cell){
                      //e - the click event object
                      //cell - cell component
                      weeks_editor(cell);
                    },
                    headerSort:false})
  }

  function add_entity_to_bd(col_name, btn_name, new_str_name){
    btn_div = document.getElementById('add_entity_to_bd')
    btn_div.innerHTML ='<btn id="add_entity_btn">'+btn_name+'</btn>'
    btn = document.getElementById('add_entity_btn')
    btn.addEventListener("click", function(){
      if (col_name == 'loc' || col_name == 'eqp' || col_name == 'sect' || col_name == 'node'){
        download_new_entity_form(col_name, new_str_name)
      }
      if (col_name == 'work'){
        download_new_operation_form()
      }  
    });
  }

  if (TableData[0].loc_name != undefined){
    table_mode = 'loc_table'
    for (let i = 0; i < TableData.length; i++){   
      let row = {loc: TableData[i].loc_name, id: TableData[i].id}   
      table_data.push(row)
    }
    var table = new Tabulator("#equipment-tree-table", {
      layout:window.innerWidth > 800 ? "fitColumns" : "fitData",
      placeholder:"Нет данных",
      data: table_data,
      columns: [{title:"", field:"delete", formatter:"tickCross", cellClick:function(e, cell){
                                                                  var ent_id = cell.getRow().getCells()[1].getValue() //получаем id 
                                                                  delete_entity_from_db('loc', "участок", ent_id)},},
                {title:"Id", field:"id", hozAlign:"center", width:50, formatter:"textarea"},
                {title:"Участки", field:"loc", hozAlign:"center", width:180, formatter:"textarea"}]
    });
    add_entity_to_bd('loc', "Добавить участок", "Новый участок")
  }
  else if (TableData[0].eqp_name != undefined){
    table_mode = 'eqp_table' 
    for (let i = 0; i < TableData.length; i++){   
      let row = {eqp : TableData[i].eqp_name, id: TableData[i].id}   
      table_data.push(row)
    }
    var table = new Tabulator("#equipment-tree-table", {
      layout:window.innerWidth > 800 ? "fitColumns" : "fitData",
      placeholder:"Нет данных",
      data: table_data,
      columns: [{title:"", field:"delete", formatter:"tickCross", cellClick:function(e, cell){
                                                                  var ent_id = cell.getRow().getCells()[1].getValue() //получаем id 
                                                                  delete_entity_from_db('eqp', "оборудование", ent_id)},},
                {title:"Id", field:"id", hozAlign:"center", width:50, formatter:"textarea"},
                {title:"Оборудование", field:"eqp", hozAlign:"center", width:180, formatter:"textarea"},]
    });
    add_entity_to_bd('eqp', "Добавить оборудование", "Новое оборудование")
  }
  else if (TableData[0].sect_name != undefined){
    table_mode = 'sect_table'
    for (let i = 0; i < TableData.length; i++){   
      let row = {sect : TableData[i].sect_name,  id: TableData[i].id}   
      table_data.push(row)
    }
    var table = new Tabulator("#equipment-tree-table", {
      layout:window.innerWidth > 800 ? "fitColumns" : "fitData",
      placeholder:"Нет данных",
      data: table_data,
      columns: [{title:"", field:"delete", formatter:"tickCross", cellClick:function(e, cell){
                                                                  var ent_id = cell.getRow().getCells()[1].getValue() //получаем id 
                                                                  delete_entity_from_db('sect', "раздел", ent_id)},},
                {title:"Id", field:"id", hozAlign:"center", width:50, formatter:"textarea"},
                {title:"Разделы", field:"sect", hozAlign:"center", width:180, formatter:"textarea"},]
    });
    add_entity_to_bd('sect', "Добавить раздел", "Новый раздел")
  }
  else if (TableData[0].node_name != undefined){
    table_mode = 'node_table'
    for (let i = 0; i < TableData.length; i++){   
      let row = {node : TableData[i].node_name,  id: TableData[i].id}    
      table_data.push(row)
    }
    var table = new Tabulator("#equipment-tree-table", {
      layout:window.innerWidth > 800 ? "fitColumns" : "fitData",
      placeholder:"Нет данных",
      data: table_data,
      columns: [{title:"", field:"delete", formatter:"tickCross", cellClick:function(e, cell){
                                                                  var ent_id = cell.getRow().getCells()[1].getValue() //получаем id 
                                                                  delete_entity_from_db('node', "узел", ent_id)},},
                {title:"Id", field:"id", hozAlign:"center", width:50, formatter:"textarea"},
                {title:"Узлы", field:"node", hozAlign:"center", width:180, formatter:"textarea"},]
    });
    add_entity_to_bd('node', "Добавить узел", "Новый узел")
  }
  else if (TableData[0].work_content != undefined){
    table_mode = 'work_table'
    for (let i = 0; i < TableData.length; i++){   
      let row = { 
        id : TableData[i].id,
        work : TableData[i].work_content,
        tools : TableData[i].tools,
        staff_pos : TableData[i].staff_pos,
        periodicity : TableData[i].per_days,
        risk : TableData[i].risk,
      } 
      let week_cols_plan={}
      for(let j=1; j<53; j++){
        week="_"+j.toString()
        week_cols_plan[week]=TableData[i][week]
      } 
      row=Object.assign({}, row, week_cols_plan);  
      table_data.push(row)
    }
    let week_cols_plan = Array();
    for(let i=0; i<52; i++){
      week_cols_plan.push({title:"_"+(i+1).toString(), field:"_"+(i+1).toString(), width:5, formatter:week_formatter,
                      cellClick:function(e, cell){
                        //e - the click event object
                        //cell - cell component
                        weeks_editor(cell);
                    },
                    headerSort:false})
    }
    var table = new Tabulator("#equipment-tree-table", {
      layout:"fitColumns",
      placeholder:"Нет данных",
      data: table_data,
      columns: [{title:"", field:"delete", formatter:"tickCross", cellClick:function(e, cell){
                                                                     var op_id = cell.getRow().getCells()[1].getValue() //получаем id операции
                                                                     delete_work_from_db(op_id)
                                                                  },},
                {title:"Id", field:"id", hozAlign:"center", width:30, formatter:"textarea"},
                {title:"Операция", field:"work", hozAlign:"center", width:500, formatter:"textarea", editor:per_dateEditor},
                {title:"Инструмент", field:"tools", hozAlign:"center", width:180, formatter:"textarea", editor:per_dateEditor},
                {title:"Исполнитель", field:"staff_pos", hozAlign:"center", width:180, formatter:"textarea"},
                {title:"Периодичность(дн.)", field:"periodicity", hozAlign:"center", width:180, formatter:"textarea", editor:per_dateEditor},   
                {title:"Риск", field:"risk", hozAlign:"center", width:180, formatter:"textarea", editor:per_dateEditor},             
               ].concat(week_cols_plan),
    });
    table.on("cellEdited", function(cell){
      //cell - cell component
      col_name = cell.getColumn().getField()
      var row_id = cell.getRow().getCells()[1].getValue() //получаем id операции
      update_repair_operation_data(row_id, col_name, cell.getValue());
      let fill_with_per = false; 
      if (col_name[0] == '_'){ //один из недельных столбцов
        let cells = cell.getRow().getCells();
        let week_firs_indх=0;
        for(let i=0; i < cells.length; i++){
          if(cells[i].getColumn().getField()[0] == '_'){//индех первой ячейки с неделями
            week_firs_indх = i
            break;
          }
        } 
        for(let i=week_firs_indх; i < cells.length; i++){ //проверяем все недельные ячейки, кроме текущей. Если все они пустые - предлагаем заполнить
          if (cells[i].getValue() == "yellow" && cells[i] != cell){
            break;
          }
          if (i == cells.length-1){
            fill_with_per = confirm('Заполнить в соответствие с периодичностью?'); 
          }
        }
        
      };
      if (fill_with_per){
        week = col_name.slice(1) //номер недели
        let cells = cell.getRow().getCells();
        for(let i=0; i < cells.length; i++){
          if (cells[i].getColumn().getField() == "periodicity"){
            per = cells[i].getValue()
          }
          if (cells[i] == cell){ //текущая ячейка
            cur_cell_indx = i;
            break;
          }
        }
        h = Math.floor(per/7)
        for (let i=cur_cell_indx+h; i < cells.length; i=i+h){
          cells[i].setValue("yellow");
          col_name = cell.getColumn().getField()
          sleep(70)
        }
      }
    });
    add_entity_to_bd('work', "Добавить операцию", "Новая операция")
  }

  return table
} //RenderTable

//table = last_operations_list_update()
