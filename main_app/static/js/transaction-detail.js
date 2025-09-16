
  document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('#id_transaction_date');
    if (!input || typeof MCDatepicker === 'undefined') return;

    // Ensure it's a text input for the picker (some browsers render date inputs differently)
    input.setAttribute('type', 'text');

    // Use existing value (if any), otherwise default to today
    const initial = input.value ? new Date(input.value) : new Date();

    const picker = MCDatepicker.create({
      el: '#id_transaction_date',
      dateFormat: 'yyyy-mm-dd',
      selectedDate: initial,
      maxDate: new Date(),      // prevent future dates
      closeOnBlur: true,
      customOkBTN: 'OK',
      customCancelBTN: 'Cancel'
    });

    input.addEventListener('click', () => picker.open());
  });
