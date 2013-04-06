'use strict';

var services = angular.module('todoApp.services', []);

services.factory('UrlRegistry', function() {
  var urls = {};

  return {
    add: function(name, url) {
      urls[name] = url;
    },
    get: function(name) {
      return urls[name];
    },
    size: function() {
      return Object.keys(urls).length;
    }
  }
});

// services.factory('List', function($resource) {
//   return $resource();
// });
