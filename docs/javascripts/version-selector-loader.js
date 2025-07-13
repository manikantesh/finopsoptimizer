// Robust loader for version selector
fetch('version-selector.html')
  .then(response => response.text())
  .then(html => {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    const selector = temp.querySelector('.version-selector');
    function tryInject(attempts = 0) {
      const header = document.querySelector('.md-header');
      if (header && selector && !document.querySelector('.version-selector')) {
        header.appendChild(selector);
      } else if (attempts < 50) { // Retry for up to 5 seconds
        setTimeout(() => tryInject(attempts + 1), 100);
      }
    }
    tryInject();
  }); 