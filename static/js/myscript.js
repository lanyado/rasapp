/* eslint-disable no-self-assign */
/* eslint-disable no-unused-vars */
(() => {
	$('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
	$('.dataTables_length').addClass('bs-select');
	window.domain = 'http://127.0.0.1:5000/';
})();

function showExcel (filename) {
	const promise = new Promise((resolve, reject) => {
		const url = `${window.domain}duties-table?filename=${filename}`;
		window.open(url, '_blank');
		resolve('opened the duties table');
	});
	return promise;
}

// eslint-disable-next-line consistent-return
function addUser (table, row) {
	for (let i = 0; i < 3; i += 1) { // chack that all all the must input are full
		if (row[i] === '' || row[i] === null) {
			swal('יש למלא את כל השדות', '', 'error');
			return 1;
		}
	}

	const exemptions = {};
	for (let i = 3; i < row.length - 1; i += 2) {
		const exemptionName = row[i];
		const exemptionDate = row[i + 1];

		exemptions[exemptionName] = exemptionDate;
	}

	const formData = new FormData();

	formData.append('id', row[0]);
	formData.append('name', row[1]);
	formData.append('unit', row[2]);
	formData.append('exemptions', JSON.stringify(exemptions));

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
			if (response.success) {
				swal(response.message, 'מעולה', 'success').then(() => {
					window.location = window.location;
				});
			} else swal(response.message, '', 'error');
		})
		.fail((jqXhr) => {
			console.log(jqXhr.responseJSON);
			swal('', 'נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר', 'error');
		});
}

function editUser (table, row) {
	const user = {
		id: $($('.modal-content').find('#inputId2')[0]).val(),
		name: $($('.modal-content').find('#inputName2')[0]).val(),
		unit: $($('.modal-content').find('#inputUnit2')[0]).val(),
	};

	const exemptions = {};
	const exemptionsTable = $('#exemptions-table-warpper2');
	const numberOfExemptions = exemptionsTable.find('select').length;

	for (let i = 0; i < numberOfExemptions; i += 1) {
		const exemptionName = $(exemptionsTable.find('select')[i]).val();
		const exemptionDate = $(exemptionsTable.find('input')[i]).val();

		exemptions[exemptionName] = exemptionDate;
	}

	const formData = new FormData();

	formData.append('user', JSON.stringify(user));
	formData.append('exemptions', JSON.stringify(exemptions));
	formData.append('original_id', $(row).children()[0].textContent);

	$.ajax({
		url: '/editUser',
		type: 'POST',
		dataType: 'json',
		data: formData,
		processData: false,
		cache: false,
		contentType: false,
	})
		.done((response) => {
			if (response.success) {
				swal(response.message, 'מעולה', 'success').then(() => {
					// refresh the page to see the changes
					window.location = window.location;
				});
			} else swal(response.message, '', 'error');
		})
		.fail((jqXhr) => {
			console.log(jqXhr.responseJSON);
			swal('', 'נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר', 'error');
		});
}

function removeUser (table, row) {
	const formData = new FormData();
	formData.append('id', $(row).children()[0].textContent);

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
			if (response.success) {
				swal(response.message, 'מעולה', 'success');
				// remove the user from the users html table
				table.row($(row)).remove().draw();
			} else swal(response.message, '', 'error');
		})
		.fail((jqXhr) => {
			console.log(jqXhr.responseJSON);
			swal('', 'נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר', 'error');
		});
}

function translate (word){
	const translateDict = {
		'kitchen' : 'מטבח',
		'shmirot' : 'שמירה',
	}

	for (const [key, value] of Object.entries(translateDict)) {
		if (word.includes(key)) return value; 
	}
}

function getUserInfo () {
	$.post('/getUserInfo', {
		id: $($('.tr-color-selected').find('td[name=id]')[0]).text(),
	}, (response) => {
		console.log(response);
		const { exemptions } = response;
		$('#info-last-weekday').html(`תורנות אמצש אחרונה : ${response.last_weekday}`)
		$('#info-last-weekend').html(`תורנות סופש אחרונה : ${response.last_weekend}`)

		
		let weekdayHistoryList = ''
		for (let [key, value] of Object.entries(response.weekday_history)) {
			value = translate(value);
			weekdayHistoryList += `<li><p>${key} : ${value}</p></li>`;
		}
		$('#info-weekday-history').html(`<h5> היסטורית תורנויות אמצש: </h5> <ul> ${weekdayHistoryList} </ul>`);

		let weekendHistoryList = ''
		for (let [key, value] of Object.entries(response.weekend_history)) {
			value = translate(value);
			weekendHistoryList += `<li><p>${key} : ${value}</p></li>`;
		}
		$('#info-weekend-history').html(`<h5> היסטורית תורנויות סופש: </h5> <ul> ${weekendHistoryList} </ul>`);
	});
}

function getWorkers () {
	// detect if the user didn't select dates
	if ($('.calendar_content .selected').length === 0) {
		swal('לא נבחרו תאריכים', '', 'error');
		return;
	}

	const formData = new FormData();
	formData.append('dates', JSON.stringify(window.dates));

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
			if (response.success) {
				swal(response.message, 'מעולה', 'success')
					.then(() => {
						// open it in a new tab
						showExcel(response.filename);
					})
					.then(() => {
						// refresh the dashboard
						window.location = window.location;
					});
			} else swal(response.message, '', 'error');
		})
		.fail((jqXhr) => {
			console.log(jqXhr.responseJSON);
			swal('', 'נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר', 'error');
		});
}
$('#get-workers').on('click', () => {
	getWorkers();
});

$('#view-excel').on('click', () => {
	let filename = $('#select-excel').val();
	filename = filename.replace(' הכי חדש', '');
	showExcel(filename);
});
