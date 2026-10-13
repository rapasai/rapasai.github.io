/* RapasAI Lab /ask: network requests happen only after a user submits the form. */
(() => {
  'use strict';
  const form = document.getElementById('contact-form');
  const button = document.getElementById('submit-button');
  const label = document.getElementById('submit-label');
  const status = document.getElementById('form-status');
  const success = document.getElementById('success-panel');
  if (!form || !button || !label || !status || !success) return;
  let busy = false;
  function setMessage(text, isError) {
    status.textContent = text;
    status.classList.toggle('error', Boolean(isError));
    status.hidden = !text;
  }
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    // Honeypot: do not transmit robot submissions.
    if (form.elements['_gotcha']?.value) return;
    busy = true;
    button.disabled = true;
    label.textContent = '送信中…';
    setMessage('送信しています。', false);
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      });
      if (!response.ok) throw new Error('送信失敗');
      form.hidden = true;
      success.hidden = false;
      success.focus();
    } catch (_error) {
      setMessage('送信できませんでした。通信状況をご確認のうえ、もう一度お試しください。', true);
    } finally {
      busy = false;
      button.disabled = false;
      label.textContent = '送信する';
    }
  });
})();
