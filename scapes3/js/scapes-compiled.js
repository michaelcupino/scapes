var h=this;
function k(a){var b=typeof a;if("object"==b)if(a){if(a instanceof Array)return"array";if(a instanceof Object)return b;var c=Object.prototype.toString.call(a);if("[object Window]"==c)return"object";if("[object Array]"==c||"number"==typeof a.length&&"undefined"!=typeof a.splice&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("splice"))return"array";if("[object Function]"==c||"undefined"!=typeof a.call&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("call"))return"function"}else return"null";else if("function"==
b&&"undefined"==typeof a.call)return"object";return b}function l(a){var b=k(a);return"array"==b||"object"==b&&"number"==typeof a.length}function m(a){return"string"==typeof a}function n(a){var b=typeof a;return"object"==b&&null!=a||"function"==b}function p(a,b,c){return a.call.apply(a.bind,arguments)}
function q(a,b,c){if(!a)throw Error();if(2<arguments.length){var e=Array.prototype.slice.call(arguments,2);return function(){var c=Array.prototype.slice.call(arguments);Array.prototype.unshift.apply(c,e);return a.apply(b,c)}}return function(){return a.apply(b,arguments)}}function u(a,b,c){u=Function.prototype.bind&&-1!=Function.prototype.bind.toString().indexOf("native code")?p:q;return u.apply(null,arguments)};function v(a){if(!w.test(a))return a;-1!=a.indexOf("&")&&(a=a.replace(x,"&amp;"));-1!=a.indexOf("<")&&(a=a.replace(y,"&lt;"));-1!=a.indexOf(">")&&(a=a.replace(z,"&gt;"));-1!=a.indexOf('"')&&(a=a.replace(A,"&quot;"));-1!=a.indexOf("'")&&(a=a.replace(B,"&#39;"));return a}var x=/&/g,y=/</g,z=/>/g,A=/"/g,B=/'/g,w=/[&<>"']/;function C(a,b){return a<b?-1:a>b?1:0};var D=Array.prototype,E=D.indexOf?function(a,b,c){return D.indexOf.call(a,b,c)}:function(a,b,c){c=null==c?0:0>c?Math.max(0,a.length+c):c;if(m(a))return m(b)&&1==b.length?a.indexOf(b,c):-1;for(;c<a.length;c++)if(c in a&&a[c]===b)return c;return-1},F=D.forEach?function(a,b,c){D.forEach.call(a,b,c)}:function(a,b,c){for(var e=a.length,g=m(a)?a.split(""):a,d=0;d<e;d++)d in g&&b.call(c,g[d],d,a)};function G(a){var b=a.length;if(0<b){for(var c=Array(b),e=0;e<b;e++)c[e]=a[e];return c}return[]}
function H(a,b,c){return 2>=arguments.length?D.slice.call(a,b):D.slice.call(a,b,c)};function I(a,b){var c;c=a.className;c=m(c)&&c.match(/\S+/g)||[];for(var e=H(arguments,1),g=c.length+e.length,d=c,f=0;f<e.length;f++)0<=E(d,e[f])||d.push(e[f]);a.className=c.join(" ");return c.length==g};function aa(a,b){for(var c in a)b.call(void 0,a[c],c,a)}var J="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");function ba(a,b){for(var c,e,g=1;g<arguments.length;g++){e=arguments[g];for(c in e)a[c]=e[c];for(var d=0;d<J.length;d++)c=J[d],Object.prototype.hasOwnProperty.call(e,c)&&(a[c]=e[c])}};var K;a:{var L=h.navigator;if(L){var M=L.userAgent;if(M){K=M;break a}}K=""};var ca=-1!=K.indexOf("Opera")||-1!=K.indexOf("OPR"),N=-1!=K.indexOf("Trident")||-1!=K.indexOf("MSIE"),O=-1!=K.indexOf("Gecko")&&-1==K.toLowerCase().indexOf("webkit")&&!(-1!=K.indexOf("Trident")||-1!=K.indexOf("MSIE")),da=-1!=K.toLowerCase().indexOf("webkit");function P(){var a=h.document;return a?a.documentMode:void 0}
var Q=function(){var a="",b;if(ca&&h.opera)return a=h.opera.version,"function"==k(a)?a():a;O?b=/rv\:([^\);]+)(\)|;)/:N?b=/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/:da&&(b=/WebKit\/(\S+)/);b&&(a=(a=b.exec(K))?a[1]:"");return N&&(b=P(),b>parseFloat(a))?String(b):a}(),R={};
function S(a){if(!R[a]){for(var b=0,c=String(Q).replace(/^[\s\xa0]+|[\s\xa0]+$/g,"").split("."),e=String(a).replace(/^[\s\xa0]+|[\s\xa0]+$/g,"").split("."),g=Math.max(c.length,e.length),d=0;0==b&&d<g;d++){var f=c[d]||"",r=e[d]||"",ea=RegExp("(\\d*)(\\D*)","g"),fa=RegExp("(\\d*)(\\D*)","g");do{var s=ea.exec(f)||["","",""],t=fa.exec(r)||["","",""];if(0==s[0].length&&0==t[0].length)break;b=C(0==s[1].length?0:parseInt(s[1],10),0==t[1].length?0:parseInt(t[1],10))||C(0==s[2].length,0==t[2].length)||C(s[2],
t[2])}while(0==b)}R[a]=0<=b}}var T=h.document,U=T&&N?P()||("CSS1Compat"==T.compatMode?parseInt(Q,10):5):void 0;var ga=!N||N&&9<=U;!O&&!N||N&&N&&9<=U||O&&S("1.9.1");N&&S("9");function ha(a,b){aa(b,function(c,b){"style"==b?a.style.cssText=c:"class"==b?a.className=c:"for"==b?a.htmlFor=c:b in V?a.setAttribute(V[b],c):0==b.lastIndexOf("aria-",0)||0==b.lastIndexOf("data-",0)?a.setAttribute(b,c):a[b]=c})}var V={cellpadding:"cellPadding",cellspacing:"cellSpacing",colspan:"colSpan",frameborder:"frameBorder",height:"height",maxlength:"maxLength",role:"role",rowspan:"rowSpan",type:"type",usemap:"useMap",valign:"vAlign",width:"width"};
function ia(a,b,c){var e=arguments,g=document,d=e[0],f=e[1];if(!ga&&f&&(f.name||f.type)){d=["<",d];f.name&&d.push(' name="',v(f.name),'"');if(f.type){d.push(' type="',v(f.type),'"');var r={};ba(r,f);delete r.type;f=r}d.push(">");d=d.join("")}d=g.createElement(d);f&&(m(f)?d.className=f:"array"==k(f)?I.apply(null,[d].concat(f)):ha(d,f));2<e.length&&ja(g,d,e);return d}
function ja(a,b,c){function e(c){c&&b.appendChild(m(c)?a.createTextNode(c):c)}for(var g=2;g<c.length;g++){var d=c[g];if(!l(d)||n(d)&&0<d.nodeType)e(d);else{var f;a:{if(d&&"number"==typeof d.length){if(n(d)){f="function"==typeof d.item||"string"==typeof d.item;break a}if("function"==k(d)){f="function"==typeof d.item;break a}}f=!1}F(f?G(d):d,e)}}};function ka(){this.e="Hello from the scapes js app."};function W(){var a=ia("h1",null,"Hello {{ctrl.yourName}}!");document.body.appendChild(a);window.console.log((new ka).e)}var X=["scapes","app"],Y=h;X[0]in Y||!Y.execScript||Y.execScript("var "+X[0]);for(var Z;X.length&&(Z=X.shift());)X.length||void 0===W?Y=Y[Z]?Y[Z]:Y[Z]={}:Y[Z]=W;W.module=angular.module("scapes",["ngResource"]);function $(a,b){a.d=this;a.ctrl=a.d;this.statusMessage=this.statusMessage=this.yourName=this.f="";this.a=b("/angular",{},{post:{method:"POST"}})}$.$inject=["$scope","$resource"];
W.module.controller("HomeCtrl",$);$.prototype.b=function(){this.a.post({},u($.prototype.c,this))};$.prototype.analyzeDoc=$.prototype.b;$.prototype.c=function(a){this.statusMessage=a.statusMessage};
