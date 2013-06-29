$(function(){

   $('.add_note').click(function(event){

        event.preventDefault(event);
        event.stopPropagation(event);

        var description = $(this).parent().parent().parent().parent().children('.description').text();
        SPAN = $(this).parent().parent().parent().parent().children('.description');
        var order = $(this).parent().parent().parent().parent().parent().attr('class');

        // if there is allready a note/tooltip I grab it and I show it in the form
    	var tooltip = SPAN.attr('data-original-title');
        console.log(SPAN);
        console.log(tooltip);

        $('#production_note').val(tooltip);
        $('#form_note_description').text(description);
        $('#note_ac_od_id').attr('value', order);
        $('#myModal4').modal('show');
   })

   // on click "ok" at the plan form
   $('#note_ok').click(function(event){

        event.preventDefault(event); // prevent the click default

        var note = $('#production_note').val();

        var options = {
            success: function(){
                SPAN.attr('data-original-title', note);
                $('#myModal4').modal('hide');
                $('#production_note').val('');
            }
           ,error: function(){
                alert('Could not record in database, speak to Nello');
            }
        };

        // ajax call
        $('.note_form').ajaxSubmit(options);
   })

   // close plan modal window
   $('#note_cancel').click(function(event){
		event.preventDefault(event); // prevent the click default
        $('#production_note').val('');
		$('#myModal4').modal('hide');
   })

   // prevent the return key stroke on this input field
   $('#production_note').keydown(function(event){
       if(event.keyCode == 13){
            event.preventDefault(event);
            event.stopPropagation(event);
       };
   })


    // tick or untick file preparation
    $('a.fileprep').click(function(event) {

        event.preventDefault(event);

        var ac_od_id = ($(this).attr('id'));
        var fileprep = ($(this).attr('fileprep'));
        var cell = $(this).closest('td');

        if (fileprep == 0){
            fileprep = 1;
            $(this).attr('fileprep',fileprep);
            $(cell).css('background-color','rgb(125,125,125)');
        } else if(fileprep == 1) {
            fileprep = 2;
            $(this).attr('fileprep',fileprep);
            $(cell).css('background-color','rgb(200,200,200)');
        } else {
            fileprep = 0;
            $(this).attr('fileprep',fileprep);
            $(cell).css('background-color','rgb(250,250,250)');
        }

        var data = {'ac_od_id': ac_od_id, 'fileprep':fileprep};

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        var url = home_on_server + "/progress_report/record_fileprep";

        jQuery.ajax({
            type: "POST",
            data: data,
            url: url,
            error: function () {alert('Cannot record to DB speak to Nello.');}
        });
    });


    // on click on order pop up modal window with the order. Use Boostrap.js
    $('.order').click(function(event){
        event.preventDefault(); // prevent the click default

        order_detail = $(this).attr('href');
        $('.order_frame').attr('src', order_detail);
        $('#myModal2').modal('show');
    })

    // enable tooltip
   $('.description').tooltip();

   // if the status of the td.local_status is standby, set background color orange
   $('.status_assambled').each(function(){
       var status = $(this).attr('local_status');
       if(status == 'standby'){
          $(this).css('background-color','orange');
       }
   })

    /**
     * If the check box of laminated, machined, assembled are click
     * is called an ajax call that update the state in the corresponding
     */
    $('img:not(.ratsign)').click(function(event){

        event.preventDefault(event); // prevent the click default

        var name = $(this).attr('name');
        var record = $(this).attr('record');
        var ac_od_id = $(this).closest('tr').attr('class');

        if(record == '1'){
            // the product will NOT be Assambled
            record = 0
            $(this).attr('src', 'http://169.254.184.4/img/check.gif');
            $(this).attr('record', '0');

            $(this).closest('td').prev().prev().children('a').attr('href', '#'); // breaks the link to timer
        } else {
            // the product will be Assambled
            record = 1
            $(this).attr('src', 'http://169.254.184.4/img/checked.gif');
            $(this).attr('record', '1');
            // when the user tick on assambled, disable the link to the timer putting '#' in the href attribute of the link
            var link = $(this).closest('td').prev().prev().children('a').attr('link');
            $(this).closest('td').prev().prev().children('a').attr('href', link);
        }

        var source = $(this).attr('name');
        if(source == 'laminated'){
            if(record == 0){
                var c = $(this).parent().next().find('input').attr('value','');
                var c = $(this).parent().parent().next().find('input').val('')
                console.log(c);
            }
        }

        data = {'record' : record, 'ac_od_id' : ac_od_id, 'name': name};
        data = JSON.stringify(data);

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        url = home_on_server + "/progress_report/record";
        // Ajaxq is a JQuery plugin that anable to call multiple ajax call and be sure that them will
        // be executed in the same order
        jQuery.ajaxq('queue',{
          type: "POST",
          url: url,
          cache: false,
          data: data,
          success: function (data) { $('.assembly_buffer').html('Ready for Assembly &nbsp; ' + data[0])},
          error: function (status) {alert('Could not record in database, speak to Nello')}
        });

        setRollover($(this).attr('name'));
	})


})