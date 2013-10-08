/* global EpicEditor */
(function() {
'use strict';

var editor = new EpicEditor({
  container: 'body-editor',
  textarea: 'body',
  basePath: '/static/epiceditor'
});

editor.load();

})();
