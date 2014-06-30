'use strict';

goog.require('scapes.config');

describe('scapes.config', function() {
  describe('scapesConfig', function() {
    beforeEach(module(scapes.config.module.name));

    it('should provide the window.scapesConfig if it exists', function() {
      var config = {a: 1};
      module(function($provide) {
        $provide.constant('$window', {
          scapesConfig: config
        });
      });
      inject(function(scapesConfig) {
        expect(scapesConfig).toBe(config);
      });
    });

    it('should provide an empty object if window.scapesConfig does not exist',
        inject(function(scapesConfig) {
          expect(scapesConfig).toEqual({});
        })
    );
  });
});

