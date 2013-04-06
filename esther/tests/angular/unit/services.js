'use strict';

describe('UrlRegistry', function() {
  var UrlRegistry;

  beforeEach(module('todoApp.services'));
  beforeEach(inject(function($injector) {
    UrlRegistry = $injector.get('UrlRegistry');
  }));

  it('should register URLs and make them available for retrieval ', function() {
    UrlRegistry.add('paris', 'http://paris.fr/');
    expect(UrlRegistry.get('paris')).toBe('http://paris.fr/');
  });
});
