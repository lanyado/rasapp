(function (){
  $('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
  $('.dataTables_length').addClass('bs-select');
})()

function addUser (table, row){
    for(let i=0; i<3; i++){ // chack that all all the must input are full
       if(row[i] === "" || row[i] === null) {
            swal("שגיאה", "יש למלא את כל השדות", "error");
            return 1;
       }
    }

    const exemptions = {}
    for(let i=3; i<row.length-1; i=i+2){
        const exemptionName = row[i];
        const exemptionDate = row[i+1];

        exemptions[exemptionName] = exemptionDate;
    }

    const formData = new FormData();

    formData.append('id', row[0])
    formData.append('name', row[1])
    formData.append('unit', row[2])
    formData.append('last_weekday', '2000-01-01')
    formData.append('last_weekend', '2000-01-01')
    formData.append('exemptions', JSON.stringify(exemptions))

    $.ajax({
        url: '/addUser',
        type: 'POST',
        dataType: 'json',
        data: formData,
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

function editUser (table, row){
    const user = {
      'id': $($('.modal-content').find('#inputId2')[0]).val(),
      'name': $($('.modal-content').find('#inputName2')[0]).val(),
      'unit': $($('.modal-content').find('#inputUnit2')[0]).val()
    }

    const exemptions = {};
    const exemptionsTable = $("#exemptions-table-warpper2");
    const numberOfExemptions = exemptionsTable.find('select').length;

    for(let i=0; i< numberOfExemptions; i++){
      const exemptionName = $(exemptionsTable.find('select')[i]).val();
      const exemptionDate = $(exemptionsTable.find('input')[i]).val();

      exemptions[exemptionName] = exemptionDate;
    }

    const formData = new FormData();

    formData.append('user', JSON.stringify(user))
    formData.append('exemptions', JSON.stringify(exemptions))
    formData.append('original_id', $(row).children()[0].textContent)

    $.ajax({
        url: '/editUser',
        type: 'POST',
        dataType: 'json',
        data: formData,
        processData: false,
        cache: false,
        contentType: false
    })
        .done((response) => {
            if (response.success){
              swal(response.message, "מעולה", "success").then(function() {
                    // refresh the page to see the changes
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

function removeUser (table, row){
    const formData = new FormData();
    formData.append('id', $(row).children()[0].textContent)

    $.ajax({
        url: '/removeUser',
        type: 'POST',
        dataType: 'json',
        data: formData,
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

function getToranim (){
  const formData = new FormData();
  formData.append('dates', JSON.stringify(window.dates))

   $.ajax({
       url: '/getToranim',
       type: 'POST',
       dataType: 'json',
       data: formData,
       processData: false,
       cache: false,
       contentType: false,
   })
       .done((response) => {
         if (response.success){
          swal(response.message, "מעולה", "success").then(function() {
              // open it in a new tab
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
}
$('#get-toranim').on('click',function(){
  getToranim();
})
