$(function(){

    // initialize tooltips
    $('th').tooltip({container: 'span.manual'});

   // remove the div created by boostrap for show the tooltip,
   // so no anymore problems on the print of the page
   $('thead').mouseleave(function(){$('.tooltip.fade').remove();})

    // clean al the first break_line empty of every table
    $('table').each(function(){
        $(this).each(function(){
            var c = $(this).find('tr.break_line:eq(0)').css('display', 'none');
        });
    });

    // location code
    $('.location_menu').contextmenu();
    $('.location').click(function(event){

        event.preventDefault(); // prevent the click default
        console.log($(this).attr('location'));
        var location = $(this).attr('location');

        var ac_od_id = $(this).parent().parent().parent().parent().parent().attr('class');

        data = {'ac_od_id':ac_od_id, 'location':location};

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        var url = home_on_server + "/line_ups/record_location";
        var span = $(this).parent().parent().parent().parent().children('span');

        jQuery.ajax({
             type: "POST"
            ,data: data
            ,url: url
            ,error: function(){
                alert('cannot record the Location: speak to Nello');
            }
            ,success: function(){
                $(span).text(location)
            }
        }); // end Ajax call
    })

    // on click on order pop up modal window with the order. Use Boostrap.js
    $('.order').click(function(event){
        event.preventDefault(); // prevent the click default

        order_detail = $(this).attr('href');
        $('.order_frame').attr('src', order_detail);
        $('#myModal2').modal('show');
    });

    // date picker. Initialize date picker
    options = {'format':'dd-mm-yyyy'};
    $('.dp1').datepicker(options)
        .on('changeDate', function(ev){

            //console.log(ev.date.valueOf())
            // istance of Date object to cath the values of the new date
            var newDate = new Date(ev.date)
            var day = newDate.getDate();
            var month = newDate.getMonth()+1;
            var year = newDate.getFullYear();

            // istance of moment in order to manipulate the data
            d = moment(day + '-' + month + '-' + year, 'D-M-YYYY');

            var date = d.format('DD MMM YYYY');
            // change the link date
            $(this).text(date);

            var ac_o_id =  $(this).parent().next().next().text();
            var data = {'ac_o_id':ac_o_id, 'date': date}

            //console.log(ac_o_id);
            //console.log(date);
            //console.log(data);

            // build the url for the ajax call
            url = 'http://169.254.184.4/access_api/orders/update_required/'

            jQuery.ajax({
                type: "POST",
                data: data,
                url: url,
                error: function (){
                    //alert('cannot record the Location: speck to Nello');
                }
            }); // end Ajax call
        }); // end of data picker change event

}); // end document ready
