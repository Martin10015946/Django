


var getNCName = function(name) {
        //if (name.indexOf('?') != -1) { 
        //    name = name.substr(0, name.lastIndexOf('?'));
        //}
        name = name.substr(0, name.lastIndexOf('.'));
        name = name.replace(/_/g, ' ');
        return name.substr(name.lastIndexOf('/') + 1)
}


$(function(){
    // initialize Boostrap right click function on img
    $('img').contextmenu();

    $('.menu-action').click(function(event){
        event.preventDefault(); // prevent the click default        
        var imgsrc = $(this).attr('src');
        var NCName = getNCName($(this).attr('src'));
        var NCStatus = $(this).attr('status');
        var folder = $('div#folder').text();
        var shop = $('div#shop').text();
        
        $('img[src*="' + imgsrc + '"]').attr("src", 'http://169.254.184.4/img/working.png');
            
        // build the url for the ajax call
        var home_on_server = $('#home_on_server').text();
        url = home_on_server + "/boardvision/set_status";
        // data to server
        data = {'shop':shop, 'folder':folder, 'NCStatus':NCStatus, 'NCName':NCName}

        jQuery.ajax({
            type: "POST",
            data: data,
            url: url,
            error: function () {alert('Cannot record to DB speak to Nello.');},
            success: function() {
                $('img[src*="http://169.254.184.4/img/working.png"]').attr("src", imgsrc + "?" + Math.random());
            }

        })
    })
}) // end of document ready
