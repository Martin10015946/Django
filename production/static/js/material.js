// Update the core order.
function updateCoreOrder(input){
    var th = input.attr('thickness');
    var order = input.attr('total') - input.val();
    if (order > 0) {
        $("td.order[thickness='" + String(th) + "']>span").text(order);
    }
}


$(function() {

    // Calculate the order
    $('input[week=4]').each(function () {
        if ($(this).val() != '') {
            var material_id = $(this).attr('material_id');
            var order = $(this).attr('total') - $(this).val();
            if (order > 0) {
                $("td.order#" + material_id + ">span").text(order);
            }
        }
    });

    // Update the core order.
    $('input.core').change(function (){
       updateCoreOrder($(this));
    });

    // Update every "to order" field of the plywood stock
    $('.core').each(function(){
        updateCoreOrder($(this));
    })

    // Update the stock materials order.
    $('input[week=4]').change(function () {
        var material_id = $(this).attr('material_id');
        var order = $(this).attr('total') - $(this).val();
        if (order > 0) {
         $("td.order#" + material_id + ">span").text(order);
        }
    });

    // Update the stock records.
    $('input.stock').change(function (){
        var material_id = $(this).attr('material_id');
        var week = $(this).attr('week');
        var data = {'id': material_id, 'week': week, 'qty': $(this).val()};
        var home_on_server = $('.home_on_server').text();
        data = JSON.stringify(data);
        url = home_on_server + "/materials/record_stock";
        jQuery.ajax({
            type: "POST",
            data: data,
            url: url,
            error: function () {alert('Cannot record to DB speak to Nello.');}
        });
    });

    // Control display of details of the core quantities calculation.
    $('div.bom:lt(3)').hide();
    $('a.calc').click(function (){
        $('div.bom:lt(3)').toggle();
    });

    // Show order in modal. 
    $('.order').click(function(event){
        event.preventDefault(); // prevent the click default

        order_detail = $(this).attr('href');
        $('.order_frame').attr('src', order_detail);
        $('#myModal2').modal('show');
    });

    // the material field loose the focus: ajax call to update OrderDetail materials
    $('.materials').blur(function(){

        var home_on_server = $('.home_on_server').text();
        var material = $(this).val();
        var ac_od_id = $(this).parent().parent().attr('class');

        //console.log(material)
        //console.log(ac_od_id)

        var dict = {'ac_od_id': ac_od_id, 'materials': material}
        var data = JSON.stringify(dict);

        url = home_on_server + "/record_materials/";
        jQuery.ajax({
            type: "POST",
            data: data,
            url: url,
            error: function () {alert('Cannot record to DB speak to Nello.');}
        });
    })

    // update Plywood stock
    $('.core').blur(function(){

        var home_on_server = $('.home_on_server').text();
        var stock_qty = $(this).val();
        var nominal_thickness = $(this).parent().prev().text();
        var data = {'nominal_thickness': nominal_thickness, 'stock_qty' : stock_qty};
        var url = home_on_server + "/record_stock_plywood/";

        if (stock_qty != ""){
            var stock_qty = parseInt(stock_qty);
            if(isNaN(stock_qty)){
                alert('Insert a number!');
                $(this).val('');
            } else {
                jQuery.ajax({
                    type: "POST",
                    data: data,
                    url: url,
                    error: function () {alert('Cannot record to DB speak to Nello.');}
                });
            }
        } else {
            // if the field is empty put 0
            var data = {'nominal_thickness': nominal_thickness, 'stock_qty' : 0};
            jQuery.ajax({
                type: "POST",
                data: data,
                url: url,
                error: function () {alert('Cannot record to DB speak to Nello.');}
            });
        }
    })

}); // end of document ready
