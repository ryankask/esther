'use strict';

describe('todo app', function() {

  beforeEach(function() {
    browser().navigateTo('/todo');
  });

  it('should show TODO in the heading', function() {
    expect(element('div[role=main] h1').html()).toBe('TODO');
  });
});
