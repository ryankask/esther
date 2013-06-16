'use strict';

angular.module('todoApp', ['todoApp.controllers', 'todoApp.filters',
                           'todoApp.services', 'todoApp.directives'])
  .config(function($interpolateProvider, $httpProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    $httpProvider.defaults.transformRequest = function(data) {
      if (data === undefined) {
        return data;
      }
      return $.param(data);
    };
  });
