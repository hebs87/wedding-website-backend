document.addEventListener("DOMContentLoaded", () => {
  const copyLinkBtns = document.querySelectorAll("#copy-link");

  const copyLinkToClipboard = async (link) => {
    await navigator.clipboard.writeText(link);
  }

  copyLinkBtns.forEach(btn => {
    // Get link from
    const link = btn.getAttribute('data-clipboard-text');
    btn.addEventListener("click", () => copyLinkToClipboard(link))
  });
});
