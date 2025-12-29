var marker_run = false;

function bottling_journal_update(){ 
  bottling_year = document.getElementById('bottling_year').value
  bottling_lot = document.getElementById('bottling_lot').value
  bottling_grade = document.getElementById('bottling_grade').value

  data_download_marker_on_off(false); //Показываем маркер "Подождите. Идёт загрузка данных..."
  marker_run=true; //Запускаем бегущий маркер
  charts_tables_on_off(true); //Убираем таблицы и графики
 
  var XHR = new XMLHttpRequest()
      request_str = "/FregatMonitoringApp/bottling_journal_data/";
      let q_flag = false;
      if (bottling_year != ""){
        request_str = request_str + '?bottling_year='+bottling_year
        q_flag = true;
      }
      if (bottling_lot != ""){
        if (q_flag) {
          request_str = request_str + '&bottling_lot='+bottling_lot
        } else {
          q_flag = true;
          request_str = request_str + '?bottling_lot='+bottling_lot
        }
      }
      if (bottling_grade != ""){
        if (q_flag) {
          request_str = request_str + '&bottling_grade='+bottling_grade;
        } else {
          q_flag = true;
          request_str = request_str + '?bottling_grade='+bottling_grade;
        }
      }
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
      table.setGroupStartOpen(false);      
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
      document.getElementById("bottling-journal-block").style['opacity'] = hidden_t
  } catch {}
}

//Build Tabulator
function RenderLog(TableData){

  let table_data = []
  for (let i = 0; i < TableData.length; i++){   
      let row = {   
        grade : TableData[i].grade,
        lot : TableData[i].lot,
        data : TableData[i].data,
        bundle : TableData[i].bundle,
        weight : TableData[i].weight,
      }       
      table_data.push(row)

  }

  var table = new Tabulator("#bottling-journal-table", {
  placeholder:"Нет данных",
  data: table_data,
  title:"Журнал розливов",
  layout:"fitColumns",
  groupBy:["grade", "lot"],
  groupHeader:function(value, count, data, group){
    //value - the value all members of this group share
    //count - the number of rows in this group
    //data - an array of all the row data objects in this group
    //group - the group component for the group
    let sum_weight = 0
    for (let i = 0; i < data.length; i++){
      sum_weight += Number(data[i].weight.substring(0,4))
    }
    return value + "<span style='color:#d00; margin-left:10px;'>(" + count + " пачек)</span> <span> Общий вес: "+ sum_weight +"кг";
  },
  groupStartOpen:true,
  groupToggleElement:"header",
          columns:[
              {title:"Марка сплава", field:"grade", hozAlign:"center", width:180},
              {title:"№ Розлива", field:"lot", hozAlign:"right", sorter:"number", width:100},
              {title:"Дата/Время", field:"data", hozAlign:"center", width:180, 
               formatter:"datetime",
               formatterParams:{
               inputFormat:"yyyy-MM-dd'T'HH:mm:ss.SSS'Z'",
               outputFormat:"dd-MM-yy HH:mm:ss",
               invalidPlaceholder:"(invalid date)",
               timezone:"W-SU",
              }},
              {title:"№ пакета", field:"bundle", hozAlign:"center", width:140},
              {title:"Вес", field:"weight", hozAlign:"center", width:130},
          ],
  });

  //trigger download of data.csv file
  document.getElementById("download-csv").addEventListener(
  'click', 
  function(){
      table.download("csv", "data.csv");
  }, 
  false);

  //trigger download of data.xlsx file
  document.getElementById("download-xlsx").addEventListener(
  'click', 
  function(){
      table.download("xlsx", "data.xlsx", {sheetName:"Розлив готовой продукции"});
  }, 
  false);

  return table
} //RenderTable