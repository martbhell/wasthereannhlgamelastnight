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

*Chosing a team means you only get YES if that team played last night.*

Why?
====

So I live in a timezone where the NHL games are often over at 5am in the morning. I tend to watch replays. I'm not always sure if there was a game last night. Schedules often have the results too. I tend to not want to know the results if I intend to watch the replay. It would be really nice if I could just browse to $URL/team and it would tell me if my team played last night or during stanley cup $URL would be enough.

How?
====

Getting the playoff list is manual (for now):

 - Visit http://www.nhl.com/ice/schedulebyseason.htm
 - Click on print
 - Print as pdf
 - pdftotext
 - Alter the python script to point to the new file and print what you want (only the dates).


How to make this work per team and regular season?
==================================================
TBA

Source
======

Forked from https://github.com/amanjeev/isitfridaythe13th because it had the google appspot already in it and python :) Thanks!

wasthereannhlgamelastnight(..) has been re-written a few times - it's no longer even close to the isitfridaythe13th - it now uses webapp2 for example instead of python print to stdout.
