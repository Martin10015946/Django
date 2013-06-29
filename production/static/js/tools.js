$(function(){

    // the user update the board thickness field
    $('input.measured_value').change(function(){

        var value = $(this).val();
        var tool_number = $(this).parent().parent().children('td.tool_number').text();
        var td_when_changed = $(this).parent().parent().children('td.when_changed');
        var td_day_used = $(this).parent().parent().children('td.days_used');
        var shop = $('.shop').text();

        // if the field is not empty, process it
        if(value != ""){
            var value = parseFloat(value);
            // if the user put something witch is not a number, show an error
            if (isNaN(value)){
                alert('Input a number');
            } else {
                var dict = {'shop': shop, 'tool_number': tool_number, 'value': value};

                // build the url for the ajax call
                var home_on_server = $('.home_on_server').text();
                var url = home_on_server + "/tools/record_tool_value";

                jQuery.ajax({
                    type: "POST",
                    data: dict,
                    url: url,
                    error: function (){
                        alert('Cannot record to DB speak to Nello.');
                    },
                    success:function(result){

                        var today = new Date();
                        var dd = today.getDate().toString();
                        var mm = today.getMonth()+1; //January is 0!
                        var mm = mm.toString();
                        var yyyy = today.getFullYear().toString();

                        $(td_when_changed).empty()
                        $(td_when_changed).text(dd + '/' + mm + '/' + yyyy);
                        $(td_day_used).css('background-color', 'white');
                        $(td_day_used).text('0');

                        // range alert
                        var range = Math.abs(result.standard_value - result.measured_value);
                        if(range > 1){
                            alert('ATTENTION: measure out of Range!')
                        }
                    }
                });
            }

        // the field cannot be empty
        } else {
            alert('The tool length cannot be empty');
        }
    })
}) // end of document ready