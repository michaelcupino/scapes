'use strict';

goog.require('scapes.app');

describe('scapes.app', function() {
  describe('HomeCtrl', function() {
    var instance;
    var scope;
    var $httpBackend;

    beforeEach(module(function($provide) {
      $provide.constant('scapesConfig', {
        isUserLoggedIn: true,
        loginUrl: 'abc123'
      });
    }));
    beforeEach(module(scapes.app.module.name));
    beforeEach(inject(function($rootScope, $controller, _$httpBackend_) {
      scope = $rootScope.$new();
      instance = $controller('HomeCtrl', {
        $scope: scope
      });
      $httpBackend = _$httpBackend_;
    }));

    it('should assign fields on scope', function() {
      expect(scope.ctrl.docId).toBe('');
      expect(scope.ctrl.statusMessage).toBe('');
      expect(scope.ctrl.isUserLoggedIn).toBe(true);
      expect(scope.ctrl.loginUrl).toBe('abc123');
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

