wasthereannhlgamelastnight
==========================

This works with the new NHL.com website (2017-2018)

Usage
=====

case insensitive:  

 * https://wtangy.se
 * https://wtangy.se/det
 * https://wtangy.se/redwings
 * https://wtangy.se/nyrangers
 * https://wtangy.se/Vgk
 * https://wtangy.se/newyorkrangers
 * https://wtangy.se/20171222
 * https://wtangy.se/22-12-2017
 * https://wtangy.se/22-12-2017/DET
 * https://wtangy.se/lak/20171014
 * https://wtangy.se/foo/20171014
 * https://wtangy.se/foo/20170901

What does this mean?

 * *Not choosing anything just tells you if there was a game yesterday*
 * *Choosing a team means you only get YES if that team played yesterday.*
 * *Choosing a date means you only get YES if there is a game on _that_ date.*
 * *Choosing a team and a date you only get YES if the chosen team plays/played on that date.*
 * *Choosing a team incorrectly and a date correctly you only get YES if there was/is a game on that date*

Why?
====

So I(author) live in a timezone where the NHL games are often over at 5am in the morning, sometimes they start then. I tend to watch replays. I'm not always sure if there was a game yesterday. Schedules online often have the results, news or "yes it went to overtime" to spoil the game.

It would be really nice if I could just browse to $URL/team and it would tell me if my team played yesterday or during Stanley Cup (or regular season) $URL would be enough to just tell me if there was a game at all.

Now there is! :)

How to update the schedule inside the scripts?
====

Updating the playoff list in wasthereannhlgamelastnight.py is done by:

 - Adding cron.yaml to <a href="gcloud.md">gcloud</a>

What about regular season and playoffs?
==================================================

Currently the script doesn't differentiate between playoffs and regular seasons.

It just takes the dates from NHL.com's API which can be accessed on https://statsapi.web.nhl.com/api/v1/schedule?startDate=2017-10-04&endDate=2018-04-09 - now there are more arguments to this API that I have not found any documentation for. Here's another example: 
<pre>
https://www.google.fi/url?sa=t&rct=j&q=&esrc=s&source=web&cd=7&cad=rja&uact=8&ved=0ahUKEwidtqvvn9fWAhWlApoKHd_VBVUQFghJMAY&url=https%3A%2F%2Fstatsapi.web.nhl.com%2Fapi%2Fv1%2Fschedule%3FstartDate%3D2016-01-31%26endDate%3D2016-02-05%26expand%3Dschedule.teams%2Cschedule.linescore%2Cschedule.broadcasts%2Cschedule.ticket%2Cschedule.game.content.media.epg%26leaderCategories%3D%26site%3Den_nhl%26teamId%3D&usg=AOvVaw293oxkI9Kgt_VuxY0dLmjf 
</pre>

TODO / Known issues
====================

 * flowchart for parameters? =)
 * games include preseason - if this is a problem let me know!
 * could be nice if one could get debug errors to the browser console, rather than having to run the local app_devserver
 * dynamically generate a sitemap.xml
 * Would be cool to not have \n all over the python and still get the HTML page readable

Source
======

<a href="gcloud.md">gcloud</a> - reminders for myself.

Forked from https://github.com/amanjeev/isitfridaythe13th because it had the google appspot already in it and python :) Thanks!

wasthereannhlgamelastnight(..) has been re-written a few times - it's no longer even close to the isitfridaythe13th, for example:
 - it now uses webapp2 for example instead of python print to stdout.
 - it used to have a manual NHL_schedule.py with a set and a list, now it reads and writes to gcloud object store!
