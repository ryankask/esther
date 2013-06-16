'use strict';

angular.module('todoApp', ['todoApp.controllers', 'todoApp.filters',
                           'todoApp.services', 'todoApp.directives'])
  .config(function($interpolateProvider, $httpProvider) {
    var defaultContentType = 'application/x-www-form-urlencoded';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    $httpProvider.defaults.headers.post['Content-Type'] = defaultContentType;
    // PATCH is in the defaults in Angular 1.1
    $httpProvider.defaults.headers.patch = { 'Content-Type': defaultContentType };

    $httpProvider.defaults.transformRequest = function(data) {
      if (data === undefined) {
        return data;
      }
      return $.param(data);
    };
  });
