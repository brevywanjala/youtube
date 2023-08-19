function openCard(cardId) {
  var card = document.getElementById(cardId);
  var overlay = document.querySelector('.card-overlay');
  card.style.display = 'block';
  overlay.style.display = 'block';
}

function closeCard() {
  var cards = document.querySelectorAll('.card1');
  var overlay = document.querySelector('.card-overlay');
  for (var i = 0; i < cards.length; i++) {
    cards[i].style.display = 'none';
  }
  overlay.style.display = 'none';
}