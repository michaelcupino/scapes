var h=this;
function k(a){var c=typeof a;if("object"==c)if(a){if(a instanceof Array)return"array";if(a instanceof Object)return c;var b=Object.prototype.toString.call(a);if("[object Window]"==b)return"object";if("[object Array]"==b||"number"==typeof a.length&&"undefined"!=typeof a.splice&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("splice"))return"array";if("[object Function]"==b||"undefined"!=typeof a.call&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("call"))return"function"}else return"null";else if("function"==
c&&"undefined"==typeof a.call)return"object";return c}function l(a){var c=k(a);return"array"==c||"object"==c&&"number"==typeof a.length}function m(a){return"string"==typeof a}function n(a){var c=typeof a;return"object"==c&&null!=a||"function"==c}function p(a,c,b){return a.call.apply(a.bind,arguments)}
function q(a,c,b){if(!a)throw Error();if(2<arguments.length){var e=Array.prototype.slice.call(arguments,2);return function(){var b=Array.prototype.slice.call(arguments);Array.prototype.unshift.apply(b,e);return a.apply(c,b)}}return function(){return a.apply(c,arguments)}}function u(a,c,b){u=Function.prototype.bind&&-1!=Function.prototype.bind.toString().indexOf("native code")?p:q;return u.apply(null,arguments)};var v=angular.module("scapesConfigModule",[]);function w(a){return a.scapesConfig||{}}w.$inject=["$window"];v.factory("scapesConfig",w);function x(a){if(!y.test(a))return a;-1!=a.indexOf("&")&&(a=a.replace(z,"&amp;"));-1!=a.indexOf("<")&&(a=a.replace(A,"&lt;"));-1!=a.indexOf(">")&&(a=a.replace(B,"&gt;"));-1!=a.indexOf('"')&&(a=a.replace(C,"&quot;"));-1!=a.indexOf("'")&&(a=a.replace(D,"&#39;"));return a}var z=/&/g,A=/</g,B=/>/g,C=/"/g,D=/'/g,y=/[&<>"']/;function E(a,c){return a<c?-1:a>c?1:0};var F=Array.prototype,G=F.indexOf?function(a,c,b){return F.indexOf.call(a,c,b)}:function(a,c,b){b=null==b?0:0>b?Math.max(0,a.length+b):b;if(m(a))return m(c)&&1==c.length?a.indexOf(c,b):-1;for(;b<a.length;b++)if(b in a&&a[b]===c)return b;return-1},H=F.forEach?function(a,c,b){F.forEach.call(a,c,b)}:function(a,c,b){for(var e=a.length,g=m(a)?a.split(""):a,d=0;d<e;d++)d in g&&c.call(b,g[d],d,a)};function I(a){var c=a.length;if(0<c){for(var b=Array(c),e=0;e<c;e++)b[e]=a[e];return b}return[]}
function aa(a,c,b){return 2>=arguments.length?F.slice.call(a,c):F.slice.call(a,c,b)};function ba(a,c){var b;b=a.className;b=m(b)&&b.match(/\S+/g)||[];for(var e=aa(arguments,1),g=b.length+e.length,d=b,f=0;f<e.length;f++)0<=G(d,e[f])||d.push(e[f]);a.className=b.join(" ");return b.length==g};function ca(a,c){for(var b in a)c.call(void 0,a[b],b,a)}var J="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");function da(a,c){for(var b,e,g=1;g<arguments.length;g++){e=arguments[g];for(b in e)a[b]=e[b];for(var d=0;d<J.length;d++)b=J[d],Object.prototype.hasOwnProperty.call(e,b)&&(a[b]=e[b])}};var K;a:{var L=h.navigator;if(L){var M=L.userAgent;if(M){K=M;break a}}K=""};var ea=-1!=K.indexOf("Opera")||-1!=K.indexOf("OPR"),N=-1!=K.indexOf("Trident")||-1!=K.indexOf("MSIE"),O=-1!=K.indexOf("Gecko")&&-1==K.toLowerCase().indexOf("webkit")&&!(-1!=K.indexOf("Trident")||-1!=K.indexOf("MSIE")),fa=-1!=K.toLowerCase().indexOf("webkit");function P(){var a=h.document;return a?a.documentMode:void 0}
var Q=function(){var a="",c;if(ea&&h.opera)return a=h.opera.version,"function"==k(a)?a():a;O?c=/rv\:([^\);]+)(\)|;)/:N?c=/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/:fa&&(c=/WebKit\/(\S+)/);c&&(a=(a=c.exec(K))?a[1]:"");return N&&(c=P(),c>parseFloat(a))?String(c):a}(),R={};
function S(a){if(!R[a]){for(var c=0,b=String(Q).replace(/^[\s\xa0]+|[\s\xa0]+$/g,"").split("."),e=String(a).replace(/^[\s\xa0]+|[\s\xa0]+$/g,"").split("."),g=Math.max(b.length,e.length),d=0;0==c&&d<g;d++){var f=b[d]||"",r=e[d]||"",ga=RegExp("(\\d*)(\\D*)","g"),ha=RegExp("(\\d*)(\\D*)","g");do{var s=ga.exec(f)||["","",""],t=ha.exec(r)||["","",""];if(0==s[0].length&&0==t[0].length)break;c=E(0==s[1].length?0:parseInt(s[1],10),0==t[1].length?0:parseInt(t[1],10))||E(0==s[2].length,0==t[2].length)||E(s[2],
t[2])}while(0==c)}R[a]=0<=c}}var T=h.document,U=T&&N?P()||("CSS1Compat"==T.compatMode?parseInt(Q,10):5):void 0;var ia=!N||N&&9<=U;!O&&!N||N&&N&&9<=U||O&&S("1.9.1");N&&S("9");function ja(a,c){ca(c,function(b,c){"style"==c?a.style.cssText=b:"class"==c?a.className=b:"for"==c?a.htmlFor=b:c in V?a.setAttribute(V[c],b):0==c.lastIndexOf("aria-",0)||0==c.lastIndexOf("data-",0)?a.setAttribute(c,b):a[c]=b})}var V={cellpadding:"cellPadding",cellspacing:"cellSpacing",colspan:"colSpan",frameborder:"frameBorder",height:"height",maxlength:"maxLength",role:"role",rowspan:"rowSpan",type:"type",usemap:"useMap",valign:"vAlign",width:"width"};
function ka(a,c,b){var e=arguments,g=document,d=e[0],f=e[1];if(!ia&&f&&(f.name||f.type)){d=["<",d];f.name&&d.push(' name="',x(f.name),'"');if(f.type){d.push(' type="',x(f.type),'"');var r={};da(r,f);delete r.type;f=r}d.push(">");d=d.join("")}d=g.createElement(d);f&&(m(f)?d.className=f:"array"==k(f)?ba.apply(null,[d].concat(f)):ja(d,f));2<e.length&&la(g,d,e);return d}
function la(a,c,b){function e(b){b&&c.appendChild(m(b)?a.createTextNode(b):b)}for(var g=2;g<b.length;g++){var d=b[g];if(!l(d)||n(d)&&0<d.nodeType)e(d);else{var f;a:{if(d&&"number"==typeof d.length){if(n(d)){f="function"==typeof d.item||"string"==typeof d.item;break a}if("function"==k(d)){f="function"==typeof d.item;break a}}f=!1}H(f?I(d):d,e)}}};function ma(){this.i="Hello from the scapes js app."};function W(){var a=ka("h1",null,"Hello {{ctrl.docId}}!");document.body.appendChild(a);window.console.log((new ma).i)}var X=["scapes","app"],Y=h;X[0]in Y||!Y.execScript||Y.execScript("var "+X[0]);for(var Z;X.length&&(Z=X.shift());)X.length||void 0===W?Y=Y[Z]?Y[Z]:Y[Z]={}:Y[Z]=W;W.module=angular.module("scapes",[v.name,"ngResource"]);
function $(a,c,b){a.g=this;a.ctrl=a.g;this.authUrl=this.f=this.pipelineUrl=this.j=this.statusMessage=this.statusMessage=this.docId=this.h="";this.isUserLoggedIn=this.isUserLoggedIn=b.isUserLoggedIn;this.loginUrl=this.loginUrl=b.loginUrl;this.c=c("/document-analysis",{},{post:{method:"POST"}});this.b=c("/folder-analysis",{},{post:{method:"POST"}})}$.$inject=["$scope","$resource","scapesConfig"];W.module.controller("HomeCtrl",$);$.prototype.d=function(a){this.c.post({docId:a},u($.prototype.a,this))};
$.prototype.analyzeDoc=$.prototype.d;$.prototype.e=function(a){this.b.post({folderId:a},u($.prototype.a,this))};$.prototype.analyzeFolder=$.prototype.e;$.prototype.a=function(a){this.statusMessage=a.statusMessage;this.pipelineUrl=a.pipelineUrl;this.authUrl=a.authUrl};
