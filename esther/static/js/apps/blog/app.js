'use strict';

var module = angular.module('blogApp', ['blogApp.filters']);

module.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});
