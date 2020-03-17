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

  var exemptions = {}
  if (row.length>2){
    for(var i=3;i<row.length-1;i=i+2){ 
      var exemption_name = row[i];
      var exemption_date = row[i+1];

      exemptions[exemption_name] = exemption_date;
    }
  }

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
        if (response.success){
          table.row.add(row).draw(); // add the new user to the users html table
          swal(response.message, "מעולה", "success").then(function() {
                  window.location = window.location;
            });
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

    var user = {
      'id': $($('.modal-content').find('#inputId')[1]).val(),
      'name': $($('.modal-content').find('#inputName')[1]).val(),
      'unit': $($('.modal-content').find('#inputUnit')[1]).val()
    }

    var exemptions = {};
    for(var i=0;i<$("#exemptions_table_warpper2" ).find('select').length;i++){ 
      var exemption_name = $($("#exemptions_table_warpper2" ).find('select')[i]).val();
      var exemption_date = $($("#exemptions_table_warpper2" ).find('input')[i]).val();

      exemptions[exemption_name] = exemption_date;
    }

    var form_data = new FormData();
   
    form_data.append('user', JSON.stringify(user))
    form_data.append('exemptions', JSON.stringify(exemptions))

    form_data.append('original_id', $(row).children()[0].textContent)

    $.ajax({
        url: '/editUser',
        type: 'POST',
        dataType: 'json',
        data: form_data,
        processData: false,
        cache: false,
        contentType: false
    })
        .done((response) => {
          if (response.success){
            swal(response.message, "מעולה", "success").then(function() {
                  window.location = window.location; // refresh the page to see the changes
            });
          }
          else
            swal(response.message, "שגיאה", "error");
        })
        .fail((jqXhr) => {
            console.log(jqXhr.responseJSON)
            swal('שגיאה','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
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
          if (response.success){
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

function get_exemptions(){
  setTimeout(() => {
        $.post( "/getExemptions", {
            id: $($('#editInputs').find('#inputId')).val()
          },function(response){
            console.log(response.exemptions)
            $(".TextBoxContainer").html("") // clear the exemptions table
                for (key in response.exemptions){
                    var exemption_name = key
                    var exemption_date = response.exemptions[key]
                    add_exemptions(exemption_name, exemption_date)
                    if (response.exemptions[key])
                        $($("input[title|='"+key+"']")[0]).val(response.exemptions[key])
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


/*======== The exemptions table =======*/
function GetDynamicTextBox(name, date) {
    return '<td><select name="" class="form-control"><option>פטור מטבחים אמצש</option><option>פטור מטבחים סופש</option><option>פטור שמירות אמצש</option><option>פטור שמירות סופש</option></select></td>'+'<td><input name = "DynamicTextBox" type="date" value = "' + date + '" class="form-control" /></td>' + '<td>      <button type="button" class="btnAdd btn btn-outline-danger remove">הסר</button></td>'
}
function add_exemptions(name, date){
    var tr = $("<tr />");
    tr.html(GetDynamicTextBox(name, date));

     if (name != "")
        $(tr).find('option:contains("'+name+'")').attr('selected','selected');

     $(".TextBoxContainer").append(tr);
}

$(function () {
    var element1 = $('#exemptions_table').clone();
    $("#exemptions_table_warpper1" ).html(element1);
    var element2 = $('#exemptions_table').clone();

    $('#to_remove').remove();

    $("#exemptions_table_warpper2" ).html(element2);

    $(".btnAdd").bind("click", function () {
        add_exemptions("","")
    });
    $("body").on("click", ".remove", function () {
        $(this).closest("tr").remove();
    });
});
