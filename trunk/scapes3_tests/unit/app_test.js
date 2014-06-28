'use strict';

goog.require('scapes.app');

describe('scapes.app', function() {
  describe('HomeCtrl', function() {
    beforeEach(module(scapes.app.module.name));
    it('should assign yourName on scope', inject(function($controller) {
      var scope = {};
      var ctrl = $controller('HomeCtrl', {
        $scope: scope
      });
      expect(scope.ctrl.yourName).toBe('world');
    }));
  });
});

