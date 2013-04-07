'use strict';

function TodoCtrl($scope, $rootElement, List) {
  var userId = $rootElement.data('user-id');
  $scope.showCreateListForm = false;

  $scope.createList = function() {
    List.save({'userId': userId}, $scope.newList);
  };
}
