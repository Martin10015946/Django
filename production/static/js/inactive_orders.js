// document ready
$(function(){

    $('#not_in_access').click(function(event){

        event.preventDefault(event); // prevent the click default

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        var url = home_on_server + "/progress_report/inactive_orders/delete";

		// build the data to post
        var list = [];
        var order_details  = $('.not-found-in-access');
        $(order_details).each(function(){
            list.push($(this).text());
        });
        var data = JSON.stringify(list)

        // ajax call
	    jQuery.ajax({
            type: "POST"
           ,url: url
           ,data: data
           ,dataType: "json"
           ,success: function (data) {
                $(order_details).parent().remove();
            }
           ,error: function (status) {
               alert('Could not record in database, speak to Nello');
            }
        });

    })

    $('#no_planned').click(function(event){

        event.preventDefault(event); // prevent the click default

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        var url = home_on_server + "/progress_report/inactive_orders/delete";

		// build the data to post
        var list = [];
        var order_details  = $('.without-planned-date');
        $(order_details).each(function(){
            list.push($(this).text());
        });
        var data = JSON.stringify(list)

        // ajax call
	    jQuery.ajax({
            type: "POST"
           ,url: url
           ,data: data
           ,dataType: "json"
           ,success: function (data) {
                $(order_details).parent().remove();
            }
           ,error: function (status) {
               alert('Could not record in database, speak to Nello');
            }
        });

    })

    $('#blank_eta').click(function(event){

        event.preventDefault(event); // prevent the click default

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        var url = home_on_server + "/progress_report/inactive_orders/blank_future_eta";

	    jQuery.ajax({
            type: "GET"
           ,url: url
           ,success: function (data) {
                alert('Record Updated')
            }
           ,error: function (status) {
               alert('Could not record in database, speak to Nello');
            }
        });
    })

}) // end document ready