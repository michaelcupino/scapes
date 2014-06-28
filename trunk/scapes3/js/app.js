/**
 * @fileoverview SCAPES app.
 */

'use strict';

goog.provide('scapes.app');

goog.require('goog.dom');
goog.require('scapes.hello');

/**
 * Adds an element to the dom and console logs a message.
 * @export
 */
scapes.app = function() {
  var newDiv = goog.dom.createDom('h1', null, 'Hello {{ctrl.yourName}}!');
  goog.dom.appendChild(document.body, newDiv);

  var helloObject = new scapes.hello.HelloClass();
  helloObject.shout();
};

/**
 * Angular module for scapes.
 */
scapes.app.module = angular.module('scapes', []);

/**
 * @param {!angular.Scope} $scope
 * @constructor
 * @ngInject
 */
scapes.app.HomeCtrl = function($scope) {
  // TODO(michaelcupino): Use @export annotation when closure compiler has these
  // flags: --remove_unused_prototype_props_in_externs=false and
  // --export_local_property_definitions.
  $scope.ctrl = this;
  goog.exportProperty($scope, 'ctrl', $scope.ctrl);
   
  this.yourName = 'world';
  goog.exportProperty(this, 'yourName', this.yourName);
};
scapes.app.module.controller('HomeCtrl', scapes.app.HomeCtrl);

