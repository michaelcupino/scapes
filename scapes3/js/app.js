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
  var newDiv = goog.dom.createDom('h1', null, 'Hello {{yourName}}!');
  goog.dom.appendChild(document.body, newDiv);

  var helloObject = new scapes.hello.HelloClass();
  helloObject.shout();
};

