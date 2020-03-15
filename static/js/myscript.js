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
function add_user(table, row){
  for(var i=0;i<3;i++){ // chack that all all the must input are full
     if(row[i] === "" || row[i] === null) {
          swal("שגיאה", "יש למלא את כל השדות", "error");
          return 1;
     }
  }

  console.log(row)

  var exemptions = {'פטור שמירות אמצש': row[3],
                    'פטור שמירות סופש': row[4],
                    'פטור מטבחים אמצש': row[5],
                    'פטור מטבחים סופש': row[6]}

  var new_user = new FormData();

  new_user.append('id', row[0])
  new_user.append('name', row[1])
  new_user.append('unit', row[2])
  new_user.append('last_weekday', '2000-01-01')
  new_user.append('last_weekend', '2000-01-01')
  new_user.append('exemptions', JSON.stringify(exemptions))

  $.ajax({
      url: '/addUser',
      type: 'POST',
      dataType: 'json',
      data: new_user,
      processData: false,
      cache: false,
      contentType: false,
  })
      .done((response) => {
        if (response.add_successful){
          swal(response.message, "מעולה", "success");
          // add the new user to the users html table
          table.row.add(row).draw();
        }
        else
          swal(response.message, "שגיאה", "error");
      })
      .fail((jqXhr) => {
          console.log(jqXhr.responseJSON)
          swal('שגיאה','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
    });
}

function edit_user(table, row){

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

function remove_user(table, row){
    var user_to_remove = new FormData();
    user_to_remove.append('id', $(row).children()[0].textContent)

    $.ajax({
        url: '/removeUser',
        type: 'POST',
        dataType: 'json',
        data: user_to_remove,
        processData: false,
        cache: false,
        contentType: false,
    })
        .done((response) => {
          if (response.remove_successful){
            swal(response.message, "מעולה", "success");
            // remove the user from the users html table
            table.row($(row)).remove().draw();
          }
          else
            swal(response.message, "שגיאה", "error");
        })
        .fail((jqXhr) => {
            console.log(jqXhr.responseJSON)
            swal('שגיאה','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
      });
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
