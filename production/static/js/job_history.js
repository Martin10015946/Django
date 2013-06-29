function draw_scale(paper) {
		paper.path("M10 30L730 30");
		var start_hour = 9;
  	for(var i = 10; i < 740; i+=60) {	
			paper.path('M' + i.toString() + ' 30L' + i.toString() + ' 40');
			paper.text(i,20,start_hour.toString());
			start_hour += 1;
		}
}

function draw_block(id,f, start, end, paper) {
	var scale_start = new Date(start);
	scale_start.setHours(9);
	scale_start.setMinutes(0);
	var x = Math.abs((scale_start.getTime() - start.getTime())/1000/60)+10;
	var width = Math.abs((start.getTime() - end.getTime())/1000/60);
	var block = paper.rect(x,50,width,40).attr({'fill':'#FFCF73', 'stroke':'#FFCF73'});
	var file_text = paper.text(x,100, f)
	file_text.hide()
	block.node.setAttribute('class','block');
	block.node.setAttribute('id',id);
	
	block.hover(function () {
    block.attr({'stroke': '#A66D00'});
		file_text.show();
  },
  function () {
    block.attr({'stroke': '#FFCF73'});
		file_text.hide();
  });

}

function clean_dates(start,end) {
    /* pick up the date of today from span#id
    * and remove it from the date displayed in
    * the jobs table below.*/
    var d = $('span#date').text();
    start.text(start.text().replace(d,'').slice(0,6));
    end.text(end.text().replace(d,'').slice(0,6));
}

$(document).ready(function(){

    // set today value in the datapicker after the page is loaded (because the boostra .css blanck it)
    var today = $('.today').text();
    $('input').val(today);

	$('.timeline').each(function (){
		var timeline = new Raphael($(this).children('div.canvas_container').get(0), 740, 110);
		draw_scale(timeline);

	  $(this).find('tr').each(function() {
			var f = $(this).children('td.filename');
			var start = $(this).children('td.start');
			var end = $(this).children('td.end');
			var start_date = new Date(start.text());
			var end_date = new Date(end.text());
			draw_block($(this).attr('id'), f.text(), start_date, end_date, timeline);
		    clean_dates(start,end)
		});
	});

	/* For the week view: hide jobs tables, only show timelines */
    if ($('div.timeline').get().length > 1) {
		$('table.jobs').hide();
		$('h2').css('font-size','14px');
		$('h2').css('margin','0px');
	}

	function select(id) {
		$('tbody').children().css('background','white');
		$('tbody').children('#'+id).css('background','#A66D00');
		$('.block').attr({'fill':'#FFCF73', 'stroke':'#FFCF73'});
		$('#'+id).attr({'fill':'#A66D00', 'stroke':'#A66D00'});
	}

	$('.block').click(function (){ select($(this).attr('id'));});
	$('tr').click(function (){select($(this).attr('id'));});


    // date picker. Initialize date picker
    options = {'format':'dd/mm/yyyy', "autoclose": true};
    $('.dp1').datepicker(options)
        .on('changeDate', function(ev){


            //console.log(ev.date.valueOf())
            // istance of Date object to cath the values of the new date
            var newDate = new Date(ev.date);
            var day = newDate.getDate();
            var month = newDate.getMonth()+1;
            var year = newDate.getFullYear();

            var shop = $('.shop_tag').text();

            $('.datepicker').hide();

            var home_on_server = $('.home_on_server').text();
            //if (home_on_server != ""){
            //    home_on_server = '/' + home_on_server
            //}
            var url = home_on_server + '/jobhistory/' + year + '/' + month + '/' + day + '/' + shop

            window.location.href = url
        }); // end of data picker change event
});

