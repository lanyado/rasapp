(function (){
  $('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
  $('.dataTables_length').addClass('bs-select');
})();

function add_user(table, row){
    for(let i=0; i<3; i++){ // chack that all all the must input are full
       if(row[i] === "" || row[i] === null) {
            swal("שגיאה", "יש למלא את כל השדות", "error");
            return 1;
       }
    }

    let exemptions = {}
    for(let i=3; i<row.length-1; i=i+2){
        let exemption_name = row[i];
        let exemption_date = row[i+1];

        exemptions[exemption_name] = exemption_date;
    }

    let new_user = new FormData();

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
    let user = {
      'id': $($('.modal-content').find('#inputId2')[0]).val(),
      'name': $($('.modal-content').find('#inputName2')[0]).val(),
      'unit': $($('.modal-content').find('#inputUnit2')[0]).val()
    }

    let exemptions = {};
    let exemptions_table = $("#exemptions-table-warpper2");
    let number_of_exemptions = exemptions_table.find('select').length;

    for(let i=0; i< number_of_exemptions; i++){
      let exemption_name = $(exemptions_table.find('select')[i]).val();
      let exemption_date = $(exemptions_table.find('input')[i]).val();

      exemptions[exemption_name] = exemption_date;
    }

    let form_data = new FormData();

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
    let user_to_remove = new FormData();
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
            id: $($('#editInputs').find('#inputId2')).val()
          },function(response){
            $(".exemptions-table-body").html("") // clear the exemptions table
                const exemptions = response.exemptions;
                Object.keys(exemptions).forEach(function (key) {
                    let name = key;
                    let date = exemptions[name];
                    add_exemptions(name, date)
                    if (exemptions[name])
                        $($(`input[title|='${name}']`)[0]).val(exemptions[name])
                    else
                        $($(`input[title|='${name}']`)[0]).val('')
                });
          });
    }, 25);
}

$('#get_toranim').on('click',function(){
  let form_data = new FormData();
  form_data.append('dates', JSON.stringify(window.dates))

   $.ajax({
       url: '/getToranim',
       type: 'POST',
       dataType: 'json',
       data: form_data,
       processData: false,
       cache: false,
       contentType: false,
   })
       .done((response) => {
         if (response.success){
          swal(response.message, "מעולה", "success").then(function() {
              window.open(response.redirect_url, '_blank');
           });
         }
         else
           swal(response.message, "שגיאה", "error");
       })
       .fail((jqXhr) => {
           console.log(jqXhr.responseJSON)
           swal('שגיאה','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
     });

})

/*======== The exemptions table =======*/

function get_exemption_tr(name, date) {
    const exemptions_names = new Set(['פטור מטבחים אמצש', 'פטור מטבחים סופש','פטור שמירות אמצש','פטור שמירות סופש']);
    let tr = '<td><select class="form-control">';

    exemptions_names.forEach((exemption_name) => {tr+= `<option>${exemption_name}</option>`});

    tr += `</select></td><td><input type="date" value = "${date}" class="form-control" /></td>'
           <td><button type="button" class="btnAdd btn btn-outline-danger remove">הסר</button></td>`;
    return tr;
}

function add_exemptions(name, date){
    let tr = $("<tr/>");
    tr.html(get_exemption_tr(name, date));

    if (name)
        $(tr).find(`option:contains("${name}")`).attr('selected','selected');

    $(".exemptions-table-body").append(tr);
}

function formatDate(date) {
    let d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

(function (){
    let element1 = $('#exemptions-table').clone();
    $("#exemptions-table-warpper1" ).html(element1);
    let element2 = $('#exemptions-table').clone();
    $('#to_remove').remove();
    $("#exemptions-table-warpper2" ).html(element2);
})();

$(".btnAdd").bind("click", () => {
    // add a new exemption with a defult date on ADD BUTTON click
    const today = new Date();
    const defult_date = today.setFullYear(today.getFullYear() + 10); // today + 1 month

    add_exemptions("",formatDate(defult_date));
});

function removeExemption(){  // remove the last exemption on REMOVE BUTTON click
    $(this).closest("tr").remove();
}
$("body").on('click', '.remove', removeExemption);
