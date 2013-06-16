'use strict';

angular.module('todoApp.services', ['ngResource'])
  .factory('List', function($resource) {
    return $resource('/todo/api/:userId/lists');
  });
