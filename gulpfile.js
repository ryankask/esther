'use strict';

var path = require('path');
var gulp = require('gulp');
var rename= require('gulp-rename');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');

gulp.task('sass', function() {
  var sassOptions = {
    style: 'compressed',
    includePaths: ['bower_components/foundation/scss'],
    errLogToConsole: true
  };

  return gulp.src('client/scss/*.scss')
    .pipe(sass(sassOptions))
    .pipe(rename('app.min.css'))
    .pipe(gulp.dest('esther/static/css'));
});

gulp.task('js', function() {
  var files = [
    'bower_components/jquery/dist/jquery.min.js',
    'bower_components/foundation/js/foundation.min.js',
    'client/js/app.js'
  ];

  return gulp.src(files)
    .pipe(concat('app.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('esther/static/js'))
});

gulp.task('watch', function() {
  gulp.watch('client/scss/**/*.scss', ['sass']);
  gulp.watch('client/js/**/*.js', ['js']);
});

gulp.task('build', ['sass', 'js']);
gulp.task('default', ['build', 'watch']);