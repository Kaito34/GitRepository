(function(){/*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
'use strict';var g=this||self;function h(a){if(a&&a!=g)return k(a.document);null===m&&(m=k(g.document));return m}var q=/^[\w+/_-]+[=]{0,2}$/,m=null;function k(a){return(a=a.querySelector&&a.querySelector("script[nonce]"))&&(a=a.nonce||a.getAttribute("nonce"))&&q.test(a)?a:""}function r(a){return a}
function t(a){var c=null,d=g.trustedTypes||g.TrustedTypes;if(!d||!d.createPolicy)return c;try{c=d.createPolicy(a,{createHTML:r,createScript:r,createScriptURL:r,createURL:r})}catch(e){g.console&&g.console.error(e.message)}return c}t("uf-api#base");var u;var w=t("uf-api#html");w&&w.createScript("");function x(a,c){this.h=a===y&&c||"";this.g=z}var z={},y={};w&&w.createHTML("<!DOCTYPE html>");w&&w.createHTML("");w&&w.createHTML("<br>");try{(new self.OffscreenCanvas(0,0)).getContext("2d")}catch(a){};function A(a){this.g=a||g.document||document};function B(a,c,d){a.timeOfStartCall=(new Date).getTime();var e=d||g,n=e.document,b=a.nonce||h(e);b&&!a.nonce&&(a.nonce=b);if("help"==a.flow){a:{var f=["document","location","href"];for(var l=e||g,v=0;v<f.length;v++)if(l=l[f[v]],null==l){f=null;break a}f=l}!a.helpCenterContext&&f&&(a.helpCenterContext=f.substring(0,1200));f=!0;c&&JSON&&JSON.stringify&&(l=JSON.stringify(c),(f=1200>=l.length)&&(a.psdJson=l));f||(c={invalidPsd:!0})}c=[a,c,d];e.GOOGLE_FEEDBACK_START_ARGUMENTS=c;d=a.serverUri||"//www.google.com/tools/feedback";
if(f=e.GOOGLE_FEEDBACK_START)f.apply(e,c);else{e=d+"/load.js?";for(var p in a)c=a[p],(d=null==c)||(d=typeof c,d="object"==d&&null!=c||"function"==d),d||(e+=encodeURIComponent(p)+"="+encodeURIComponent(c)+"&");a=(n?new A(9==n.nodeType?n:n.ownerDocument||n.document):u||(u=new A)).g;p="SCRIPT";"application/xhtml+xml"===a.contentType&&(p=p.toLowerCase());a=a.createElement(p);b&&a.setAttribute("nonce",b);b=e;b=w?w.createScriptURL(b):b;b=new x(y,b);b instanceof x&&b.constructor===x&&b.g===z?b=b.h:("object"!=
typeof b||!b||b instanceof Array||b instanceof Object||Object.prototype.toString.call(b),b="type_error:TrustedResourceUrl");a.src=b;(b=h())&&a.setAttribute("nonce",b);n.body.appendChild(a)}}var C=["userfeedback","api","startFeedback"],D=g;C[0]in D||"undefined"==typeof D.execScript||D.execScript("var "+C[0]);for(var E;C.length&&(E=C.shift());)C.length||void 0===B?D[E]&&D[E]!==Object.prototype[E]?D=D[E]:D=D[E]={}:D[E]=B;}).call(this);