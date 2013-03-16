'use strict';

describe('TodoCtrl', function() {
  var scope, todoCtrl;

  beforeEach(inject(function($rootScope, $controller) {
    scope = $rootScope.$new();
    todoCtrl = $controller(TodoCtrl, {$scope: scope});
  }));

  it('should have a login boolean set in the scope', function() {
    expect(scope.loggedIn).toBe(false);
  });
});
