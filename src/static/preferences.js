/* https://www.w3schools.com/html/html5_webstorage.asp */
/*jslint browser */
/*global argdate, argteam, console */

function loadTeam() {
    // loadTeam we run on the main front page
    "use strict";
    if (Storage === undefined) {
        console.log("browser does not support Web Storage");
    } else {
        if (!localStorage.team) {
            console.log("no team found in Web Storage, choose your team in the menu!");
        } else {
        /* If we detect no arguments we use the team from localStorage  */
            if (argdate === "None") {
                if (argteam === "None") {
                    // console.log(localStorage.team);
                    // strnew is a function to return "/DET" from strnew("DET")
                    // https://stackoverflow.com/questions/41117799/string-interpolation-on-variable
                    var strnew = function (str) {
                        return `/${str}`;
                    };
                    // console.log(strnew(localStorage.team));
                    location.replace(strnew(localStorage.team));
                }
            }
        }
    }
}

function saveTeam(myteam) {
    // saveTeam we call via an onClick in the /menu
    "use strict";
    if (typeof(Storage) !== "undefined") {
        localStorage.team = myteam;
    }

}
