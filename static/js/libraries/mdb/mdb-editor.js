'use strict';

(function ($) {

  $.fn.mdbEditor = function () {

    return this.map(function (i, e) {

      var $selectedRow = void 0,
          $selectedTable = $(e),
          $selectedTableId = $selectedTable.closest('.wrapper-modal-editor').find('table').attr('id'),
          $selectedTableSharp = $('#' + $selectedTableId),
          $table = $('#' + $selectedTableId).DataTable(),
          $wrapperModalEditor = $selectedTableSharp.closest('.wrapper-modal-editor'),
          $createShowP = $wrapperModalEditor.find('.createShowP'),
          $buttonEdit = $wrapperModalEditor.find('.buttonEdit'),
          $buttonDelete = $wrapperModalEditor.find('.buttonDelete'),
          $buttonAddFormWrapper = $wrapperModalEditor.find('.buttonAddFormWrapper'),
          $buttonEditWrapper = $wrapperModalEditor.find('.buttonEditWrapper'),
          $editInsideWrapper = $wrapperModalEditor.find('.editInsideWrapper'),
          $deleteButtonsWrapper = $wrapperModalEditor.find('.deleteButtonsWrapper'),
          editInside = $wrapperModalEditor.find('.editInside'),
          trColorSelected = '.tr-color-selected';

      var addNewRows = function addNewRows() {

        //new user
        var $newRow = [];

        //add to the new user all the parameters
        for (var _i = 0; _i < $wrapperModalEditor.find('.addNewInputs input, .addNewInputs select').length; _i++) {
            $newRow.push($wrapperModalEditor.find('.addNewInputs input, .addNewInputs select').eq(_i).val());
        }

        addUser($table, $newRow);

      },
          btnToModalAdd = function btnToModalAdd(e) {

        var $etargetClosetWrapper = $(e.target).closest('.wrapper-modal-editor');

        $etargetClosetWrapper.find('.addNewInputs input, .addNewInputs select').val('');
        $etargetClosetWrapper.find('.addNewInputs label').removeClass('active');
        $etargetClosetWrapper.find('.addNewInputs input, .addNewInputs select').removeClass('valid');
      },
        addColorToTr = function addColorToTr(e) {
        return $(e.target).parent().not('thead tr').not('tfoot tr').toggleClass('tr-color-selected').siblings().removeClass('tr-color-selected');
      },
          toggleDisabledToButtons = function toggleDisabledToButtons(e) {

        $selectedRow = $(e.target).parent();

        if ($(e.target).parent().not('thead tr').not('tfoot tr').hasClass('tr-color-selected')) {

          $buttonEdit.prop('disabled', false);
          $buttonDelete.prop('disabled', false);
          $createShowP.html('1 row selected');
        } else if (!$('tr').hasClass('tr-color-selected')) {

          $buttonEdit.prop('disabled', true);
          $buttonDelete.prop('disabled', true);
          $createShowP.html('0 row selected');
        }
      },
          buttonEditInput = function buttonEditInput(e) {

        for (var _i2 = 0; _i2 < $(e.target).closest('.wrapper-modal-editor').find('thead tr').children().length; _i2++) {

          $table.row($wrapperModalEditor.find('.modalEditClass input').eq(_i2).val($table.cell($selectedRow, _i2).data()));
        }
      },
          addClassActiveToLabel = function addClassActiveToLabel() {
        return $('.modalEditClass label').addClass('active');
      },
          buttonEditInside = function buttonEditInside(e) {
            editUser($table, $selectedRow);

        for (var _i3 = 0; _i3 < $(e.target).closest('.wrapper-modal-editor').find('thead tr').children().length; _i3++) {
          $table.cell($(trColorSelected).find('td').eq(_i3)).data($wrapperModalEditor.find('.modalEditClass input').eq(_i3).val());
        }
      },
          removeColorClassFromTr = function removeColorClassFromTr() {
        return $selectedTable.find('.tr-color-selected').removeClass('tr-color-selected');
      },
          disabledButtons = function disabledButtons() {

        $buttonEdit.prop('disabled', true);
        $buttonDelete.prop('disabled', true);
      },
          selectedZeroRowsNews = function selectedZeroRowsNews() {

        $createShowP.html('0 row selected');
        $table.draw(false);
      },
          buttonDeleteYes = function buttonDeleteYes() {

             setTimeout(() => {
                removeUser($table, trColorSelected);
                $buttonEdit.prop('disabled', true);
                $buttonDelete.prop('disabled', true);
                $createShowP.html('0 row selected');
            }, 20);
      },
          bindEvents = function bindEvents() {

        $buttonAddFormWrapper.on('click', '.buttonAdd', addNewRows);
        $selectedTableSharp.on('click', 'tr', addColorToTr);
        $selectedTableSharp.on('click', 'tr', toggleDisabledToButtons);
        $buttonEditWrapper.on('click', $buttonEdit, buttonEditInput);
        $buttonEditWrapper.on('click', $buttonEdit, addClassActiveToLabel);
        $deleteButtonsWrapper.on('click', '.btnYesClass', buttonDeleteYes);
        $editInsideWrapper.on('click', editInside, buttonEditInside);
        $editInsideWrapper.on('click', editInside, removeColorClassFromTr);
        $editInsideWrapper.on('click', editInside, disabledButtons);
        $editInsideWrapper.on('click', editInside, selectedZeroRowsNews);
        $('.wrapperToBtnModalAdd').on('click', '.btnToModalAdd', btnToModalAdd);
      };

      bindEvents();
    });
  };

  $.fn.mdbEditorRow = function () {
    var _this = this;

    return this.map(function (i, e) {

      var editRow = '.editRow',
          saveRow = '.saveRow',
          tdLast = 'td:last',
          $removeColumns = $('.removeColumns'),
          $this = $(e),
          $tableId = $this.closest('.wrapper-row-editor').find('table').attr('id'),
          $sharpTableId = $('#' + $tableId),
          $tableData = $sharpTableId.DataTable(),
          addNewColumn = '.addNewColumn',
          $buttonWrapper = $('.buttonWrapper'),
          $closeByClick = $('.closeByClick'),
          $showForm = $('.showForm');

      var addNewTr = function addNewTr(e) {

        $(document).find($(e.target).parents().eq(1)).map(function (i, event) {

          $(event).find('tr').map(function (i, ev) {

            $(ev).find(tdLast).not('.td-editor').after('<td class="text-center td-editor" style="border-top: 1px solid #dee2e6; border-bottom:1px solid #dee2e6"><button class="btn btn-sm editRow btn-sm btn-teal"><i class="far fa-edit"></i></button></td>');
          });
        });
      },
          removeDisabledButtons = function removeDisabledButtons(e) {

        var $tableId = $(e.target).closest('.wrapper-row-editor').find('table').attr('id'),
            $findButton = $('#' + $tableId).closest('.wrapper-row-editor').find('.removeColumns');

        if ($('#' + $tableId).find('td').hasClass('td-editor') == true) {

          $findButton.prop('disabled', false);
        } else {

          $findButton.prop('disabled', true);
        }

        if (!$('#' + $tableId).closest('.wrapper-row-editor').find('td.td-editor').hasClass('td-editor')) {

          $findButton.prop('disabled', true);
        }
      },
          editRowAndAddClassToTr = function editRowAndAddClassToTr(e) {

        var $closestTrTd = $(e.target).closest('.wrapper-row-editor tr').find('td'),
            $closestTrEdit = $(e.target).closest('.wrapper-row-editor tr').find(editRow),
            divWrapper = '<div class="d-flex justify-content-center div-to-remove"></div>',
            editButton = '<td class="text-center td-editor td-yes" style="border:none"><button class="btn btn-sm btn-danger deleteRow" style="cursor:pointer;"><i class="fas fa-trash-alt"></i></b></td>',
            saveButton = '<td class="text-center td-editor td-yes" style="border:none"><button class="btn btn-sm btn-primary saveRow" style="cursor:pointer;"><i class="fas fa-check"></i></button></td>';

        for (var _i4 = 0; _i4 < $(e.target).closest('.wrapper-row-editor').find('table thead th').length; _i4++) {

          $closestTrTd.eq(_i4).html('<input type="text" class="val' + _i4 + ' form-control" value="' + $closestTrTd.eq(_i4).text() + '">');
        }

        $closestTrEdit.after($(divWrapper).append(saveButton, editButton));

        $($('#' + $tableId)).on('click', '.deleteRow', function () {

          $($('#' + $tableId).closest('.wrapper-row-editor').find('.showForm, .closeByClick').removeClass('d-none'));
        });
      },
          clickBtnCBCaddDnone = function clickBtnCBCaddDnone(e) {

        $(e.target).addClass('d-none');
        $showForm.addClass('d-none');
      },
          addDnoneByClickBtns = function addDnoneByClickBtns() {

        $showForm.addClass('d-none');
        $closeByClick.addClass('d-none');
      },
          addColorClassAndPy = function addColorClassAndPy(e) {

        var $closestTr = $(e.target).closest('tr');

        $closestTr.addClass('tr-color-selected');
        $closestTr.find('td').not('.td-editor').addClass('py-5');
      },
          addDisabledButtonsByEditBtn = function addDisabledButtonsByEditBtn(e) {

        $(e.target).prop('disabled', true);
        $(e.target).closest('.wrapper-row-editor').find($removeColumns).prop('disabled', true);
      },
          saveRowAndRemovePy = function saveRowAndRemovePy(e) {

        var $closestTr = $(e.target).closest('tr');

        for (var _i5 = 0; _i5 < $(e.target).closest('.wrapper-row-editor').find('table thead th').length; _i5++) {

          $tableData.cell($closestTr.find('td').eq(_i5)).data($closestTr.find('.val' + _i5).val());
        }

        $closestTr.find('td').removeClass('py-5');
      },
          removeDisabledColorAdnTdYes = function removeDisabledColorAdnTdYes(e) {

        var $closestTr = $(e.target).closest('tr');

        $closestTr.find(editRow).prop('disabled', false);
        $closestTr.removeClass('tr-color-selected');
        $closestTr.find('.td-yes').remove();
        $tableData.draw(false);

        $('#' + $(_this).closest('.wrapper-row-editor').find('table').attr('id')).closest('.wrapper-row-editor').find('.removeColumns').prop('disabled', false);
      },
          saveRowClickRemoveDiv = function saveRowClickRemoveDiv() {
        return $('.div-to-remove').remove();
      },
          removeColorInTrAndDraw = function removeColorInTrAndDraw(e) {

        var $tableId = $(e.target).closest('.wrapper-row-editor').find('table').attr('id');

        $tableData.row($('#' + $tableId).find('tr.tr-color-selected')).remove().draw(false);

        if (!$('#' + $tableId + ' tr').hasClass('td-editor')) {

          $('#' + $tableId).closest('.wrapper-row-editor').find($removeColumns).prop('disabled', false);
        } else {

          $('#' + $tableId).closest('.wrapper-row-editor').find($removeColumns).prop('disabled', true);
        }
      },
          removeSelectedButtonsFromRow = function removeSelectedButtonsFromRow(e) {

        var $tableId = $(e.target).closest('.wrapper-row-editor').find('table').attr('id');

        if (!$('#' + $tableId).hasClass('td-editor') === true) {

          $(e.target).closest('.wrapper-row-editor').find('.removeColumns').attr('disabled', true);
        }
        if ($('#' + $tableId).hasClass('td-editor') === false && $('#' + $tableId + ' tr').hasClass('tr-color-selected') === false) {

          $('#' + $tableId).find('.td-editor').remove();
          $('#' + $tableId).find('.tr-color-selected').remove();
          $tableData.draw(false);
        }
      },
          bindEvents = function bindEvents() {

        $buttonWrapper.on('click', addNewColumn, addNewTr);
        $buttonWrapper.on('click', addNewColumn, removeDisabledButtons);
        $this.on('click', editRow, editRowAndAddClassToTr);
        $this.on('click', editRow, addColorClassAndPy);
        $this.on('click', editRow, addDisabledButtonsByEditBtn);
        $this.on('click', saveRow, saveRowAndRemovePy);
        $this.on('click', saveRow, removeDisabledColorAdnTdYes);
        $this.on('click', saveRow, saveRowClickRemoveDiv);
        $('.buttonYesNoWrapper').on('click', '.btnYes', removeColorInTrAndDraw);
        $buttonWrapper.on('click', '.removeColumns', removeSelectedButtonsFromRow);
        $showForm.on('click', '.btnYes, .button-x, .btnNo', addDnoneByClickBtns);
        $closeByClick.on('click', clickBtnCBCaddDnone);
      };

      bindEvents();

      if ($closeByClick.hasClass('d-none') === true) {

        $(document).keyup(function (e) {

          if (e.keyCode === 27) {

            $closeByClick.addClass('d-none');
            $showForm.addClass('d-none');
          }
        });
      }
    });
  };

  $('.buttonWrapper').on('click', '.addNewRows', function (e) {

    var $newRow = [];

    for (var i = 0; i < $(e.target).closest('.wrapper-row-editor').find('table thead th').length; i++) {

      $newRow.push($(e.target).val());
    }

    $('#' + $(e.target).closest('.wrapper-row-editor').find('table').attr('id')).DataTable().row.add($newRow).draw();
  });
})(jQuery);
