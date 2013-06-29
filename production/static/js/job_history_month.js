$(document).ready(function(){

    // date picker. Initialize date picker
    var options = {'format':'dd/mm/yyyy', "autoclose": true};
    $('.dp1').datepicker(options)
        .on('changeDate', function(ev){

            // istance of Date object to cath the values of the new date
            var newDate = new Date(ev.date);
            var day = newDate.getDate();
            var month = newDate.getMonth()+1;
            var year = newDate.getFullYear();

            var shop = $('.shop_tag').text();

            $('.datepicker').hide();

            var home_on_server = $('.home_on_server').text();
            var url = home_on_server + '/jobhistory/' + year + '/' + month + '/' + day + '/' + shop

            window.location.href = url

        }); // end of data picker change event

    var line1 = [];
    var counter = 1;
    $('.chart_column').each(function(){
        var el = []
        var x_description = $(this).next().text();
        el[0] = x_description;
        el[1] = parseInt($(this).text());
        line1.push(el);
        counter+=1;
    })

    var plot1 = $.jqplot('chart1', [line1], {
      title: 'Job History Chart',
      series:[{renderer:$.jqplot.BarRenderer}],
      // this is the plugin for
      axesDefaults: {
          tickRenderer: $.jqplot.CanvasAxisTickRenderer ,
          tickOptions: {
            angle: -60,
            fontSize: '9pt'
          }
      },
      axes: {
        xaxis: {
          renderer: $.jqplot.CategoryAxisRenderer
        }
      }
    });
});

