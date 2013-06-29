 $(function(){
     //$('#main').contextmenu({target:'#context-menu'})
     //$('#main').contextmenu({target:'#context-menu2'})

     $('a.rat').click(function(){
         alert('the rat was click');
     });


     $('#print').click(function(){
         $('.delete').hide();
         window.print()
     });
 })