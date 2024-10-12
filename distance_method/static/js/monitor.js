function remove_from_track_list(track_row){

    var track_spread = new FormData;
    track_spread.append("stock1", track_row['stock1']);
    track_spread.append("stock2", track_row['stock2']);
    track_spread.append("start_date", track_row['start_date']);
    track_spread.append("end_date", track_row['end_date']);
    track_spread.append("method", track_row['method']);
    track_spread.append("window_size", track_row['window_size']);
    track_spread.append("n_times", track_row['n_times']);
    track_spread.append("stop_loss_percentage", track_row['stop_loss_percentage']);
    track_spread.append("max_recover_days", track_row['max_recover_days']);
    track_spread.append("consider_optimization", track_row['consider_optimization']);
    track_spread.append("critical_value", track_row['critical_value']);
    track_spread.append("consider_p_value", track_row['consider_p_value']);
    track_spread.append("track_date", track_row['track_date']);

    $.ajax({
      url: "/monitor/remove_track/",
      data:track_spread, 
      type:'POST',
      dataType: 'json',
      processData:false,
      contentType:false,
      success:function(data)
      {
        alert("Remove successfully!");
      }
    });
}

function run_monitor_analysis(track_row){
    var track_spread = new FormData;
    track_spread.append("stock1", track_row['stock1']);
    track_spread.append("stock2", track_row['stock2']);
    track_spread.append("start_date", track_row['start_date']);
    track_spread.append("end_date", track_row['end_date']);
    track_spread.append("method", track_row['method']);
    track_spread.append("window_size", track_row['window_size']);
    track_spread.append("n_times", track_row['n_times']);
    track_spread.append("stop_loss_percentage", track_row['stop_loss_percentage']);
    track_spread.append("max_recover_days", track_row['max_recover_days']);
    track_spread.append("consider_optimization", track_row['consider_optimization']);
    track_spread.append("critical_value", track_row['critical_value']);
    track_spread.append("consider_p_value", track_row['consider_p_value']);
    track_spread.append("track_date", track_row['track_date']);

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/monitor/run_tracker/",
        data: track_spread,
        processData: false,
        contentType: false,
        success: function (response) {
            $('#staticBackdrop').modal('show');
            
            var indexCell = $(`#target_button`);
            if (indexCell.length) {
                indexCell.html(`<button type="button" class="btn btn-success">Results</button>`);
                indexCell.removeAttr('id'); // 刪除 id
            } 

            render_signals_graph(
                "signals_plot-monitor",
                response.stock1,
                response.stock2,
                response.data1_his["close"],
                response.data2_his["close"],
                response.plot_signals
              );
    
            render_bands_graph(
                "bollinger_bands_plot-monitor",
                response.spread,
                response.middle_line,
                response.upper_line,
                response.lower_line,
                response.bands_signals_sell,
                response.bands_signals_buy
            );
    
            render_profit_loss_graph(
                "profit_loss_plot-monitor",
                response.pl_daily_profits,
                response.pl_total_values,
                response.pl_entry_point,
                response.pl_exit_point,
            );

            $("#signals_table-monitor").DataTable({
                autoWidth: false,
                bDestroy: true,
                searching: false,
                lengthMenu: [
                  [5, 10, 20, -1],
                  [5, 10, 20, "All"],
                ],
                data: response.table_signals,
                columns: [
                  { data: "date", title: "Date" },
                  { data: "type", title: "Type" },
                  { data: "stock1_action", title: `Action of ${response.stock1}` },
                  { data: "stock1_price", title: `Price of ${response.stock1}` },
                  { data: "stock2_action", title: `Action of ${response.stock2}` },
                  { data: "stock2_price", title: `Price of ${response.stock2}` },
                ],
                columnDefs: [
                  {
                    targets: [2, 3],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "white");
                    },
                  },
                  {
                    targets: [4, 5],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "whitesmoke");
                    },
                  },
                ],
                fnRowCallback: function (nRow, aData) {
                  if (aData["type"] == "Open") {
                    $(nRow).find("td:eq(0)").css("background-color", "paleturquoise");
                    $(nRow).find("td:eq(1)").css("background-color", "paleturquoise");
                  } else {
                    $(nRow).find("td:eq(0)").css("background-color", "MistyRose");
                    $(nRow).find("td:eq(1)").css("background-color", "MistyRose");
                  }
                },
            });
    
            $("#exe_signals_table-monitor").DataTable({
                autoWidth: false,
                bDestroy: true,
                searching: false,
                lengthMenu: [
                  [5, 10, 20, -1],
                  [5, 10, 20, "All"],
                ],
                data: response.exe_table_signals,
                columns: [
                  { data: "date", title: "Date" },
                  { data: "type", title: "Type" },
                  { data: "stock1_action", title: `Action of ${response.stock1}` },
                  { data: "stock1_price", title: `Price of ${response.stock1}` },
                  { data: "stock2_action", title: `Action of ${response.stock2}` },
                  { data: "stock2_price", title: `Price of ${response.stock2}` },
                  { data: "percentage", title: `Percentage of Profit|Loss (%)` },
                ],
                columnDefs: [
                  {
                    targets: [2, 3],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "white");
                    },
                  },
                  {
                    targets: [4, 5],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "whitesmoke");
                    },
                  },
                ],
                fnRowCallback: function (nRow, aData) {
                  if (aData["type"] == "Open") {
                    $(nRow).find("td:eq(0)").css("background-color", "paleturquoise");
                    $(nRow).find("td:eq(1)").css("background-color", "paleturquoise");
                  } else {
                    $(nRow).find("td:eq(0)").css("background-color", "MistyRose");
                    $(nRow).find("td:eq(1)").css("background-color", "MistyRose");
                  }
                },
            });
        }
      });
}

$(document).ready(function (){
  
    $.ajax({
        url: "/monitor/get_track_list/",
        type: "post",
        dataType : 'json',
        processData : false,
        contentType : false,
        success: function (res) {
            console.log(res)
            var table = $("#monitor").DataTable({
                data: res.track_data,
                "createdRow": function (row, data, dataIndex) {
                    // 將每個儲存格的文字置中
                    $(row).find('td').css({
                        'white-space': 'nowrap',  // 防止換行
                        'text-align': 'center'    // 置中
                    });
                },

                columns: [
                    { data: 'method' },
                    { data: 'stock1' },
                    { data: 'stock2' },
                    { data: 'start_date' },
                    { data: 'end_date' },
                    { data: 'window_size'},
                    { data: 'n_times' },
                    { data: 'track_date' },
                    {
                        className: 'dt-remove-tracking dt-center',  // 讓按鈕也置中
                        orderable: false,
                        data: null,
                        defaultContent: '<button type="button" class="btn btn-danger">Untrack</button>',
                    },
                    {
                        className: 'dt-run-analysis dt-center',  // 讓按鈕也置中
                        orderable: false,
                        data: null,
                        defaultContent: `<button type="button" class="btn btn-success">Results</button>`,
                    },
                ],
                order: [[1, 'asc']],  // 依 stock2 排序
            });
            
            
            $('#monitor tbody').on('click', 'td.dt-remove-tracking', function () {
                var row = table.row($(this).parents('tr'));
                var data = row.data();
                remove_from_track_list(data);                        
                row.remove().draw();
            });

            $('#monitor tbody').on('click', 'td.dt-run-analysis', function () {
                var row = table.row($(this).parents('tr'));
                var track_row = row.data();
                run_monitor_analysis(track_row);
                var indexCell = $(this).parents('tr').find('td').eq(9); // 獲取該行的第 9 個單元格
                indexCell.attr('id', 'target_button'); // 設置 id
                indexCell.html(`<div class="circle" id="distance_circle" align=center style="">
                                    <span class="spinner-border">
                                    </span><span class="load"></span> 
                                </div>`
                            );
            });
        }
    });
});


