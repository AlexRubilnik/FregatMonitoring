var marker_run = false;


function full_operations_list_update(){ 
  data_download_marker_on_off(false); //Показываем маркер "Подождите. Идёт загрузка данных..."
  marker_run=true; //Запускаем бегущий маркер
  charts_tables_on_off(true); //Убираем таблицы и графики
 
  var XHR = new XMLHttpRequest()
      request_str = "/SPR/full_operations_list_update/";
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

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function update_repair_operation_data(work_id, field, new_data){ 

  var XHR = new XMLHttpRequest()
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
      document.getElementById("full-operations-table-block").style['opacity'] = hidden_t
  } catch {}
}

//Build Tabulator
function RenderLog(TableData){

  let table_data = []
  for (let i = 0; i < TableData.length; i++){   
      let row = {   
        id : TableData[i].id,
        loc : TableData[i].loc,
        eqp : TableData[i].eqp,
        sect : TableData[i].sect,
        node : TableData[i].node,
        staff_pos : TableData[i].staff_pos,
        per : TableData[i].per,
        tools : TableData[i].tools,
        risk : TableData[i].risk,
        work : TableData[i].work,
        last : TableData[i].last,
        next : TableData[i].next,
      }   
      let week_cols={}
      for(let j=1; j<53; j++){
        week="_"+j.toString()
        week_cols[week]=TableData[i][week]
      } 
      row=Object.assign({}, row, week_cols);
      table_data.push(row)

  }

    //Create Date Editor
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
  
  var table = new Tabulator("#full-operations-table", {
  placeholder:"Нет данных",
  data: table_data,
  title:"Перечень оборудования",
  layout:"fitColumns",
  groupBy:["loc", "eqp", "sect"],
  groupStartOpen:true,
  groupToggleElement:"header",
          columns: [
            {title:"ID", field:"id", hozAlign:"center", width:20, formatter:"textarea"},
            {title:"Участок", field:"loc", hozAlign:"center", width:180, formatter:"textarea"},
            {title:"Оборудование", field:"eqp", hozAlign:"right", sorter:"number", width:100, formatter:"textarea"},
            {title:"Раздел", field:"sect", hozAlign:"center", width:180, formatter:"textarea"},
            {title:"Узел", field:"node", hozAlign:"center", width:140, formatter:"textarea"},
            {title:"Исполнитель", field:"staff_pos", hozAlign:"center", width:140, formatter:"textarea"},
            {title:"Периодичность(дн.)", field:"per", hozAlign:"center", width:140, formatter:"textarea", editor:per_dateEditor},
            {title:"Риски при невыполнении", field:"risk", hozAlign:"center", width:140, formatter:"textarea", editor:per_dateEditor},
            {title:"Инструмент", field:"tools", hozAlign:"center", width:140, formatter:"textarea", editor:per_dateEditor},
            {title:"Работа", field:"work", hozAlign:"center", width:520, formatter:"textarea", editor:per_dateEditor},
            {title:"Последнее обслуживание", field:"last", hozAlign:"center", width:120, editor:per_dateEditor, formatter:"date", formatterParams:{
              inputFormat:"yyyy-MM-dd",
              outputFormat:"yyyy-MM-dd",
              invalidPlaceholder:"(invalid date)",
              timezone:"Russia/Moscow",
              }},
            {title:"Следующее обслуживание", field:"next", hozAlign:"center", width:120, editor:per_dateEditor, formatter:"date", formatterParams:{
              inputFormat:"yyyy-MM-dd",
              outputFormat:"yyyy-MM-dd",
              invalidPlaceholder:"(invalid date)",
              timezone:"Russia/Moscow",
              }},
          ].concat(week_cols),

  });

  table.on("cellEdited", function(cell){
    //cell - cell component
    col_name = cell.getColumn().getField()
    var row_id = cell.getRow().getCells()[0].getValue() //получаем id операции
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
        if (cells[i].getColumn().getField() == "per"){
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
  return table
} //RenderTable

table = full_operations_list_update()