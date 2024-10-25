$.ajaxSetup({
  data: {
    csrfmiddlewaretoken: "{{ csrf_token }}",
  },
});
  
  function render_signals_graph(
    container,
    ticker1,
    ticker2,
    price1,
    price2,
    signals
  ) {
    // set the allowed units for data grouping
    groupingUnits = [
      [
        "week", // unit name
        [1], // allowed multiples
      ],
      ["month", [1, 2, 3, 4, 6]],
    ];
  
    let plotLinesArray = [];
    if (signals["Entry_Exit"] && signals["Entry_Exit"].length > 0) {
      for (let i = 0; i < signals["Entry_Exit"].length; i++) {
        plotLinesArray.push({
          color: signals["Entry_Exit"][i].color, // 垂直線的顏色
          width: 1, // 垂直線的寬度
          value: signals["Entry_Exit"][i].date, // 垂直線的位置（日期）
          dashStyle: "Dash", // 線條樣式
          label: {
            text: signals["Entry_Exit"][i].label, // 標籤文字
            align: "center", // 標籤對齊方式
            y: -5, // 標籤位置（向上移動）
            rotation: 0,
            style: {
              fontSize: "10px",
            },
          },
        });
      }
    }
  
    var obj = {
      rangeSelector: {
        selected: 5,
      },
  
      title: {
        text: "Price & Signals",
      },
  
      xAxis: {
        gridLineWidth: 1, // 設定x軸網格線的寬度
        plotLines: plotLinesArray,
      },
  
      yAxis: [
        {
          labels: {
            align: "right",
            x: -6,
          },
          title: {
            text: "Price",
          },
          top: "0%",
          height: "100%",
          offset: 0,
          lineWidth: 1,
          resize: {
            enabled: true,
          },
        },
      ],
  
      tooltip: {
        split: true,
      },
  
      series: [
        {
          name: ticker1,
          data: price1,
          color: "black",
          lineWidth: 1,
          dataGrouping: {
            units: groupingUnits,
          },
        },
        {
          name: ticker2,
          data: price2,
          color: "black",
          lineWidth: 1,
          dataGrouping: {
            units: groupingUnits,
          },
        },
        {
          type: "scatter",
          data: signals["stock1_buy_point"], // 使用傳遞的數據
          name: "Long",
          marker: {
            symbol: "triangle",
            fillColor: "green",
            lineColor: "green",
            lineWidth: 2,
            name: "buy",
            enabled: true,
            radius: 6,
          },
          visibility: true,
        },
        {
          type: "scatter",
          data: signals["stock1_sell_point"], // 使用傳遞的數據
          name: "Short",
          marker: {
            symbol: "triangle-down",
            fillColor: "red",
            lineColor: "red",
            lineWidth: 2,
            name: "sell",
            enabled: true,
            radius: 6,
          },
          visibility: true,
        },
        {
          type: "scatter",
          data: signals["stock2_buy_point"], // 使用傳遞的數據
          name: "Long",
          marker: {
            symbol: "triangle",
            fillColor: "green",
            lineColor: "green",
            lineWidth: 2,
            name: "buy",
            enabled: true,
            radius: 6,
          },
          visibility: true,
        },
        {
          type: "scatter",
          data: signals["stock2_sell_point"], // 使用傳遞的數據
          name: "Short",
          marker: {
            symbol: "triangle-down",
            fillColor: "red",
            lineColor: "red",
            lineWidth: 2,
            name: "sell",
            enabled: true,
            radius: 6,
          },
          visibility: true,
        },
      ],
    };
  
    Highcharts.stockChart(container, obj);
  }
  
  function render_bands_graph(
    container,
    spread,
    middle_line,
    upper_line,
    lower_line,
    signals_sell,
    signals_buy
  ){
    // set the allowed units for data grouping
    groupingUnits = [
        [
            "week", // unit name
            [1], // allowed multiples
        ],
        ["month", [1, 2, 3, 4, 6]],
        ];
    
        var obj = {
            rangeSelector: {
              selected: 5,
            },
        
            title: {
              text: "Bollinger Bands & Signals",
            },
        
            xAxis: {
              gridLineWidth: 1, // 設定x軸網格線的寬度
            },
        
            yAxis: [
              {
                labels: {
                  align: "right",
                  x: -6,
                },
                title: {
                  text: "value",
                },
                top: "0%",
                height: "100%",
                offset: 0,
                lineWidth: 1,
                resize: {
                  enabled: true,
                },
              },
            ],
        
            tooltip: {
              split: true,
            },
        
            series: [
              {
                name: "upper_line",
                data: upper_line,
                color: "red",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
              },
              {
                name: "lower_line",
                data: lower_line,
                color: "red",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
              },
              {
                name: "middle_line",
                data: middle_line,
                color: "blue",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
              },
              {
                name: "spread",
                data: spread,
                color: "black",
                lineWidth: 1,
                dataGrouping: {
                  units: groupingUnits,
                },
              },

              {
                type: "scatter",
                data: signals_buy, // 使用傳遞的數據
                name: "Long",
                marker: {
                  symbol: "triangle",
                  fillColor: "green",
                  lineColor: "green",
                  lineWidth: 2,
                  name: "buy",
                  enabled: true,
                  radius: 6,
                },
                visibility: true,
              },
              {
                type: "scatter",
                data: signals_sell, // 使用傳遞的數據
                name: "Short",
                marker: {
                  symbol: "triangle-down",
                  fillColor: "red",
                  lineColor: "red",
                  lineWidth: 2,
                  name: "sell",
                  enabled: true,
                  radius: 6,
                },
                visibility: true,
              },
            ],
          };
        
          Highcharts.stockChart(container, obj);

  };
  
  function render_profit_loss_graph(
    container,
    daily_profits,
    total_values,
    entry_point,
    exit_point,
  ){
    // set the allowed units for data grouping
    groupingUnits = [
        [
            "week", // unit name
            [1], // allowed multiples
        ],
        ["month", [1, 2, 3, 4, 6]],
        ];
    
        var obj = {
            rangeSelector: {
                selected: 5,
            },
        
            title: {
                text: "Profits & loss",
            },
        
            xAxis: {
                gridLineWidth: 1, // 設定x軸網格線的寬度
            },
        
            yAxis: [
                {
                labels: {
                    align: "right",
                    x: -6,
                    formatter: function () {
                        return (this.value).toFixed(2) + '%'; // 將數值轉換為百分比格式
                    }
                },
                title: {
                    text: "percentage",
                },
                top: "0%",
                height: "100%",
                offset: 0,
                lineWidth: 1,
                resize: {
                    enabled: true,
                },
                },
            ],
        
            tooltip: {
                split: true,
            },
        
            series: [
                {
                name: "Daily Value",
                data: daily_profits,
                color: "blue",
                lineWidth: 1,
                dataGrouping: {
                    units: groupingUnits,
                },
                },
                {
                name: "Cash",
                data: total_values,
                color: "orange",
                lineWidth: 1,
                dataGrouping: {
                    units: groupingUnits,
                },
                },
                {
                type: "scatter",
                data: exit_point, // 使用傳遞的數據
                name: "Exit Point",
                marker: {
                    symbol: "circle",
                    fillColor: "green",
                    lineColor: "green",
                    name: "Exit Point",
                    enabled: true,
                    radius: 3,
                },
                visibility: true,
                },
                {
                type: "scatter",
                data: entry_point, // 使用傳遞的數據
                name: "Entry Point",
                marker: {
                    symbol: "circle",
                    fillColor: "brown",
                    lineColor: "brown",
                    name: "Entry Point",
                    enabled: true,
                    radius: 3,
                },
                visibility: true,
                },
            ],
            };
        
            Highcharts.stockChart(container, obj);
  };

  $(document).ready(function () {

    $('#distance_add_track').click(function(){

      // 拿取使用者選取的parames
      var stock1 = $(`#stock1-distance`).val();
      var stock2 = $("#stock2-distance").val();
      var start_date = $("#start_date-distance").val();
      var end_date = $("#end_date-distance").val();
      var window_sizes = $(`#window_size-distance`).val();
      var std = $("#std-distance").val();
  
      var track_params = new FormData();
      track_params.append("stock1", stock1);
      track_params.append("stock2", stock2);
      track_params.append("method", "distance");
      track_params.append("start_date", start_date);
      track_params.append("end_date", end_date);
      track_params.append("window_sizes", window_sizes);
      track_params.append("std", std);
  
      $.ajax({
          url: "/monitor/add_track/",
          type: "post",
          data : track_params,
          dataType : 'json',
          processData : false,
          contentType : false,
          success: function (res) {
              alert("Add track successful!!!!!!!!!!!")
          }
      });
    });

    $("#distance_submit").click(function () {
  
      // 拿取使用者選取的parames
      var stock1 = $(`#stock1-distance`).val();
      var stock2 = $("#stock2-distance").val();
      var start_date = $("#start_date-distance").val();
      var end_date = $("#end_date-distance").val();
      var window_sizes = $(`#window_size-distance`).val();
      var std = $("#std-distance").val();
  
      var data_config = new FormData();
      data_config.append("stock1", stock1);
      data_config.append("stock2", stock2);
      data_config.append("start_date", start_date);
      data_config.append("end_date", end_date);
      data_config.append("window_sizes", window_sizes);
      data_config.append("std", std);
  
      var date1 = new Date(start_date);
      var date2 = new Date(end_date);
      var today = new Date();
  
      var timeDifference = date2 - date1;
      var yearsDifference = timeDifference / (365 * 24 * 60 * 60 * 1000);
      if (date1 > date2) {
        alert("Error!!! Start date cannot be greater than end date");
        return;
      }
      if (yearsDifference < 1) {
        alert(
          "Error!!! The difference between start and end dates must be greater than 1 year"
        );
        return;
      }
      if (date2 > today || date1 > today) {
        alert("Error!!! The date entered cannot be greater than today");
        return;
      }
  
      $(`#distance_submit`).hide();
      $(`#distance_circle`).show();
      $(`#distance_add_track`).hide();
      $(".distance_result").css("display", "none");
  
      $.ajax({
        headers: { "X-CSRFToken": csrf_token },
        type: "POST",
        dataType: "json",
        url: "run_distance/",
        data: data_config,
        processData: false,
        contentType: false,
        success: function (response) {
          console.log(response);
  
          $(`#distance_submit`).show();
          $(`#distance_circle`).hide();
          $(`#distance_add_track`).show();
          $(".distance_result").css("display", "block");
   
          render_signals_graph(
            "signals_plot",
            response.stock1,
            response.stock2,
            response.data1_his["close"],
            response.data2_his["close"],
            response.plot_signals
          );

          render_bands_graph(
            "bollinger_bands_plot",
            response.spread,
            response.middle_line,
            response.upper_line,
            response.lower_line,
            response.bands_signals_sell,
            response.bands_signals_buy
          );

          render_profit_loss_graph(
            "profit_loss_plot",
            response.pl_daily_profits,
            response.pl_total_values,
            response.pl_entry_point,
            response.pl_exit_point,
          );

          $("#signals_table").DataTable({
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

          $("#exe_signals_table").DataTable({
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

        
        },
      });
    });
  });
  