PRODUCT = NaN; // global variable to save the tr.product when is clicked

// modal dialog size
DIALOG_WIDTH = 900
DIALOG_HEIGHT = 500

day_start_hours = 09;
day_start_minutes = 00;
value_of_minutes = 60;

day_start_date = moment();
day_start_date.hours(day_start_hours);
day_start_date.minutes(day_start_minutes);

function draw_scale(paper) {
	paper.path("M10 30L730 30");
	var start_hour = 9;
  	for(var i = 10; i < 740; i+=60) {	
     if (i == 10) {  
        paper.path('M' + i.toString() + ' 30L' + i.toString() + ' 90');
     } else if (i == 250) {
        ii = i+30;
        paper.path('M' + i.toString() + ' 30L' + i.toString() + ' 40');
        paper.path('M' + ii.toString() + ' 30L' + ii.toString() + ' 90');
     } else if (i == 550) {
        paper.path('M' + i.toString() + ' 30L' + i.toString() + ' 90');
     } else {
			  paper.path('M' + i.toString() + ' 30L' + i.toString() + ' 40');
     }
			paper.text(i,20,start_hour.toString());
			start_hour += 1;
	}
}

function draw_block(id,f, start, end, paper, color) {
	var scale_start = moment(start);
	scale_start.hours(9);
	scale_start.minutes(0);
	var x = Math.abs(scale_start.diff(start, 'minutes'))+10;
	var width = Math.abs(start.diff(end, 'minutes'));
	var block = paper.rect(x,45,width,25).attr({'fill': color, 'stroke': color});
	var file_text = paper.text(x,100, f)
	file_text.hide()
	block.node.setAttribute('class','block');
	block.node.setAttribute('id',id);
	
	block.hover(function () {
	   block.attr({'stroke': 'black'});
	   file_text.show();
	},
	function () {
	   block.attr({'stroke': color});
	   file_text.hide();
	});
}

/*
 * delete the key points of the timer dialog window 
 */
function deleteKeypoints(){
	
	$('.timer_keypoints').empty();
}

function record_data(type){
	var total =  parseInt((total_worked + total_pause)/value_of_minutes);
	var id = $('.timer_id').text();
	if (type == 'ready') {
		$('tr[id="' + id + '"]').css('color','grey');
	} else if (type == 'standby') {
		$('tr[id="' + id + '"]').css('color','orange');
	}
	
	var actual = parseInt(total_worked/value_of_minutes);
	var pause = parseInt(total_pause/value_of_minutes);
		
	$('tr[id="' + id + '"]').children('td.actual').text(actual);
	$('tr[id="' + id + '"]').children('td.pause').text(pause);
	$('tr[id="' + id + '"]').children('td.total').text(total);
	$('tr[id="' + id + '"]').children('td.status').text(type); 
	$('tr[id="' + id + '"]').attr('class', 'product timed');
	// prevent later timing of this product
	$('tr[id="' + id + '"]').unbind('click');

	//console.log($('tr[id="' + id + '"]')); // test delete 
	data = {'ac_od_id' : id, 'actual': actual, 'pause': pause, 'status' : type};
	data = JSON.stringify(data);
	
	/*
	 * build the url from the settings
	 */
	var home_on_server = $('.home_on_server').text();
	url = home_on_server + '/record/';
	
    jQuery.ajax({
      type: "POST",
      url: url,
      data: data,
      //success: function(status){},
      error: function (status) {alert('Could not record this in database, call Nello')}
    });
}


/*
 * calculate a total from a certain number of coloums identified by the
 * class and write the total in a tag identified by the class
 */
function totals(totals,target){

	var total = 0;  		
	var plan = $(totals).each(function(){
		var element = $(this).text();
		if(parseInt(element)){
			total = total + parseInt(element);
		}
	});
	var t = moment([0, 0, 0, 0, 0, 0, 0]);
	t.add('minutes', total);
	$(target).text(t.format('H:mm'));	
}

$(document).ready(function(){

	var timeline = new Raphael($('.timeline').children('div.canvas_container').get(0), 740, 80);
	draw_scale(timeline);
	var time_color = 'grey';
	var overtime_color = 'orange';
   
    if(value_of_minutes != 60){
    	$('.test').show();
    }
    
	// click on the row open the timer
	$("tr.product").click(function(event){
		
		assembly = $( ".assembly_dialog" ).dialog({
            height: DIALOG_HEIGHT,
            width: DIALOG_WIDTH,
			modal: true,
			resizable: false,
			draggable: false
		});
        $(assembly).css('width', DIALOG_WIDTH);
        $(assembly).css('height', DIALOG_HEIGHT);

		PRODUCT = $(this);
		
		var data = $(this).children('td.assembly').html();
		$('.assembly_data').html($(data));
	})
	
	$('.button_assembly_confirm').click(function(event){
		
		deleteKeypoints(); // delete key points
		event.preventDefault(); // prevent the click default
		$('.button_cancel').css('display', 'block'); // if button-play is pressed, button cancel desappear		
		timer = $( ".timer" ).dialog({
			height: DIALOG_HEIGHT,
			width: DIALOG_WIDTH,
			modal: true,
			resizable: false,
			draggable: false
		});

        $(timer).css('width', DIALOG_WIDTH);
        $(timer).css('height', DIALOG_HEIGHT);
        $(assembly).hide(); // to hide the prior dialog


		$( ".timer" ).css('display', 'inline');

		var product = PRODUCT.children('td.product').text();
		var description = PRODUCT.children('td.description').text();
		var plan = PRODUCT.children('td.plan').text();
		var id = PRODUCT.attr('id');
		
		
		//  key points are taken from the product htmls of the first screen and append in the dialog timer
		 		
		var keypoints = $(this).children('td.keypoints').children(); 		
		$('.timer_keypoints').append(keypoints); 			 		
		
		$('.timer_product').text(product)
		$('.timer_description').text(description)
		$('.timer_time').text("Time: " + plan + " minutes")
		$('.timer_id').text(id);
		
		time_spent = moment([0, 0, 0, 0, 0, 0, 0]);
		
	})
    
	function refresh (){
		
		// the totals at the bottoms of the main page
		totals('.plan','.total_plan');		
		totals('.actual','.total_actual');		
		totals('.pause','.total_pause');		
		totals('.total','.total_total');		
			
	    $('.block').each(function(){ $(this).remove();});
			last_end_date = moment();
			last_end_date.hours(day_start_hours);
			last_end_date.minutes(day_start_minutes);
			last_end_date.seconds(00);
			
			// Draw products that have been timed
		  	$('.timeline').find('tr.timed').each(function() {
		  		
		  		var status = $(this).children('td.status');		  		
		  		
				// set the appropriate color for the lines and unbind the click on the tr.product
				var id = $(this).attr('id');
		  		if(status.text() == "ready"){
					$(this).css('color','grey');
					$('tr[id="' + id + '"]').unbind('click');					
		  		}

		  		if(status.text() == "standby"){
					$(this).css('color','orange');
					$('tr[id="' + id + '"]').unbind('click');										
		  		}
		  		
				// choose color according to status	  		
		  		if(status.text() == "ready"){
		  			time_color = 'grey';
					overtime_color = '#D8D8D2';	  			
		  		}
		  		
		  		if(status.text() == "standby"){
		  			time_color = 'orange';
					overtime_color = '#CC7A00';	  			
		  		}	  		
		  		
				var product = $(this).children('td.product');
				
		        var start = $(this).children('td.start'); 
		        var start_date = moment(start.text());
						
		        var plan = $(this).children('td.plan');	
		        var pminutes = parseInt(plan.text());
						
		        var actual = $(this).children('td.total'); 
		        var aminutes = parseInt(actual.text());
				
				var end_date = moment(start.text());
				
		        var overtime = 0;
		        if (aminutes > pminutes){ overtime = aminutes - pminutes;} 
        
				if (aminutes > 0) {
					end_date.add('minutes', aminutes - overtime);
					draw_block($(this).attr('id'), product.text(), start_date, end_date, timeline, time_color);
				}
				
		        // Draw the block of the overtime (orange)
				if (parseInt(actual.text()) > parseInt(plan.text())){
					var actual_end_date = moment(end_date);
					actual_end_date.add('minutes', overtime);
					draw_block($(this).attr('id'), product.text(), end_date, actual_end_date, timeline, overtime_color);
					last_end_date = moment(actual_end_date);
				} else {
					last_end_date = end_date;
				}
			});

		// Draw the products that have not been timed yet according to their ETA
       var first_not_timed = $('.timeline').find("tbody tr[class!='product timed']:first");
        var plan = parseInt(first_not_timed.children('plan').text());
        var new_start = moment();
        var new_ETA = moment();
        new_ETA.add('minutes',plan);

        var offset = moment.duration(new_ETA - moment(first_not_timed.children('td.ETA').text()));
        
        var product = first_not_timed.children('td.product');
        draw_block($(this).attr('id'), product.text(), new_start, new_ETA, timeline, 'black');

		  $('.timeline').find("tbody tr[class!='product timed']").each(function() {
			  
	      var product = $(this).children('td.product');
	
			  var ETA = $(this).children('td.ETA');
		    var ETA_date = moment(ETA.text()); 
        ETA_date.add(offset);

		    var plan = $(this).children('td.plan');
		    var pminutes = parseInt(plan.text());
		    
        var start = moment(ETA_date);
        start.subtract('minutes', pminutes); 

			  draw_block($(this).attr('id'), product.text(), start, ETA_date, timeline, 'black');
		    });
		 
		$('.block').click(function (){ select($(this).attr('id'));});
	}

    refresh();
	
	if ($('div.timeline').get().length > 1) {
		$('table.jobs').hide();
		$('h2').css('font-size','14px');
		$('h2').css('margin','0px');
	}

	function select(id) {
		$('tbody').children().css('background','white');
		$('tbody').children('#'+id).css('background','#D8D8D2');
		$('.block').each(function (){
			$(this).attr({'stroke':$(this).attr('fill')});
		});
		$('#'+id).attr({'stroke':'black'});
	}
	 
	function init_timer() {
		flag_play = false; // wether play or  pause
		flag_start = false; // in order to record start time date the first time
		total_worked = 0; // milliseconds
		total_pause = 0; // milliseconds
		$('.timing').text('0:00:00');
		$('.button_play').css('background', 'url("http://169.254.184.4/img/playback_play.png") no-repeat scroll 0 0 transparent');
		$('.button_play').css('background-size', '150px 150px');		
		// kill the timer loops
		if (typeof(counter_pause) !== 'undefined') { clearInterval(counter_pause); };
		if (typeof(counter_working) !== 'undefined') { clearInterval(counter_working); };
	}

	init_timer();
	
	/*
	 * play/stop button is clicked 
	 */
	$('.button_play').click(function(event){
		
		// update start time only the first time
		event.preventDefault();
		
		$('.button_cancel').css('display', 'none'); // if button-play is pressed, button cancel desappear
		
		if(flag_start == false){
			flag_start = true;
			var id = $('.timer_id').text();
			var start = moment().format("YYYY/MM/DD HH:mm:ss");
			var start_ajax = moment().format("YYYY-MM-DD HH:mm:ss");
			$('tr[id="' + id + '"]').children('td.start').text(start);
			
			data = {'ac_od_id' : id, 'start_time' : start_ajax};
			data = JSON.stringify(data); 
			
			/*
			 * build the url from the settings
			 */
			var home_on_server = $('.home_on_server').text();
			url = home_on_server + '/play/';
			console.log(url); 			
			
		    jQuery.ajax({
		      type: "POST",
		      url: url,
		      data: data,
		      //success: function(status){console.log('SUCCESS')},
		      error: function (status) {alert('Could not record in database, speak to Nello')}
		    });
		}            
		
		if(flag_play == false){
			$('.button_play').css('background', 'url("http://169.254.184.4/img/playback_stop.png") no-repeat scroll 0 0 transparent');
			$('.button_play').css('background-size', '150px 150px');		
			flag_play = true;
			counter_working = setInterval(function() {
				total_worked++;
				time_spent.add('seconds', 1);
			   
				// only refresh time  if seconds ends with 0 or 5
				 var str = time_spent.format('ss');	
				 if (str.substr(1) == '5'){
			   		$('.timing').text(time_spent.format('H:mm:ss'))
				 }else if (str.substr(1) == '0') {
			   		$('.timing').text(time_spent.format('H:mm:ss'))				 	
				 }
				 				
			   // checks if the pause loop exist before to stop it
			   if(typeof(counter_pause) !== 'undefined'){
					clearInterval(counter_pause);                           
			   }
			}, 1000);
		}else{
			$('.button_play').css('background', 'url("http://169.254.184.4/img/playback_play.png") no-repeat scroll 0 0 transparent');                
			$('.button_play').css('background-size', '150px 150px');		
			flag_play = false;
			counter_pause = setInterval(function() {
			   total_pause++;
			}, 1000);                
			
			clearInterval(counter_working);
		}
	})
	 
    /*
     * record button clicked: open confirm window
     */   
	$('.button_record').click(function(event){
		event.preventDefault();	// prevent the click default			
		timer_confirm = $( ".timer_confirm" ).dialog({
            height: DIALOG_HEIGHT,
            width: DIALOG_WIDTH,
			modal: true,
			resizable: false,
			draggable: false
		});		
	})
	
	/*
     * confirm button clicked: close all the dialog windows, record data	 
     */	
	$('.button_confirm_ready').click(function(event){
		event.preventDefault();	// prevent the click default
		timer_confirm_ready = $( ".timer_confirm_ready" ).dialog({
            height: DIALOG_HEIGHT,
            width: DIALOG_WIDTH,
			modal: true,
			resizable: false,
			draggable: false
		});
	})

	/*
     * final button ready is clicked   	 
     */	
	$('.button_confirm_ready_ok').click('click', (function(event){
		event.preventDefault(); // prevent the click default
		// resets the interface to state before timing
		assembly.dialog('close');				
		timer_confirm_ready.dialog('close');  
		timer_confirm.dialog('close');
		timer.dialog('close');
		record_data('ready');		
		refresh();		 					
		init_timer();
	}))

	/*
     * standby button clicked: close all the dialog windows, record data	 
     */	
	$('.button_confirm_stanby').click(function(event){
		event.preventDefault();	// prevent the click default
		timer_confirm_ready = $( ".timer_confirm_standby" ).dialog({
            height: DIALOG_HEIGHT,
            width: DIALOG_WIDTH,
			modal: true,
			resizable: false,
			draggable: false
		});		
	})


	/*
     * final button standby is clicked   	 
     */	
	$('.button_confirm_standby_ok').click('click', (function(event){
		event.preventDefault(); // prevent the click default
		// resets the interface to state before timing
		assembly.dialog('close');		
		timer_confirm_ready.dialog('close');  
		timer_confirm.dialog('close');
		timer.dialog('close');
		record_data('standby');		
		refresh();		 					
		init_timer();
	}))

	/*
     *  button to go back
     */	
	$('.button_confirm_standby_cancel').click('click', (function(event){
		event.preventDefault(); // prevent the click default
		timer_confirm_ready.dialog('close');  
	}))
	
	/*
     *  button to go back
     */	
	$('.button_confirm_ready_cancel').click('click', (function(event){
		event.preventDefault(); // prevent the click default
		timer_confirm_ready.dialog('close');  
	}))

	/*
     *  button to go back
     */	
	$('.button_confirm_cancel').click(function(event){
		event.preventDefault(); // prevent the click default
		timer_confirm.dialog('close'); // resets the interface to state before timing
	})	

	/*
     *  button to go back
     */	
	$('.button_cancel').click(function(event){
		event.preventDefault(); // prevent the click default
		timer.dialog('close'); // resets the interface to state before timing
        $(assembly).show();
	})
	
	/*
     *  button to go back
     */	
	$('.button_assembly_cancel').click(function(event){
		event.preventDefault(); // prevent the click default
		assembly.dialog('close'); // resets the interface to state before timing
	})
});