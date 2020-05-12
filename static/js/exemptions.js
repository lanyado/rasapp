/* eslint-disable no-unused-vars */
/* eslint-disable no-use-before-define */
function formatDate (givenDate) {
	const date = new Date(givenDate);
	let month = `${date.getMonth() + 1}`;
	let day = `${date.getDate()}`;
	const year = date.getFullYear();

	if (month.length < 2) { month = `0${month}`; }
	if (day.length < 2) { day = `0${day}`; }

	return [year, month, day].join('-');
}

function getExemptions () {
	$.post('/getExemptions', {
		id: $($('.tr-color-selected').find('td[name=id]')[0]).text(),
	}, (response) => {
		$('.exemptions-table-body').html(''); // clear the exemptions table
		const { exemptions } = response;
		Object.keys(exemptions).forEach((key) => {
			const name = key;
			const date = exemptions[name];
			const exemptionsTable = $('.exemptions-table-body')[1];
			addExemptions(exemptionsTable, name, date);
		});
	});
}

function getExemptionTr (exemptionsTable, name, date) {
	// add the exemption name selector
	let tr = '<td><select class="form-control">';

	// add the options to the exemption select
	if (name.length > 0) {
		tr += `<option selected>${name}</option>`;
	} else {
		const ALL_EXEMPTIONS = ['פטור מטבחים אמצש', 'פטור מטבחים סופש', 'פטור שמירות אמצש', 'פטור שמירות סופש'];
		const otherExemptions = $(exemptionsTable).find('select :selected');
		let ALREADY_EXEMPTIONS = [];
		if (otherExemptions.length > 0) {
			ALREADY_EXEMPTIONS = otherExemptions.map((i, el) => $(el).val()).get();
		}
		const EXEMPTIONS_TO_ADD = ALL_EXEMPTIONS.filter((x) => !ALREADY_EXEMPTIONS.includes(x));
		if (EXEMPTIONS_TO_ADD.length > 0) {
			EXEMPTIONS_TO_ADD.forEach((exemptionName) => { tr += `<option>${exemptionName}</option>`; });
		} else return '';
	}
	// add the date picker and the remove button
	tr += `</select></td><td><input type="date" value = "${date}" class="form-control" /></td>'
           <td><button type="button" class="btn btn-outline-danger remove">הסר</button></td>`;
	return tr;
}

function addExemptions (exemptionsTable, name, date) {
	const tr = $('<tr/>');
	const trContent = getExemptionTr(exemptionsTable, name, date);
	if (trContent) {
		tr.html(trContent);
		$(exemptionsTable).append(tr);
	}
}

function btnAdd () {
	// add a new exemption with a defult date on ADD BUTTON click
	const TODAY = new Date();
	const DEFAULT_DATE = TODAY.setFullYear(TODAY.getFullYear() + 10); // today + 1 month

	const exemptionsTable = $(this).closest('#exemptions-table')[0];
	$(exemptionsTable).find('option').not('select :selected').remove();
	addExemptions(exemptionsTable, '', formatDate(DEFAULT_DATE));
}
$('body').on('click', '.btnAdd', btnAdd);

function removeExemption () { // remove the last exemption on REMOVE BUTTON click
	$(this).closest('tr').remove();
}
$('body').on('click', '.remove', removeExemption);

(() => {
	const element1 = $('#exemptions-table').clone();
	$('#exemptions-table-warpper1').html(element1);
	const element2 = $('#exemptions-table').clone();
	$('#to-remove').remove();
	$('#exemptions-table-warpper2').html(element2);
})();
