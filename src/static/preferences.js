/* https://www.w3schools.com/html/html5_webstorage.asp */
function loadTeam() {
	// loadTeam we run on the main front page
	if (typeof(Storage) !== "undefined") {
		if(!localStorage.team) {
			console.log("no team found in Web Storage, choose your team in the menu!");
		} else {
			/* If we detect no arguments we use the team from localStorage  */
			if (argdate == "None") {
				if (argteam == "None") {
					var localstorageteam = localStorage.team;
					// console.log(localstorageteam);
					// strnew is a custom function to return /$team
					// https://stackoverflow.com/questions/41117799/string-interpolation-on-variable
					var strnew = function(str){ return `/${str}`; };
					// console.log(strnew(localStorage.team));
					window.location.replace(strnew(localStorage.team));
				}
			}
		}
	} else {
		console.log("browser does not support Web Storage");

	}

}

function saveTeam(myteam) {
	// saveTeam we call via an onClick in the /menu
	if (typeof(Storage) !== "undefined") { localStorage.team = myteam; }

}
