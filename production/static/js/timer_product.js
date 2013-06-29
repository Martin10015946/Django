PRODUCT = NaN; // global variable to save the tr.product when is clicked
// URL on witch the timer will be redirect after timing
URL = $('.home_on_server').text() + '/progress_report/' + $('.year').text() + '/' + $('.week').text() + '/' + $('.shop').text() + '/';

// modal dialog size
DIALOG_WIDTH = 900
DIALOG_HEIGHT = 500

day_start_hours = 09;
day_start_minutes = 00;
value_of_minutes = 60;

day_start_date = moment();
day_start_date.hours(day_start_hours);
day_start_date.minutes(day_start_minutes);

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
      error: function (status) {alert('Could not record this in database, call Nello')},
      success: function (status) {$(location).attr('href',URL);} // brak the url
    });
}

/*
 * calculate a total from a certain number of coloums identified by the
 * class and write the total in a tag identified by the class
 */
$(document).ready(function(){

    if(value_of_minutes != 60){
    	$('.test').show();
    }
		
    width = $(document).width();
    height = $(document).height();
    
    assembly = $( ".assembly_dialog" ).dialog({
            height: DIALOG_HEIGHT,
            width: DIALOG_WIDTH,
            modal: true,
            resizable: false,
            draggable: false
    });

    PRODUCT = $('tr.product');
    var data = PRODUCT.children('td.assembly').html();
    $('.assembly_data').html($(data));
	
    $('.button_assembly_confirm').click(function(event){
        deleteKeypoints(); // delete key points
        event.preventDefault(); // prevent the click default
        width = $(window).width();
        height = $(window).height();
        timer = $( ".timer" ).dialog({
                height: DIALOG_HEIGHT,
                width: DIALOG_WIDTH,
                modal: true,
                resizable: false,
                draggable: false
        });

        $( ".timer" ).css('display', 'inline');
        $(assembly).hide(); // hide the prior dialog to avoid overlap

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
        
	init_timer();        

    })
    

    // BUTTONS SETTINGS

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

        $(timer).hide();
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
            $(timer).show();
    })	

/*
 *  button to go back
 */	
    $('.button_cancel').click(function(event){
            event.preventDefault(); // prevent the click default
            timer.dialog('close'); // resets the interface to state before timing
            $(assembly).show(); // show the prior dialog

    })

/*
 *  button to go back
 */	
    $('.button_assembly_cancel').click(function(event){
            event.preventDefault(); // prevent the click default
            assembly.dialog('close'); // resets the interface to state before timing
            $(location).attr('href',URL);            
    })
}) // document ready end
