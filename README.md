wasthereannhlgameyesterday?
==========================

**W**as**T**here**A**n**N**hl**G**ame**Y**esterday?

[![Build Status](https://travis-ci.org/martbhell/wasthereannhlgamelastnight.svg?branch=master)](https://travis-ci.org/martbhell/wasthereannhlgamelastnight)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Twitter](https://camo.githubusercontent.com/7cf10772eb6ccebe92d678c452a971e6e2778653/687474703a2f2f692e696d6775722e636f6d2f7458536f5468462e706e67)](https://twitter.com/wtangy_app)

Print YES or NO!

<a href="https://wtangy.se"><img src="wtangy_front.png"></a>
<a href="https://wtangy.se/menu"><img src="wtangy_menu.png"></a>

Usage
=====

|endpoint | function | format | example | admin |
|----------|--------|-------|---------------|-------------|
|/$TEAM| YES/NO | HTML* | RedWings | |
|/$CITYTEAM| YES/NO | HTML* |DetroitRedWings | |
|/$CITY| YES/NO |HTML* | Detroit | |
|/$SHORT| YES/NO |HTML* | DET | |
|/$DATE/$TEAM | YES/NO | HTML*| 20171022/RedWings| |
|/$TEAM/$DATE | YES/NO | HTML*| RedWings/20171111| |
|/get_schedule | Print Schedule| JSON | | |
|/version | Print Schedule Update Time| JSON/ISODATE | { "version": "2018-01-27T08:57:00.372800" } | |
|/menu | Present user with a clickable menu | HTML | | |
|/update_schedule | Update Schedule | | 202 on changed | Y |

\*  If you use Curl, Wget or Python-Urllib then all you get is YES or NO

<img src="demo.gif" title="made with asciinema and the docker asciicast2gif docker - note to self: just add .gif to the asciinema recording to get the docker oneliner">

Examples
----------

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

What do these mean?

 * *Not choosing anything just tells you if there was a game yesterday*
 * *Choosing a team means you only get YES if that team played yesterday.*
 * *Choosing a date means you only get YES if there is a game on _that_ date.*
 * *Choosing a team and a date you only get YES if the chosen team plays/played on that date.*
 * *Choosing a team incorrectly and a date correctly you only get YES if there was/is a game on that date*

There's also:

 * https://wtangy.se/menu # select a team
 * https://wtangy.se/get_schedule # get the schedule this website uses in JSON
 * https://wtangy.se/update_schedule # for admins only
 * https://wtangy.se/version # tells when the backend schedule was last updated

Features
========

 * Persistent team selection using HTML5 Web Storage. If you choose a team in the menu and you later revisit https://wtangy.se (from the same browser) you'll see the result for that team.
 * This works with the new NHL.com website (2017-)

Why?
====

So I(author) live in a timezone where the NHL games are often over at 5am in the morning, sometimes they start then. I tend to watch replays. I'm not always sure if there was a game yesterday. Schedules online often have the results, news or "yes, also it went to overtime" to spoil the game.

It would be really nice if I could just browse to $URL/team and it would tell me if my team played yesterday or during Stanley Cup (or regular season) $URL would be enough to just tell me if there was a game at all.

Now there is! :)

How to update the schedule inside the scripts?
====

The schedule used by this web site is stored in the backend.

As an admin you can update it manually or configure a <a href="gcloud.md">cronjob</a>. It will send an e-mail with schedule changes outside playoffs.

What about regular season and playoffs?
==================================================

It also worked for 2020-21 playoffs :)

Currently the script doesn't differentiate between playoffs and regular seasons.

It just takes the dates from NHL.com's <a href="https://statsapi.web.nhl.com/api/v1/schedule?startDate=2017-10-04&endDate=2017-10-22">API</a>. There are more arguments to this API that I have not found any documentation for. Here's one result from google searches:
<pre>
https://statsapi.web.nhl.com/api/v1/schedule/startDate=2016-01-31&endDate=2016-02-05?expand=schedule.teams,schedule.linescore,schedule.broadcasts,schedule.ticket,schedule.game.content.media.epg&leaderCategories=&site=en_nhl&teamId=&
</pre>

TODO / Known issues
====================

 * "BadRequestError: Admin message exceeds size limits" in update_schedule when there's a huge update
    * This is made so that if the size of the message body is too large we don't send it. One could perhaps email it as an attachment instead...
 * Choosing background color - would be sweet if it could do HTML5 so users can choose themselves too like in https://www.w3schools.com/colors/colors_picker.asp
 * games include preseason - if this is a problem let me know!
 * add a calendar selection too near the menu?
 * an app!
    * Started on this in https://github.com/martbhell/webview/tree/new_icon
    * Needs a better new icon, better resolution on the phones and I want it to display the URL somewhere
 * proper logging
    * Don't print to stdout - https://cloud.google.com/appengine/docs/standard/python/logs/#Python_writing_application_logs
    * We no longer print to stdout, so some imports could be removed?
    * could be nice if one could get debug errors to the browser console, rather than having to run the local app_devserver
    * Right now there's a few in the cloud console logs. More could be added
 * dynamically generate a sitemap.xml
 * Réal Names of cities:
   * querying Montréal Canadiens (so with the acute accent) is not currently working. Before https://github.com/martbhell/wasthereannhlgamelastnight/issues/9 MTL did not work at all
   * querying St. Louis Blues (so with the .) is not currently working. Without the dot and spaces work.
   * Ideally we would use the real names and not remove bad chars in the schedule ( in update_schedule.py )
 * improve testing
   * assert that we are redirected to update_schedule
   * update schedule_testing and then verify it / validate json
   * performance testing
   * lint javascript,css,html

Source
======

<a href="gcloud.md">gcloud</a> - reminders for myself.

Forked from https://github.com/amanjeev/isitfridaythe13th because it had the google appspot already in it and python :) Thanks!

wasthereannhlgamelastnight(..) has been re-written a few times - it's no longer even close to the isitfridaythe13th, for example:
 - it now uses webapp2 for example instead of python print to stdout.
 - it used to have a manual NHL_schedule.py with a set and a list, now it reads and writes to gcloud object store!
