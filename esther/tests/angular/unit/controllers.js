'use strict';

describe('TodoCtrl', function() {
  var scope, todoCtrl;

  beforeEach(module('todoApp.services'));
  beforeEach(inject(function($rootScope, $controller, UrlRegistry) {
    scope = $rootScope.$new();
    todoCtrl = $controller(TodoCtrl, {$scope: scope, UrlRegistry: UrlRegistry});
  }));

  it('should have a create list form boolean set to false ', function() {
    expect(scope.showCreateListForm).toBe(false);
  });
});
