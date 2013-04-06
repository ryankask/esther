'use strict';

describe('registerUrl', function() {
  var compile, UrlRegistry, compileHTML;

  compileHTML = function(html) {
    compile(angular.element(html))({});
  };

  beforeEach(module('todoApp.services'));
  beforeEach(module('todoApp.directives'));
  beforeEach(inject(function($injector) {
    compile = $injector.get('$compile');
    UrlRegistry = $injector.get('UrlRegistry');
  }));

  it('should register URLs via the UrlRegistry service ', function() {
    compileHTML('<link data-register-url itemprop="home" href="https://www.ryankaskel.com">' +
                '<link data-register-url itemprop="home" href="https://www.ryankaskel.com">' +
                '<link data-register-url itemprop="about" href="https://www.ryankaskel.com/about">');
    expect(UrlRegistry.get('home')).toBe('https://www.ryankaskel.com');
    expect(UrlRegistry.get('about')).toBe('https://www.ryankaskel.com/about');
    expect(UrlRegistry.size()).toBe(2);
  });

  it('should not register URLs if the required attributes are not supplied ', function() {
    compileHTML('<link data-register-url href="https://www.ryankaskel.com">' +
                '<link data-register-url itemprop="home1">' +
                '<link data-register-url itemprop="" href="https://www.ryankaskel.com">' +
                '<link data-register-url itemprop="home2" href="">');
    expect(UrlRegistry.size()).toBe(0);
  });
});
