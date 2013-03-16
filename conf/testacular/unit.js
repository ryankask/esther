basePath = '../../';

files = [
  JASMINE,
  JASMINE_ADAPTER,
  'esther/static/js/angular-1.0.6.min.js',
  'esther/tests/angular/static/js/lib/angular-mocks.js',
  'esther/static/js/todo/*.js',
  'esther/tests/angular/unit/*.js'
];

autoWatch = true;

browsers = ['Chrome'];

junitReporter = {
  outputFile: 'test_out/unit.xml',
  suite: 'unit'
};
