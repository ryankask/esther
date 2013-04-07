'use strict';

describe('TodoCtrl', function() {
  var scope, todoCtrl;

  beforeEach(module('todoApp.services'));
  beforeEach(inject(function($rootScope, $controller, $rootElement, List) {
    var deps;
    scope = $rootScope.$new();
    deps = {$scope: scope, $rootElement: $rootElement, List: List};
    todoCtrl = $controller(TodoCtrl, deps);
  }));

  it('should have a create list form boolean set to false ', function() {
    expect(scope.showCreateListForm).toBe(false);
  });
});
