/**
 * @fileoverview SCAPES app.
 */

'use strict';

goog.provide('scapes.app');

goog.require('goog.dom');
goog.require('scapes.config');
goog.require('scapes.hello');

/**
 * Adds an element to the dom and console logs a message.
 * @export
 */
scapes.app = function() {
  var newDiv = goog.dom.createDom('h1', null, 'Hello {{ctrl.docId}}!');
  goog.dom.appendChild(document.body, newDiv);

  var helloObject = new scapes.hello.HelloClass();
  helloObject.shout();
};

/**
 * Angular module for scapes.
 */
scapes.app.module = angular.module('scapes', [
  scapes.config.module.name,
  'ngResource'
]);

// TODO(michaelcupino): When angular1.2 externs includes the spec for $resource,
// update this jsdoc.
/**
 * @param {!angular.Scope} $scope
 * @param {!Function} $resource
 * @param {!scapesexterns.ScapesConfig} scapesConfig
 * @constructor
 * @ngInject
 */
scapes.app.HomeCtrl = function($scope, $resource, scapesConfig) {
  // TODO(michaelcupino): Use @export annotation when closure compiler has these
  // flags: --remove_unused_prototype_props_in_externs=false and
  // --export_local_property_definitions.
  $scope.ctrl = this;
  goog.exportProperty($scope, 'ctrl', $scope.ctrl);
   
  /** @type {string} */
  this.docId = '';
  goog.exportProperty(this, 'docId', this.docId);

  /** @type {string} */
  this.statusMessage = '';
  goog.exportProperty(this, 'statusMessage', this.statusMessage);

  /** @type {string} */
  this.pipelineUrl = '';
  goog.exportProperty(this, 'pipelineUrl', this.pipelineUrl);

  /** @type {string} */
  this.authUrl = '';
  goog.exportProperty(this, 'authUrl', this.authUrl);

  /** @type {boolean} */
  this.isUserLoggedIn = scapesConfig.isUserLoggedIn;
  goog.exportProperty(this, 'isUserLoggedIn', this.isUserLoggedIn);

  /** @type {string} */
  this.loginUrl = scapesConfig.loginUrl;
  goog.exportProperty(this, 'loginUrl', this.loginUrl);

  // TODO(michaelcupino): Figure out how to declare that there is a static
  // method on this class named 'post'.
  /**
   * @constructor
   * @private
   */
  this.ServerService_ = $resource('/document-analysis', {}, {
    post: {
      method: 'POST'
    }
  });
};
scapes.app.module.controller('HomeCtrl', scapes.app.HomeCtrl);

/**
 * @param {string} docId
 * @suppress {missingProperties}
 */
scapes.app.HomeCtrl.prototype.analyzeDoc = function(docId) {
  this.ServerService_.post({'docId': docId},
      goog.bind(scapes.app.HomeCtrl.prototype.analyzeOnSuccess_, this));
};
goog.exportProperty(scapes.app.HomeCtrl.prototype, 'analyzeDoc',
    scapes.app.HomeCtrl.prototype.analyzeDoc);

/**
 * @typedef {{
 *   statusMessage: string,
 *   numberOfDocs: number,
 *   pipelineUrl: string,
 *   authUrl: string
 * }}
 */
scapes.app.ServerResponse;

/**
 * @param {scapes.app.ServerResponse} response
 * @private
 */
scapes.app.HomeCtrl.prototype.analyzeOnSuccess_ = function(response) {
  this.statusMessage = response.statusMessage;
  // TODO(michaelcupino): Figure out why closure compiler renames pipelineUrl.
  this['pipelineUrl'] = response['pipelineUrl'];
  this['authUrl'] = response['authUrl'];
};

