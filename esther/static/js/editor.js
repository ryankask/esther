(function() {
'use strict';

var body = $('#body'),
    editor = new EpicEditor({
      container: 'body-editor',
      basePath: '/static/epiceditor',
      file: {
        name: 'esther-post-body',
        defaultContent: $('#body').val(),
        autoSave: 100
      }
    });

editor.load(function() {
  editor.importFile(null, body.val());
});

editor.on('save', function() {
  body.val(editor.exportFile());
});

})();
