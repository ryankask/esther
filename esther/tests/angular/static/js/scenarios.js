'use strict';

describe('todo app', function() {

  beforeEach(function() {
    browser().navigateTo('/todo');
  });

  it('the create list form should be controlled by buttons', function() {
    var createListForm = element('div[ng-show=showCreateListForm]'),
        createButton = element('.create-list');
    expect(createListForm.css('display')).toBe('none');
    createButton.click();
    expect(createListForm.css('display')).toBe('block');
    element('form .button.alert').click();
    expect(createListForm.css('display')).toBe('none');
    createButton.click();
    expect(createListForm.css('display')).toBe('block');
  });

});
