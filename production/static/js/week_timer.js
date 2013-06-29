DAY_START_HOURS = 09;
VALUE_OF_MINUTES = 60;

TIME_COLOR = 'grey';
OVERTIME_COLOR = 'orange';

day_start_date = moment();
day_start_date.hours(DAY_START_HOURS);
day_start_date.minutes(VALUE_OF_MINUTES);

/*
 * drow the scale 
 */
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

/*
 * draw the single block 
 */
function draw_block(id,f, start, end, paper, color) {
	var scale_start = moment(start);
	scale_start.hours(9);
	scale_start.minutes(0);
	var x = Math.abs(scale_start.diff(start, 'minutes'))+10;
	var width = Math.abs(start.diff(end, 'minutes'));
	var block = paper.rect(x,45,width,25).attr({'fill': color, 'stroke': color});
	var file_text = paper.text(x+10,78, f);
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

$(function() {
	// run the currently selected effect
	function runEffect() {
	// get effect type from
	var selectedEffect = $( "#effectTypes" ).val();
	// most effect types need no options passed by default
	var options = {};
	// some effects have required parameters
	if ( selectedEffect === "scale" ) {
		options = { percent: 100 };
	} else if ( selectedEffect === "size" ) {
		options = { to: { width: 280, height: 185 } };
	}

	// run the effect
	$( "#effect" ).show( selectedEffect, options, 500, callback );
};

//callback function to bring a hidden box back
function callback() {
	setTimeout(function() {
	$( "#effect:visible" ).removeAttr( "style" ).fadeOut();
	}, 1000 );
};
// set effect from select menu value
$( "#button" ).click(function() {
	runEffect();
		return false;
	});
	$( "#effect" ).hide();
});

$(document).ready(function(){
	
	/*
	 *  hide or show the timeline details
	 */
	$('.open').click(function(){
		$(this).next().fadeToggle('slow');
		$('.pause').hide();
		$('.total').hide();
	})	
	
	/*
	 * foreach table, witch is a day, make a loop
	 */
	$('.timeline').each(function(){
		
		// draw the first timeline
		var timeline = new Raphael($(this).children('div.canvas_container').get(0), 740, 90);
		draw_scale(timeline);
		
		/*
		 * for each product timed
		 */
		$(this).find('tr.timed').each(function(){
			
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
	  			TIME_COLOR = 'grey';
				OVERTIME_COLOR = '#D8D8D2';	  			
	  		}
	  		
	  		if(status.text() == "standby"){
	  			TIME_COLOR = 'orange';
				OVERTIME_COLOR = '#CC7A00';	  			
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
	        
	        if (aminutes > pminutes){ 
	        	overtime = aminutes - pminutes;
	        } 
	        
			if (aminutes > 0) {
				end_date.add('minutes', aminutes - overtime);
				draw_block($(this).attr('id'), product.text(), start_date, end_date, timeline, TIME_COLOR);
			}
			
   			// Draw the block of the overtime (orange)
			if (parseInt(actual.text()) > parseInt(plan.text())){
				var actual_end_date = moment(end_date);
				actual_end_date.add('minutes', overtime);
				draw_block($(this).attr('id'), product.text(), end_date, actual_end_date, timeline, OVERTIME_COLOR);
				last_end_date = moment(actual_end_date);
			} else {
				last_end_date = end_date;
			}

		});	// end of loop every td.timed 	
	}) // end of loop very table
}) // end of document ready 