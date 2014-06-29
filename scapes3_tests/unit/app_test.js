'use strict';

goog.require('scapes.app');

describe('scapes.app', function() {
  describe('HomeCtrl', function() {
    var instance;
    var scope;
    var $httpBackend;

    beforeEach(module(scapes.app.module.name));
    beforeEach(inject(function($rootScope, $controller, _$httpBackend_) {
      scope = $rootScope.$new();
      instance = $controller('HomeCtrl', {
        $scope: scope
      });
      $httpBackend = _$httpBackend_;
    }));

    it('should assign docId and statusMessge on scope', function() {
      expect(scope.ctrl.docId).toBe('');
      expect(scope.ctrl.statusMessage).toBe('');
    });

    it('should set the statusMessage on scope on success', function() {
      var response = {
        statusMessage: 'Hello hello',
        numberOfDocs: 5
      };
      $httpBackend.expectPOST('/angular').respond(response);
      instance.analyzeDoc('abc123');

      expect(scope.ctrl.statusMessage).toBe('');
      $httpBackend.flush();
      expect(scope.ctrl.statusMessage).toBe('Hello hello');
    });
  });
});

