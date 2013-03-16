'use strict';

var requires = ['todoApp.filters', 'todoApp.services', 'todoApp.directives'],
    app = angular.module('todoApp', requires);

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});
