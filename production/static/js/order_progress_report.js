$(function() {
    $( document ).tooltip();

    $('#time').click(function (){
        $('.assembly').show();
        $('.value').hide();
        $('.total_value').hide();
        $('.total_plan').show();
    });

    $('#value').click(function (){
        $('.value').show();
        $('.assembly').hide();
        $('.total_value').show();
        $('.total_plan').hide();
    });

    $('.text_container').keydown(function(){
        $('#record_note').show()
    })

    $('#record_note').click(function(event){

        event.preventDefault(event); // prevent the click default
        var note = $('.text_container').val();
        var url = $('.access_api_url').text() + 'orders/record_note';
        var ac_o_id = $('.order_number').text();

        var data = {'ac_o_id': ac_o_id, note:note};
        data = JSON.stringify(data);

        //console.log(data)

        $.ajax({
            type: "get"
           ,data: data
           ,url: url
           ,complete:function(jqXHR){
                $('#record_note').hide();
           }
        })
    })

}); // end of document ready