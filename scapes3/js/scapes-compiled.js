var h=this;
function k(a){var c=typeof a;if("object"==c)if(a){if(a instanceof Array)return"array";if(a instanceof Object)return c;var b=Object.prototype.toString.call(a);if("[object Window]"==b)return"object";if("[object Array]"==b||"number"==typeof a.length&&"undefined"!=typeof a.splice&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("splice"))return"array";if("[object Function]"==b||"undefined"!=typeof a.call&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("call"))return"function"}else return"null";else if("function"==
c&&"undefined"==typeof a.call)return"object";return c}function l(a){var c=k(a);return"array"==c||"object"==c&&"number"==typeof a.length}function m(a){return"string"==typeof a}function n(a){var c=typeof a;return"object"==c&&null!=a||"function"==c};function p(a){if(!t.test(a))return a;-1!=a.indexOf("&")&&(a=a.replace(u,"&amp;"));-1!=a.indexOf("<")&&(a=a.replace(v,"&lt;"));-1!=a.indexOf(">")&&(a=a.replace(w,"&gt;"));-1!=a.indexOf('"')&&(a=a.replace(x,"&quot;"));-1!=a.indexOf("'")&&(a=a.replace(y,"&#39;"));return a}var u=/&/g,v=/</g,w=/>/g,x=/"/g,y=/'/g,t=/[&<>"']/;function z(a,c){return a<c?-1:a>c?1:0};var A=Array.prototype,B=A.indexOf?function(a,c,b){return A.indexOf.call(a,c,b)}:function(a,c,b){b=null==b?0:0>b?Math.max(0,a.length+b):b;if(m(a))return m(c)&&1==c.length?a.indexOf(c,b):-1;for(;b<a.length;b++)if(b in a&&a[b]===c)return b;return-1},C=A.forEach?function(a,c,b){A.forEach.call(a,c,b)}:function(a,c,b){for(var e=a.length,g=m(a)?a.split(""):a,d=0;d<e;d++)d in g&&c.call(b,g[d],d,a)};function D(a){var c=a.length;if(0<c){for(var b=Array(c),e=0;e<c;e++)b[e]=a[e];return b}return[]}
function E(a,c,b){return 2>=arguments.length?A.slice.call(a,c):A.slice.call(a,c,b)};function F(a,c){var b;b=a.className;b=m(b)&&b.match(/\S+/g)||[];for(var e=E(arguments,1),g=b.length+e.length,d=b,f=0;f<e.length;f++)0<=B(d,e[f])||d.push(e[f]);a.className=b.join(" ");return b.length==g};function G(a,c){for(var b in a)c.call(void 0,a[b],b,a)}var H="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");function I(a,c){for(var b,e,g=1;g<arguments.length;g++){e=arguments[g];for(b in e)a[b]=e[b];for(var d=0;d<H.length;d++)b=H[d],Object.prototype.hasOwnProperty.call(e,b)&&(a[b]=e[b])}};var J;a:{var K=h.navigator;if(K){var L=K.userAgent;if(L){J=L;break a}}J=""};var M=-1!=J.indexOf("Opera")||-1!=J.indexOf("OPR"),N=-1!=J.indexOf("Trident")||-1!=J.indexOf("MSIE"),O=-1!=J.indexOf("Gecko")&&-1==J.toLowerCase().indexOf("webkit")&&!(-1!=J.indexOf("Trident")||-1!=J.indexOf("MSIE")),P=-1!=J.toLowerCase().indexOf("webkit");function Q(){var a=h.document;return a?a.documentMode:void 0}
var R=function(){var a="",c;if(M&&h.opera)return a=h.opera.version,"function"==k(a)?a():a;O?c=/rv\:([^\);]+)(\)|;)/:N?c=/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/:P&&(c=/WebKit\/(\S+)/);c&&(a=(a=c.exec(J))?a[1]:"");return N&&(c=Q(),c>parseFloat(a))?String(c):a}(),S={};
function T(a){if(!S[a]){for(var c=0,b=String(R).replace(/^[\s\xa0]+|[\s\xa0]+$/g,"").split("."),e=String(a).replace(/^[\s\xa0]+|[\s\xa0]+$/g,"").split("."),g=Math.max(b.length,e.length),d=0;0==c&&d<g;d++){var f=b[d]||"",q=e[d]||"",aa=RegExp("(\\d*)(\\D*)","g"),ba=RegExp("(\\d*)(\\D*)","g");do{var r=aa.exec(f)||["","",""],s=ba.exec(q)||["","",""];if(0==r[0].length&&0==s[0].length)break;c=z(0==r[1].length?0:parseInt(r[1],10),0==s[1].length?0:parseInt(s[1],10))||z(0==r[2].length,0==s[2].length)||z(r[2],
s[2])}while(0==c)}S[a]=0<=c}}var U=h.document,V=U&&N?Q()||("CSS1Compat"==U.compatMode?parseInt(R,10):5):void 0;var ca=!N||N&&9<=V;!O&&!N||N&&N&&9<=V||O&&T("1.9.1");N&&T("9");function da(a,c){G(c,function(b,c){"style"==c?a.style.cssText=b:"class"==c?a.className=b:"for"==c?a.htmlFor=b:c in W?a.setAttribute(W[c],b):0==c.lastIndexOf("aria-",0)||0==c.lastIndexOf("data-",0)?a.setAttribute(c,b):a[c]=b})}var W={cellpadding:"cellPadding",cellspacing:"cellSpacing",colspan:"colSpan",frameborder:"frameBorder",height:"height",maxlength:"maxLength",role:"role",rowspan:"rowSpan",type:"type",usemap:"useMap",valign:"vAlign",width:"width"};
function ea(a,c,b){var e=arguments,g=document,d=e[0],f=e[1];if(!ca&&f&&(f.name||f.type)){d=["<",d];f.name&&d.push(' name="',p(f.name),'"');if(f.type){d.push(' type="',p(f.type),'"');var q={};I(q,f);delete q.type;f=q}d.push(">");d=d.join("")}d=g.createElement(d);f&&(m(f)?d.className=f:"array"==k(f)?F.apply(null,[d].concat(f)):da(d,f));2<e.length&&fa(g,d,e);return d}
function fa(a,c,b){function e(b){b&&c.appendChild(m(b)?a.createTextNode(b):b)}for(var g=2;g<b.length;g++){var d=b[g];if(!l(d)||n(d)&&0<d.nodeType)e(d);else{var f;a:{if(d&&"number"==typeof d.length){if(n(d)){f="function"==typeof d.item||"string"==typeof d.item;break a}if("function"==k(d)){f="function"==typeof d.item;break a}}f=!1}C(f?D(d):d,e)}}};function ga(){this.a="Hello from the scapes js app."};function X(){var a=ea("h1",null,"Hello {{yourName}}!");document.body.appendChild(a);window.console.log((new ga).a)}var Y=["scapes","app"],Z=h;Y[0]in Z||!Z.execScript||Z.execScript("var "+Y[0]);for(var $;Y.length&&($=Y.shift());)Y.length||void 0===X?Z=Z[$]?Z[$]:Z[$]={}:Z[$]=X;