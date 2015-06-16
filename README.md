wasthereannhlgamelastnight
==========================

Usage
=====

case insensitive:  

 * http://wasthereannhlgamelastnight.appspot.com
 * http://wasthereannhlgamelastnight.appspot.com/det
 * http://wasthereannhlgamelastnight.appspot.com/redwings
 * http://wasthereannhlgamelastnight.appspot.com/nyrangers
 * http://wasthereannhlgamelastnight.appspot.com/tampabay
 * http://wasthereannhlgamelastnight.appspot.com/newyorkrangers

*Choosing a team means you only get YES if that team played last night.*

Why?
====

So I(author) live in a timezone where the NHL games are often over at 5am in the morning, sometimes they start then. I tend to watch replays. I'm not always sure if there was a game last night. Schedules often have the results too. I tend to not want to know the results if I intend to watch the replay. It would be really nice if I could just browse to $URL/team and it would tell me if my team played last night or during Stanley Cup $URL would be enough to just tell me if there was a game at all. Actually that could be handy for regular season too but I guess it's quite often at least one game on.

How to update the schedule inside the scripts?
====

Updating the playoff list in wasthereannhlgamelastnight.py is done by:

 - Visit http://www.nhl.com/ice/schedulebyseason.htm and make sure it has the games
 - Run ./parser/parse_nhl_schedule.py
 - Confirm that it doesn't output garbage :)
 - This outputs dictionaries that you can paste into wasthereannhlgamelastnight.py

What about regular season and playoffs?
==================================================

Currently the script doesn't differentiate between playoffs and regular seasons.

It just takes the dates from http://www.nhl.com/ice/schedulebyseason.htm

Source
======

Forked from https://github.com/amanjeev/isitfridaythe13th because it had the google appspot already in it and python :) Thanks!

wasthereannhlgamelastnight(..) has been re-written a few times - it's no longer even close to the isitfridaythe13th - it now uses webapp2 for example instead of python print to stdout.
