// Loader for version selector
fetch('version-selector.html')
  .then(response => response.text())
  .then(html => {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    const selector = temp.querySelector('.version-selector');
    function inject() {
      const header = document.querySelector('.md-header');
      if (header && selector && !document.querySelector('.version-selector')) {
        header.appendChild(selector);
      }
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', inject);
    } else {
      inject();
    }
  }); 