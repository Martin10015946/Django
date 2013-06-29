// document ready
$(function(){

    var home_on_server = $('.home_on_server').text();

    var pr_bricklane = $('.pr_bricklane').attr('href');
    var pr_garage = $('.pr_garage').attr('href');

    // test !!! remove !!!!!
    var pr_br = 'http://127.0.0.1:8000/progress_report/2013/25/bricklane/'
    var pr_gr = 'http://127.0.0.1:8000/progress_report/2013/24/garage/'
    // end test !!! remove !!!!!

    // Ajaxq is a JQuery plugin that anable to call multiple ajax call and be sure that them will
    // be executed in the same order
    jQuery.ajaxq('queue',{
        type: "GET",
        url: pr_br,
        cache: false,
        success: function(data){
            var rollover_value = $(data).find('.rollover_value').text();
            rollover_value = rollover_value.split(" ");
            rollover_value = rollover_value.pop();

            var col = $('.roll_br');
            col.empty();
            col.text(rollover_value);

        },
        error: function(data){
            var col = $('.roll_br');
            col.empty();
            col.css('color','red');
            col.text("Error! Speak to Nello");
        }
     })

    jQuery.ajaxq('queue',{
        type: "GET",
        url: pr_gr,
        cache: false,
        success: function(data){
            var rollover_value = $(data).find('.rollover_value').text();
            rollover_value = rollover_value.split(" ");
            rollover_value = rollover_value.pop();

            var col = $('.roll_gr');
            col.empty();
            col.text(rollover_value);
        },
        error: function(data){
            var col = $('.roll_br');
            col.empty();
            col.css('color','red');
            col.text("Error! Speak to Nello");
        }
     })

    var url = home_on_server + "/landpage_line_ups";

    jQuery.ajaxq('queue',{
        type: "GET",
        url: url,
        cache: false,
        success: function(data){
            $('.time_today').empty().text(data.time_today);
            $('.time_day_after').empty().text(data.time_day_after);
            $('.time_tomorrow').empty().text(data.time_tomorrow);
            $('.rollover_plan_total').empty().text(data.rollover_plan_total);
        },
        error: function(data){
            var col = $('.time_today');
            col.empty();
            col.css('color','red');
            col.text("Error! Speak to Nello");
            // ---------------------
            var col = $('.time_day_after');
            col.empty();
            col.css('color','red');
            col.text("Error! Speak to Nello");
            // ---------------------
            var col = $('.time_tomorrow');
            col.empty();
            col.css('color','red');
            col.text("Error! Speak to Nello");
            // ---------------------
            var col = $('.rollover_plan_total');
            col.empty();
            col.css('color','red');
            col.text("Error! Speak to Nello");
        }
     })

}) // end of document ready

