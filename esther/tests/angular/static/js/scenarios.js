'use strict';

describe('todo app', function() {

  beforeEach(function() {
    browser().navigateTo('/todo');
  });

  it('the create list form should be controlled by buttons and links',
     function() {
       expect(element('#create-list').css('display')).toBe('none');
       element('.options li:first a').click();
       expect(element('#create-list').css('display')).toBe('block');
       element('form .button.alert').click();
       expect(element('#create-list').css('display')).toBe('none');
       element('.options li:first a').click();
       expect(element('#create-list').css('display')).toBe('block');
   });

});
