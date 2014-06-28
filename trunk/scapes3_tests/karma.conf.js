module.exports = function(config) {
  config.set({
    frameworks: ['jasmine', 'closure'],

    basePath: '../',
    files: [
      'bower_components/closurelibrary/closure/goog/base.js',
      'bower_components/angular/angular.js',
      'bower_components/angular-route/angular-route.js',
      'bower_components/angular-resource/angular-resource.js',
      'bower_components/angular-animate/angular-animate.js',
      'bower_components/angular-mocks/angular-mocks.js',
      {
        pattern: 'bower_components/closurelibrary/closure/goog/deps.js',
        included: false,
        served: false
      },
      // TODO(michaelcupino): Move the compiled js into its own directory.
      {pattern: 'scapes3/js/*.js', included: false},
      'scapes3_tests/unit/*.js'
    ],

    preprocessors: {
      // tests are preprocessed for dependencies (closure) and for iits
      'scapes3_tests/unit/*.js': ['closure', 'closure-iit'],
      // source files are preprocessed for dependencies
      'scapes3/js/*.js': ['closure'],
      // external deps
      'bower_components/closurelibrary/closure/goog/deps.js': ['closure-deps']
    },

    autoWatch: true,

    browsers: ['Chrome'],

    plugins: [
      'karma-chrome-launcher',
      'karma-jasmine',
      'karma-closure'
    ],

    junitReporter: {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }
  });
};

