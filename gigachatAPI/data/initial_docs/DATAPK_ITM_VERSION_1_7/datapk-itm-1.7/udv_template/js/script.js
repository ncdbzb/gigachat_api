shadow = document.querySelector('bug-report-form').shadowRoot;
const closeModalButtons = shadow.querySelectorAll('[data-close-button]')
const overlay = shadow.getElementById('overlay')

window.addEventListener('keydown', (event) => {
  if (event.keyCode === 13 && event.ctrlKey) {
    const modal = shadow.getElementById('modal');
    updateValue();
    openModal(modal);
  }
});

overlay.addEventListener('click', () => {
  const modals = shadow.querySelectorAll('.modal.active')
  modals.forEach(modal => {
    closeModal(modal)
  })
})

closeModalButtons.forEach(button => {
  button.addEventListener('click', () => {
    const modal = button.closest('.modal');
    closeModal(modal);
  })
})

function openModal(modal) {
  console.log('open');
  if (modal == null) return
  console.log(modal)
  modal.classList.add('active');
  overlay.classList.add('active');
}

function closeModal(modal) {
  console.log('close');
  if (modal == null) return
  modal.classList.remove('active');
  overlay.classList.remove('active');
}

function updateValue() {
  console.log('update');
  shadow.getElementById("path").value = document.location.href;
  shadow.getElementById("typo").value = document.getSelection().toString();
  shadow.getElementById("typo1").innerHTML = document.getSelection().toString();
  shadow.getElementById("email").value = "";
  shadow.getElementById("text").value = "";
}