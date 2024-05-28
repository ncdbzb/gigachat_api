const template = document.createElement('template')
const style = 
template.innerHTML = '<link href="../styles.css" rel="stylesheet"><div class="modal" id="modal"><div class="modal-header"><div class="title">Форма для отправки ошибок</div><button data-close-button class="close-button">&times;</button></div><div class="modal-body">  <form action="/bugreport" method="post" id="bug_report">    <input readonly class="path" id="path" name="path" hidden="true"><input readonly class="typo" id="typo" name="typo" style="width:95%;" hidden="true">  <p>Выделенный текст:</p><b>    <div class="typo" id="typo1" style="width:95%;"></div></b><p>Введите почту (по желанию):</p><input class="email" type="email" id="email" name="email" placeholder="esmail@example.com"style="width:95%;">  <p>Пожалуйста введите любую информацию, которая может нам помочь:</p><textarea class="text" name="text" id="text" cols="40" rows="3"style="width:95%; height: 200px; resize: none;"></textarea></p>  <input type="submit" value="Отправить">    </form></div></div><div id="overlay"></div>';


class BugReportForm extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: 'open'});
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }
}

customElements.define("bug-report-form", BugReportForm);