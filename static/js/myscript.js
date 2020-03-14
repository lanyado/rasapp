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
function add_user($table, $newRow){
  for(var i=0;i<3;i++){ // chack that all all the must input are full
     if($newRow[i] === "" || $newRow[i] === null) {
          swal("שגיאה", "יש למלא את כל השדות", "error");
          return 1;
     }
  }
  $table.row.add($newRow).draw();
  console.log($newRow)

  var exemptions = {'פטור שמירות אמצש': $newRow[3],
                    'פטור שמירות סופש': $newRow[4],
                    'פטור מטבחים אמצש': $newRow[5],
                    'פטור מטבחים סופש': $newRow[6]}

  var new_user = new FormData();

  new_user.append('id', $newRow[0])
  new_user.append('name', $newRow[1])
  new_user.append('unit', $newRow[2])
  new_user.append('last_weekday', '2000-01-01')
  new_user.append('last_weekend', '2000-01-01')
  new_user.append('exemptions', exemptions)

  $.ajax({
      url: '/addUser',
      type: 'POST',
      dataType: 'json',
      new_user: new_user,
      processData: false,
      cache: false,
      contentType: false,
  })
      .done((response) => {
        if (response.add_successful)
          swal(response.message, "מעולה", "success");
        else
          swal(response.message, "שגיאה", "error");
      })
      .fail((jqXhr) => {
          console.log(jqXhr.responseJSON)
          swal('שגיאה','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
    });
}

function edit_user(row){

    var id = $($('.modal-content').find('#inputId')[1]).val();
    var name = $($('.modal-content').find('#inputName')[1]).val();
    var unit = $($('.modal-content').find('#inputUnit')[1]).val();

    var p1 = $($('.modal-content').find('#inputP1')[1]).val();
    var p2 = $($('.modal-content').find('#inputP2')[1]).val();
    var p3 = $($('.modal-content').find('#inputP3')[1]).val();
    var p4 = $($('.modal-content').find('#inputP4')[1]).val();

    var original_id = $(row).children()[0].textContent;
    $.post( "/editUser", {
        original_id : original_id,
        id: id,
        name: name,
        unit: unit,
        p1: p1,
        p2: p2,
        p3: p3,
        p4: p4
    });
}

function remove_user(trInTableToRremove){
     $.post( "/removeUser", {
          javascript_data: $(trInTableToRremove).children()[0].textContent
     });

    $table.row($(trInTableToRremove)).remove().draw();
}

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
