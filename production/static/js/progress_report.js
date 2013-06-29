function setRollover (name){
    // do an ajax call to get the rollover of the day 
    // and refresh the date in the tag
	if(name=='assembled'){
		
		var shop = $('.shop_tag').text();
		var home_on_server = $('.home_on_server').text();
		url = home_on_server + '/progress_report/rollovers/' + shop;
		
		// Ajaxq is a JQuery plugin that anable to call multiple ajax call and be sure that them will
		// be executed in the same order 		
		jQuery.ajaxq('queue',{
		  type: "GET",
		  url: url,
		  cache: false,
		  success: function(rollover){ $('.rollover_value').html('To catch up &nbsp; ' + rollover)},
		  error: dbError
		});	
	}
}

function preventReturnKey(event) {
    if(event.keyCode == 13){
        event.preventDefault(event);
        event.stopPropagation(event);
    };
}

function dbError() {
    alert('Cannot record to DB speak to Nello.');
}


// document ready
$(function(){

   // initialize tooltips
   $('th').tooltip({container: 'span.manual'});

   // remove the div created by boostrap for show the tooltip,
   // so no anymore problems on the print of the page
   $('thead').mouseleave(function(){$('.tooltip.fade').remove();})

   // TODO we need to a more specific selector here
   $('a').tooltip();

   $('.mergeable').click(function(event){
        event.preventDefault(event);
        event.stopPropagation(event);
        var link = $(this).attr('href');
        $('.order_frame').attr('src', link);
        $('#myModal2').modal('show');
   })

   $('.add_note').click(function(event){

        event.preventDefault(event);
        event.stopPropagation(event);

        var description = $(this).parent().parent().parent().parent().children('a').children('span').text();
        var order = $(this).parent().parent().parent().parent().parent().attr('class');
        LINK = $(this).parent().parent().parent().parent().children('a');

        // if there is allready a note/tooltip I grab it and I show it in the form
    	var tooltip = LINK.attr('data-original-title');
        $('#production_note').val(tooltip);
        $('#form_note_description').text(description);
        $('#note_ac_od_id').attr('value', order);
        $('#myModal4').modal('show');
   })

   $('img.ratsign').each(function(){
 		if ($(this).attr('rat') == 'yes') { $(this).show(); }
        $(this).popover({'trigger':'hover','container': 'tr'});
   })

    $("a#boardvision").click(function(event) { 
        event.preventDefault(event); 
        event.stopPropagation(event); 
        window.open(this.href, 'otherWindow','width=1200,height=750,scrollbars=1'); 
    });


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

        jQuery.ajax({type: "POST", data: data, url: url, error: dbError});
    });
   

   // ajax call  on submit Rat form: insert a record in the rat table
   $('.btn_rat').click(function(event){

		event.preventDefault(event); // prevent the click default 	
        var options = { 
            success: function(data) {

                var reasons = $('.reasons').find(":selected").text();
                RAT_IMAGE.attr('data-content', reasons);

                $(RAT_IMAGE).show();
                $(TICK_IMAGE).popover({'trigger':'hover','container': 'tr', 'content': reasons});

                $('#myModal').modal('hide');
                $('.radio_rat').prop('checked', false);
                $('.rat_comment').val('');

                // untick the box, becouse there is a Rat
                TICK_IMAGE.attr('src', 'http://169.254.184.4/img/check.gif');
                TICK_IMAGE.attr('record', '0');

                $('.assembly_buffer').html('Ready for Assembly &nbsp; ' + data)

            }  // post-submit callback

           ,error: function(){
                dbError();
                $('#myModal').modal('hide');
           }  // post-submit callback

           ,type: 'post'  // post-submit callback
        };
        
        $('.rat_form').ajaxSubmit(options);
   })

   // on click "ok" in the plan form
   $('#plan_ok').click(function(event){

        event.preventDefault(event); // prevent the click default

        var plan = $('#plan_plan').val();
        if (plan != ""){
            var plan = parseInt(plan);
            if(isNaN(plan)){
                alert('Insert a number!');
            } else {
                var options = {
                    complete: function(jqXHR){
                        if (jqXHR.status == 200){
                            $('#plan_ac_od_id').val('');
                            $('#plan_plan').val('');
                            $('#myModal3').modal('hide');
                            TD_PLAN.text(plan);
                            location.reload();
                        } else {
                            dbError();
                        }
                    }  // post-submit callback
                    ,dataType: 'jsonp'  // cross domain ajax call
                };
                // ajax call
                $('.plan_form').ajaxSubmit(options);
            }
        }
   })

   // on click "ok" in the note form
   $('#note_ok').click(function(event){

        event.preventDefault(event); // prevent the click default

        var note = $('#production_note').val();

        var options = {
            success: function(){
                LINK.attr('data-original-title', note);
                $('#myModal4').modal('hide');
                $('#production_note').val('');
            }
           ,error: dbError
        };

        // ajax call
        $('.note_form').ajaxSubmit(options);
   })

   // close rat modal window
   $('.btn_rat_cancel').click(function(event){   	
		event.preventDefault(event); // prevent the click default
		$('#myModal').modal('hide');
		$('.radio_rat').prop('checked', false);        			
		$('.rat_comment').val(''); 
   })

   // close plan modal window
   $('#plan_cancel').click(function(event){
		event.preventDefault(event); // prevent the click default
        $('#plan_ac_od_id').val('');
        $('#plan_plan').val('');
		$('#myModal3').modal('hide');
   })

   // close plan modal window
   $('#note_cancel').click(function(event){
		event.preventDefault(event); // prevent the click default
        $('#production_note').val('');
		$('#myModal4').modal('hide');
   })

  // Ajax functionality, called when is clicked "prog" on the product detail
  // this ajax call are cross domain, so JQuery raise an expection even if the answer is 200 (OK)
  $('.add_programme').click(function (event){
  	
	event.preventDefault(event); // prevent the click default 

    // retrieving data to send to the server
    var programme = $(this).parent().parent().parent().parent().children('span.programme');
    var programme_status = programme.attr('value');
    var ac_od_id = $(this).attr('order');

    // building the url for the ajax call
    var access_api_url = $('.access_api_url').text();
    var url = access_api_url + 'order_detail/update_status/';

    if (programme_status == 'no') {

        programme.attr('value', 'yes');
        programme.css('color','grey');

		var data = {'id': ac_od_id, 'status': 'Prog'};

	    jQuery.ajax({
	      type: "POST",
	      url: url,
          data: data,
	      //success: function(status){alert('ok')},
     	  error: function (jqXHR, textStatus, errorThrown) {
     	  	//console.log(jqXHR.responseText);
	      	//var test = $.parseJSON(jqXHR.responseText);
		  	//var test2 = $.parseJSON(test.d);
		  	//console.log(test2[0].Name);
		  }
	    });    		
        
    } else {
    		
        programme.attr('value', 'no');
        programme.css('color','white');
        
		data = {'id': ac_od_id, 'status': 'NC Ready'};

	    jQuery.ajax({
	      type: "POST",
	      url: url,
	      data: data,
	      //success: function(status){},
     	  error: function (jqXHR, textStatus, errorThrown) {
     	    //console.log(jqXHR.responseText);
	      	//var test = $.parseJSON(jqXHR.responseText);
		  	//var test2 = $.parseJSON(test.d);
		  	//console.log(test2[0].Name);
		  }
	      //error: function (status) {alert('Could not record this in database, call Nello')}
	    });    		        
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
            }
        }

        data = {'record' : record, 'ac_od_id' : ac_od_id, 'name': name};
        data = JSON.stringify(data);

        // build the url for the ajax call
        var home_on_server = $('.home_on_server').text();
        url = home_on_server + "/progress_report/record";
        // Ajaxq is a JQuery plugin that anable to call multiple ajax call and be sure that them will
        // be executed in the same order
        jQuery.ajax({
          type: "POST",
          url: url,
          cache: false,
          data: data,
          success: function (data) {
              $('.assembly_buffer').html('Ready for Assembly &nbsp; ' + data[0])
          },
          error: dbError
        });

        setRollover($(this).attr('name'));
	})

   // if the status of the td.local_status is standby, set background color orange
   $('.status_assambled').each(function(){
       var status = $(this).attr('local_status');
       if(status == 'standby'){
          $(this).css('background-color','orange');       
       }
   })

    $('#rat a').click(function(event){

        $('.reasons').empty()
    	
		event.preventDefault(event); // prevent the click default

        var source = $(this).parent().parent().parent().parent().children('img:first').attr('name');
        var ac_od_id = $(this).parent().parent().parent().parent().parent().parent().attr('class');
	    // retrieve the description of the product and put it in the rat form
        var product = $(this).parent().parent().parent().parent().parent().parent().children('td.product').find('span.description').text();


    	RAT_IMAGE = $(this).parent().parent().parent().parent().children('.ratsign');
        TICK_IMAGE = $(this).parent().parent().parent().parent().children('img:first');

	    if (product == ""){
	    	var product = $(this).parent().parent().parent().parent().parent().parent().children('td.product').children('a').children('span.description').text();
	    }
	    $('.form_description').text(product);
	      
		$('.rat_ac_od_id').attr('value', ac_od_id);

		switch(source){
			case 'machined':
			  	source = 'machining';
			  break;
			case 'laminated':
			  	source = 'lamination';
			  break;
			case 'assembled':
			  	source = 'assembly';
			  break;
		}

        // append the rat list to the rat form
        var list = $('.' + source + '_' + 'reasons').clone();

        $('.reasons').append(list);

		$('.source').attr('value', source);
	    $('#myModal').modal('show');
	});

    $('#files a').click(function(){ var link = 'file://C:/'; });

    // on click on order pop up modal window with the order. Use Boostrap.js
    $('.order').click(function(event){
        event.preventDefault(); // prevent the click default

        order_detail = $(this).attr('href');
        $('.order_frame').attr('src', order_detail);
        $('#myModal2').modal('show');
    })

    // on click on order pop up modal window with the order. Use Boostrap.js
    $('#plan a').click(function(event){
        event.preventDefault(); // prevent the click default

        // declared global variable that will be handled by the event click on ok in the plan form to change its value
        TD_PLAN = $(this).parent().parent().parent().parent();

        var description = $(TD_PLAN).parent().children('.product').children('a').children('span').text();
        var ac_od_id = $(TD_PLAN).parent().attr('class');

        $('#form_plan_description').text(description)
        $('#plan_ac_od_id').val(ac_od_id)
        $('#myModal3').modal('show');
    })

    // the user update the board thickness field
    $('.thickness').change(function(){

        var thickness = $(this).val();
        var ac_od_id = $(this).parent().parent().attr('class');

        var thickness = parseFloat(thickness);
        // if the user put something witch is not a number, show an error
        if (isNaN(thickness)){
            alert('Input a number');
            $(this).val("");
        } else {
            var dict = {'ac_od_id': ac_od_id, 'thickness': thickness};
            var data = JSON.stringify(dict);
            var home_on_server = $('.home_on_server').text();
            url = home_on_server + "/progress_report/record_thickness";
            jQuery.ajax({ type: "POST", data: data, url: url, error: dbError });
        }
    })

}) // end of document ready
    
