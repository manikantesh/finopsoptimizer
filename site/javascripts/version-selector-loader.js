// Loader for version selector
fetch('version-selector.html')
  .then(response => response.text())
  .then(html => {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    const selector = temp.querySelector('.version-selector');
    if (selector) {
      document.addEventListener('DOMContentLoaded', function() {
        const header = document.querySelector('.md-header');
        if (header) {
          header.appendChild(selector);
        }
      });
    }
  }); 