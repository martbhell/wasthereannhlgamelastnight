/* https://www.w3schools.com/html/html5_webstorage.asp */
/*jslint browser */
/*global argdate, argteam, console */

function loadTeam() {
    // loadTeam we run on the main front page
    "use strict";
    // Some helpers
    var isAlpha = function (str) {
	// because security
        // https://stackoverflow.com/questions/2450641/validating-alphabetic-only-string-in-javascript
        return /^[a-zA-Z]+$/.test(str);
    };
    // strnew is a function to return "/DET" from strnew("DET")
    // https://stackoverflow.com/questions/41117799/string-interpolation-on-variable
    var strnew = function (str) {
        return `/${str}`;
    };
    ///////
    if (Storage === undefined) {
        console.log("browser does not support Web Storage");
    } else {
        if (!localStorage.team) {
            console.log("no team found in Web Storage, choose your team in the menu!");
        } else {
        /* If we detect no arguments we use the team from localStorage, and only when alphabetical*/
            var localstorageteam = localStorage.team;
	    var isittrue = isAlpha(localstorageteam);
            if (argdate === "None") {
                if (argteam === "None") {
                    if (isittrue) {
                        location.replace(strnew(localstorageteam));
                    }
                }
            }
        }
    }
}

function saveTeam(myteam) {
    // saveTeam we call via an onClick in the /menu
    "use strict";
    if (Storage !== undefined) {
        localStorage.team = myteam;
    }

}
