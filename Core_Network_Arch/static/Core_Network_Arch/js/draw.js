function draw_monthly(data,link_id,link_name,max){
    $('#container_'+link_id).highcharts({
        chart: {
            type: 'areaspline'
        },
        title: {
            text: link_name
        },

        xAxis: {
            categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
        },
        yAxis: {
            max: max*1000*1000,
            title: {
                text: 'Stream Speed (bits/s)'
            }
        },
        tooltip: {
            enabled: true,
            formatter: function() {
                return '<b>'+ this.series.name +'</b><br/>'+this.x +'号: '+ (this.y/1000000).toFixed(2) +'Mbps';
            }
        },
        plotOptions: {
            areaspline: {
                fillOpacity: 0.05
            }

        },
        series: data.sequence
    });
};