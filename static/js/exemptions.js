function getExemptions (){
    $.post( "/getExemptions", {
        id: $($('#editInputs').find('#inputId2')).val()
      },function(response){
        $(".exemptions-table-body").html("") // clear the exemptions table
            const exemptions = response.exemptions;
            Object.keys(exemptions).forEach(function (key) {
                const name = key;
                const date = exemptions[name];
                addExemptions(name, date)
                if (exemptions[name])
                    $($(`input[title|='${name}']`)[0]).val(exemptions[name])
                else
                    $($(`input[title|='${name}']`)[0]).val('')
            });
    });
}

function getExemptionTr (name, date) {
    const EXEMPTIONS_NAMES = new Set(['פטור מטבחים אמצש', 'פטור מטבחים סופש','פטור שמירות אמצש','פטור שמירות סופש']);
    let tr = '<td><select class="form-control">';

    EXEMPTIONS_NAMES.forEach((exemptionName) => {tr+= `<option>${exemptionName}</option>`});

    tr += `</select></td><td><input type="date" value = "${date}" class="form-control" /></td>'
           <td><button type="button" class="btnAdd btn btn-outline-danger remove">הסר</button></td>`;
    return tr;
}

function addExemptions (name, date){
    let tr = $("<tr/>");
    tr.html(getExemptionTr(name, date));

    if (name)
        $(tr).find(`option:contains("${name}")`).attr('selected','selected');

    $(".exemptions-table-body").append(tr);
}

function formatDate (date) {
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
    const element1 = $('#exemptions-table').clone();
    $("#exemptions-table-warpper1" ).html(element1);
    const element2 = $('#exemptions-table').clone();
    $('#to-remove').remove();
    $("#exemptions-table-warpper2" ).html(element2);
})();

$(".btnAdd").bind("click", () => {
    // add a new exemption with a defult date on ADD BUTTON click
    const TODAY = new Date();
    const DEFAULT_DATE = TODAY.setFullYear(TODAY.getFullYear() + 10); // today + 1 month

    addExemptions("",formatDate(DEFAULT_DATE));
});

function removeExemption (){  // remove the last exemption on REMOVE BUTTON click
    $(this).closest("tr").remove();
}
$("body").on('click', '.remove', removeExemption);
