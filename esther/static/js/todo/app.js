'use strict';

var requires = ['todoApp.filters', 'todoApp.services', 'todoApp.directives'],
    app = angular.module('todoApp', requires);

app.config(function($interpolateProvider, $httpProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});
