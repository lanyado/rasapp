(() => {
  $('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
  $('.dataTables_length').addClass('bs-select');
  window.domain = 'http://127.0.0.1:5000/'
})()

function addUser (table, row){
    for(let i=0; i<3; i++){ // chack that all all the must input are full
       if(row[i] === "" || row[i] === null) {
            swal("יש למלא את כל השדות", "","error");
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
    formData.append('weekday_history', JSON.stringify({}))
    formData.append('weekend_history', JSON.stringify({}))
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
          swal(response.message, "מעולה", "success").then(() => {
                  window.location = window.location;
          });
        }
        else
          swal(response.message, "", "error");
    })
    .fail((jqXhr) => {
        console.log(jqXhr.responseJSON)
        swal('','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
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
          swal(response.message, "מעולה", "success").then(() => {
                // refresh the page to see the changes
                window.location = window.location;
          });
        }
        else
          swal(response.message, "", "error");
    })
    .fail((jqXhr) => {
        console.log(jqXhr.responseJSON)
        swal('','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
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
        swal(response.message, "", "error");
    })
    .fail((jqXhr) => {
        console.log(jqXhr.responseJSON)
        swal('','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
    });
}

function getWorkers (){
    // detect if the user didn't select dates
    if ($('.calendar_content .selected').length===0){
        swal("לא נבחרו תאריכים", "", "error");
        return;
    }
      
    const formData = new FormData();
    formData.append('dates', JSON.stringify(window.dates))

    $.ajax({
        url: '/getWorkers',
        type: 'POST',
        dataType: 'json',
        data: formData,
        processData: false,
        cache: false,
        contentType: false,
    })
    .done((response) => {
      if (response.success){
        swal(response.message, "מעולה", "success")
        .then(() => {
            // open it in a new tab
            showExcel(response.filename);
        })
        .then(() => {
            // refresh the dashboard
            window.location = window.location;
        });
      }
      else
        swal(response.message, "", "error");
    })
    .fail((jqXhr) => {
        console.log(jqXhr.responseJSON)
        swal('','נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר','error');
    });
}
$('#get-workers').on('click',() => {
  getWorkers();
})

function showExcel (filename){
    let promise = new Promise((resolve, reject) => {
        const url = `${window.domain}duties-table?filename=${filename}`
        window.open(url, '_blank');
        resolve("open the duties table")
    });
    return promise;
}

$('#view-excel').on('click', () => {
    let filename = $('#select-excel').val();
    filename = filename.replace(' הכי חדש','');
    showExcel(filename);
})

