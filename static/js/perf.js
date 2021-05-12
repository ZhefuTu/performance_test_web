function draw_line_pic(kind, node, cpu, mem, platform, count){
    $.ajax({
        type: "GET",
        url: "/datashow/perf_data",
        data: {node: node, kind: kind, cpu: cpu, mem: mem, platform: platform, count: count},
        dataType: "json",
        success: function(result){
            var ItemLine = function(){
                return {
                    name: '',
                    data: [],
                    type: 'line',
                    // 设置折线上圆点大小
                    symbolSize:5,
                    itemStyle:{
                        normal:{
                            // 拐点上显示数值
                            // label : {
                            //   show: true
                            // },
                            borderColor:'red',  // 拐点边框颜色
                            lineStyle:{                 
                                width:3,  // 设置线宽
                                type:'solid'  //'dotted'虚线 'solid'实线
                            }
                        }
                    }
                }
            };
            var seriesTotal = [];
            if (kind=="batch_query") {
                category_list = ['non_batch_wcc','non_batch_pgrank','batch_wcc','batch_pgrank'];
                y_name = 'time_cost';
                color_list = ['#17A589', '#A93226','#76D7C4','#D98880'];
            }else if (kind=="normal_load" && node=="single") {
                category_list = ['normal_load'];
                y_name = 'avg_speed';
                color_list = ['#00EE00'];
            }else if (kind=="normal_load" && node=="cluster") {
                category_list = ['normal_load_10g', 'normal_load_30g'];
                y_name = 'avg_speed';
                color_list = ['#00EE00', '#FF9F7F'];
            }else if (kind=="hub_load") {
                category_list = ['hub_load_1'];
                y_name = 'avg_speed';
                color_list = ['#00EE00'];
            };

            for (var i=0; i<category_list.length; i++) {
                var item_line = new ItemLine();
                item_line.name = category_list[i];
                if (kind=="normal_load" && node=="single") {
                    item_line.data = result.data[3];
                }else{
                    item_line.data = result.data[i];
                };
                seriesTotal.push(item_line);
            };

            var myTable = document.getElementById(kind+"_"+node+"_table");
            myTable.innerHTML = result.table_html;

            var myOptions = document.getElementById(kind+"_"+node+"_options");
            console.log(myOptions)
            myOptions.innerHTML = result.option_html;

            var myChart = echarts.init(document.getElementById(kind +"_"+node));
            var option = {
                backgroundColor: '#FFF0F5',

                title: {
                  // text: 'Batch Query',
                  // subtext: 'Batch Query',
                  // x: 'center'
                },
         
                legend: {
                  // orient 设置布局方式，默认水平布局，可选值：'horizontal'（水平） ¦ 'vertical'（垂直）
                  orient: 'horizontal',
                  // x 设置水平安放位置，默认全图居中，可选值：'center' ¦ 'left' ¦ 'right' ¦ {number}（x坐标，单位px）
                  x: 'left',
                  // y 设置垂直安放位置，默认全图顶端，可选值：'top' ¦ 'bottom' ¦ 'center' ¦ {number}（y坐标，单位px）
                  y: 'top',
                  // data: result.xa
                  // data: ['non_batch_wcc','non_batch_pgrank','batch_wcc','batch_pgrank']
                  data: category_list
                },
         
                //  图表距边框的距离,可选值：'百分比'¦ {number}（单位px）
                grid: {
                    top: '14%',   // 等价于 y: '16%'
                    left: '3%', 
                    right: '3%',
                    bottom: '3%',
                    containLabel: true
                },
         
                // 提示框
                tooltip: {
                    trigger: 'axis',
                    textStyle: {
                        align: 'left'
                    },
                    formatter(params){
                        // console.log(params);
                        var relVal = "";
                        relVal += 'ver: <font color="yellow">'+params[0].axisValue+'</font><br>';
                        relVal += 'tag: '+params[0].data.date+'<br>';
                        if (kind=="batch_query") {
                            for (var i = 0; i < params.length; i++){
                                relVal += params[i].seriesName + ': <font color="#00EE00">' + params[i].value + '</font> s<br>';
                            }
                        }else if(kind=="normal_load" && node=="single") {
                            relVal += params[0].seriesName + ': <font color="#00EE00">' + params[0].value + '</font> l/s';
                        }else if(kind=="normal_load" && node=="cluster") {
                            for (var i = 0; i < params.length; i++){
                                relVal += params[i].seriesName + ': <font color="#00EE00">' + params[i].value + '</font> l/s<br>';
                            }
                        }else if (kind="hub_load") {
                            // for (var i = 0; i < params.length; i++){
                            //     relVal += params[i].seriesName + ': <font color="#00EE00">' + params[i].value + '</font> kl/s<br>';
                            // }
                            relVal += params[0].seriesName + ': <font color="#00EE00">' + params[0].value + '</font> kl/s';
                        }
                        return relVal
                    }
                },
         
                //工具框，可以选择
                toolbox: {
                    feature: {
                        saveAsImage: {} //下载工具
                    }
                },
         
                xAxis: {
                    name: 'version',
                    type: 'category',
                    axisLine: {
                        lineStyle: {
                            // 设置x轴颜色
                            color: '#912CEE'
                        }
                    },
                    // 设置X轴数据旋转倾斜
                    axisLabel: {
                        rotate: 60, // 旋转角度
                        interval: 0  //设置X轴数据间隔几个显示一个，为0表示都显示
                    },
                    // boundaryGap值为false的时候，折线第一个点在y轴上
                    boundaryGap: false,
                    data: result.ya
                },
         
                yAxis: {
                    name: y_name,
                    type: 'value',
                    // min:0, // 设置y轴刻度的最小值
                    // max:result.max_time,  // 设置y轴刻度的最大值
                    splitNumber:9,  // 设置y轴刻度间隔个数
                    axisLine: {
                        lineStyle: {
                            // 设置y轴颜色
                            color: '#87CEFA'
                        }
                    }
                },
         
                series: seriesTotal,
                
                color: color_list
            };
            myChart.setOption(option);
        },
        error: function(str){
            alert("No data found!");
        }
    });
}
