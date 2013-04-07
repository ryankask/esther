'use strict';

var services = angular.module('todoApp.services', ['ngResource']);

services.factory('List', function($resource) {
  return $resource('/todo/api/:userId/lists');
});
