'use strict';

function TodoCtrl($scope, UrlRegistry) {
  $scope.showCreateListForm = false;

  $scope.createList = function() {
    console.log("Createing new list with title: " + $scope.newList.title +
                "; desscription: " + $scope.newList.description +
                "; is public? " + $scope.newList.is_public);
  };
}
