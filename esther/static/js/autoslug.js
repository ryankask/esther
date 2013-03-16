(function() {
  'use strict';

  function autoslug(source, dest, key) {
    key = key || 's';
    window.onkeypress = function(event) {
      var sourceElement;

      if (String.fromCharCode(event.charCode) === key &&
          document.activeElement.nodeName !== 'INPUT' &&
          document.activeElement.nodeName !== 'TEXTAREA') {
        sourceElement = document.getElementById(source);
        document.getElementById(dest).value = slugify(sourceElement.value);
      }
    };
  }

  autoslug('title', 'slug');
})();
