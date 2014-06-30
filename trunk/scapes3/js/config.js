/**
 * @fileoverview Scapes config that contains the json object passed from the
 * server in layout.html.
 */

'use strict';

goog.provide('scapes.config');

/**
 * Scapes module that provides a scapesConfig constant, which comes from the
 * server in layout_handler.py. Please keep scapesexterns.ScapesConfig and
 * layout_handler.py in sync.
 */ 
scapes.config.module = angular.module('scapesConfigModule', []);

/**
 * @param {!angular.$window} $window
 * @ngInject
 */
scapes.config.factory = function($window) {
  return $window['scapesConfig'] || {};
};
scapes.config.module.factory('scapesConfig', scapes.config.factory);

