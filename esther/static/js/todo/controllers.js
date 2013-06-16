'use strict';

angular.module('todoApp.controllers', [])
  .controller('TodoCtrl', function($scope, $rootElement, List, Item) {
    var userId = $rootElement.data('user-id');

    if (!userId) {
      userId = 1;
      $scope.isAnonymousUser = true;
    } else {
      $scope.isAnonymousUser = false;
    }

    $scope.showCreateListForm = false;
    $scope.allLists = [];

    // Kick of the app and get the lists
    fetchLists();

    $scope.createList = function() {
      List.save({ userId: userId }, $scope.newList, function(lists) {
        $scope.showCreateListForm = false;
        $scope.newList = null;
        fetchLists();
      });
    };

    $scope.loadItems = function(list) {
      $scope.activeList = list;
      Item.query({ userId: userId, slug: list.slug }, function(items) {
        list.items = items;
        refreshList(list);
      });
    };

    $scope.createItem = function(list) {
      var params = { userId: userId, slug: list.slug };
      Item.save(params, $scope.newItem, function(response) {
        $scope.loadItems(list);
        $scope.newItem = null;
      });
    };

    $scope.markDone = function(list, item) {
      var params = { userId: userId, slug: list.slug, id: item.id },
          data = { is_done: true };
      Item.update(params, data, function(updatedItem) {
        item.is_done = updatedItem.is_done;
        refreshList(list);
      });
    };

    function fetchLists() {
      $scope.allLists = List.query({userId: userId});
    }

    function refreshList(list) {
      var i;

      list.hasItemsToDo = false;

      for (i = 0; i < list.items.length; i++) {
        if (list.items[i].is_done === false) {
          list.hasItemsToDo = true;
          break;
        }
      }
    }
  });
