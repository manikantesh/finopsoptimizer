// Loader for version selector (dropdown in nav bar, production-safe)
function fetchVersionSelector() {
  const paths = [
    'version-selector.html',
    '/finopsoptimizer/version-selector.html',
    '/version-selector.html'
  ];
  let tried = 0;
  function tryFetch() {
    if (tried >= paths.length) return;
    fetch(paths[tried])
      .then(response => {
        if (!response.ok) throw new Error('Not found');
        return response.text();
      })
      .then(html => {
        const temp = document.createElement('div');
        temp.innerHTML = html;
        // Only get the <select> element (dropdown)
        const selector = temp.querySelector('.version-selector select');
        if (!selector) return;
        selector.classList.add('finops-version-dropdown');
        // Minimal style for nav bar alignment
        selector.style.marginLeft = '16px';
        selector.style.height = '32px';
        selector.style.verticalAlign = 'middle';
        selector.style.fontSize = '1rem';
        selector.style.background = '#fff';
        selector.style.border = '1px solid #ccc';
        selector.style.borderRadius = '4px';
        selector.style.padding = '2px 8px';
        function tryInject(attempts = 0) {
          // Try to find the nav bar container
          const navBar = document.querySelector('.md-header__inner') || document.querySelector('.md-header-nav');
          if (navBar && selector && !document.querySelector('.finops-version-dropdown')) {
            navBar.appendChild(selector);
          } else if (attempts < 50) {
            setTimeout(() => tryInject(attempts + 1), 100);
          }
        }
        tryInject();
      })
      .catch(() => {
        tried++;
        tryFetch();
      });
  }
  tryFetch();
}
fetchVersionSelector(); 