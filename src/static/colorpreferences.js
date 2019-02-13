/* https://www.w3schools.com/html/html5_webstorage.asp */
/*jslint browser */
/*global console */

function loadBgColor() {
    // loadBgColor run on the main front page
    // Uses the stored bgColor or white
    "use strict";
    // Some helpers
    var isAlpha = function (str) {
        // because security
        // https://stackoverflow.com/questions/2450641/validating-alphabetic-only-string-in-javascript
        return /^[a-zA-Z]+$/.test(str);
    };
    var isHex = function (str) {
        // because security
        // https://stackoverflow.com/questions/8027423/how-to-check-if-a-string-is-a-valid-hex-color-representation/8027444
        return /^#[0-9A-F]{6}$/.test(str);
    }
    var isMenu = function (str) {
        return /menu$/.test(str);
    }

    if (Storage === undefined) {
        console.log("browser does not support Web Storage for bgColor either..");
    } else {
        var localbgcolor = localStorage.bgcolor;
        var isitAlpha = isAlpha(localbgcolor);
        var isitHex = isHex(localbgcolor);
        var isitMenu = isMenu(window.location.href);
           if (isitHex || isitAlpha){
               // example how to only adjust one div with id "content"
	       // document.getElementById("content").style.backgroundColor = localbgcolor;
	       document.body.style.backgroundColor = localbgcolor;
	       if (isitMenu){
	           document.getElementById('wrapper').style.backgroundColor = localbgcolor;
	       }
           }

    }

}

function saveBgColor(color) {
    // saveBgColor we call via an onClick in the /menu
    "use strict";
    if (Storage !== undefined) {
        localStorage.bgcolor = color.toUpperCase();
    }

}
