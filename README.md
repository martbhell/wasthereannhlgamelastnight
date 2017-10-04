wasthereannhlgamelastnight
==========================

This works with the new NHL.com website (2017-2018)

Usage
=====

case insensitive:  

 * http://wasthereannhlgamelastnight.appspot.com
 * http://wasthereannhlgamelastnight.appspot.com/det
 * http://wasthereannhlgamelastnight.appspot.com/redwings
 * http://wasthereannhlgamelastnight.appspot.com/nyrangers
 * http://wasthereannhlgamelastnight.appspot.com/Vgk
 * http://wasthereannhlgamelastnight.appspot.com/newyorkrangers
 * http://wasthereannhlgamelastnight.appspot.com/20171222
 * http://wasthereannhlgamelastnight.appspot.com/22-12-2017
 * http://wasthereannhlgamelastnight.appspot.com/22-12-2017?team=DET

What does this mean?

 * *Not choosing anything just tells you if there was a game last night*
 * *Choosing a team means you only get YES if that team played last night.*
 * *Choosing a date means you only get YES if there is a game on _that_ date.*
 * *Choosing a team and a date doesn't work currently*

Why?
====

So I(author) live in a timezone where the NHL games are often over at 5am in the morning, sometimes they start then. I tend to watch replays. I'm not always sure if there was a game last night. Schedules online often have the results, news or "yes it went to overtime" to spoil the game.

It would be really nice if I could just browse to $URL/team and it would tell me if my team played last night or during Stanley Cup (or regular season) $URL would be enough to just tell me if there was a game at all.

Now there is! :)

How to update the schedule inside the scripts?
====

Updating the playoff list in wasthereannhlgamelastnight.py is done by:

 - Run ./parser/parse_nhl_schedule_json.py
 - Confirm that it doesn't output garbage :)
 - This outputs a list and a dictionary that you put in NHL_schedule.py
 - Then run gcloud commands to update your app

What about regular season and playoffs?
==================================================

Currently the script doesn't differentiate between playoffs and regular seasons.

It just takes the dates from NHL.com's API

TODO / Known issues
====================

 * choosing a date and team doesn't work currently
 * the schedule (which is a file in this repo) is updated by me, would be cool if it was done periodically and automagically in the gcloud

Source
======

Forked from https://github.com/amanjeev/isitfridaythe13th because it had the google appspot already in it and python :) Thanks!

wasthereannhlgamelastnight(..) has been re-written a few times - it's no longer even close to the isitfridaythe13th - it now uses webapp2 for example instead of python print to stdout.
