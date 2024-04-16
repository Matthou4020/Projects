// Display correct title for buy/sell modals
window.onload = function() {
document.querySelectorAll('.btn.btn-primary.btn-sm').forEach(function(button) {
  button.addEventListener('click', function(event) {
  let headerText = event.target.id === 'buybutton' ? 'Buy shares' : 'Sell shares';
  document.querySelector('#modaltitle').innerHTML = headerText;

  document.getElementById('modalconfirm').addEventListener('click', function(event) {
    headerText === 'Buy shares' ? modalform.action = '/buy' : modalform.action = '/sell';
  });
});
});
};


