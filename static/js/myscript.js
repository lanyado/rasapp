$('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
$('.dataTables_length').addClass('bs-select');
/*
$('#usersTable').bind('DOMSubtreeModified',function(){
  setTimeout(() => {
    $.post("/postmethod", {
      javascript_data: $('#usersTable').html()
    });
  }, 25);
})
*/
function get_ptorim(){
  setTimeout(() => {
        $.post( "/getPtorim", {
            javascript_data: $($('#editInputs').find('#inputId')).val()
          },function(response){
                for (key in response.ptorim){
                    if (response.ptorim[key])
                        $($("input[title|='"+key+"']")[0]).val(response.ptorim[key])
                    else
                        $($("input[title|='"+key+"']")[0]).val('')
                }
          });
    }, 25);
}

$('#download_icon').on('click',function(){
   $.post( "/giveExcel", {
        javascript_data: JSON.stringify(window.dates)
   });
})
