document.addEventListener('DOMContentLoaded', () => {
  const copyCodeBtns = document.querySelectorAll('#copy-code');

  const copyCodeToClipboard = async (code) => {
    await navigator.clipboard.writeText(code);
  }

  copyCodeBtns.forEach(btn => {
    // Get code from
    const code = btn.getAttribute('data-clipboard-text');
    btn.addEventListener('click', () => copyCodeToClipboard(code))
  });
});
