'use strict';

var module = angular.module('blogApp.filters', []);

module.filter('slugify', function() {
  return function(input) {
    return input.toString().toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w\-]+/g, '')
      .replace(/\-\-+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '');
  }
});
