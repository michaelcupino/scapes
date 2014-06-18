/**
 * @fileoverview HelloClass.
 */

'use strict';

goog.provide('scapes.hello');

/** 
 * A class that stores a message and can shout this message.
 * @constructor
 */
scapes.hello.HelloClass = function() {
  /**
   * @type {string}
   * @private
   */
  this.message_ = 'Hello from the scapes js app.';
};

/**
 * Shouts a message by logging to the console.
 */
scapes.hello.HelloClass.prototype.shout = function() {
  window.console.log(this.message_);
};

