'use strict';

var directives = angular.module('todoApp.directives', []);

directives.directive('registerUrl', function(UrlRegistry) {
  return function(scope, element, attrs) {
    var name = element.attr('itemprop'),
        url = element.attr('href');

    if (name && url) {
      UrlRegistry.add(name, url);
    }
  };
});
