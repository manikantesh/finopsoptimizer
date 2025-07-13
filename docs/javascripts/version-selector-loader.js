// Loader for version selector (dropdown only, styled, next to title text)
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
        // Minimal style for alignment
        selector.style.marginLeft = '12px';
        selector.style.height = '32px';
        selector.style.verticalAlign = 'middle';
        function tryInject(attempts = 0) {
          // Find the FinOps Optimizer title text in the nav bar
          const titleText = document.querySelector('.md-header__title, .md-header-nav__title, .md-header .md-header__topic, .md-header__ellipsis');
          if (titleText && selector && !document.querySelector('.finops-version-dropdown')) {
            titleText.insertAdjacentElement('afterend', selector);
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