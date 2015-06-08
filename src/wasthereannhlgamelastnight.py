import webapp2
import os
import datetime

class MainPage(webapp2.RequestHandler):
    def get(self):
        """Return a friendly HTTP greeting."""
        #data = cmdline("grep 'VISITING TEAM' -B 20 -m 1 NHL.2014-2015.Playoffs.txt|grep 2015|grep -v PLAYOFF")
        #lines = data.split('\n')
        lines = ['Sat Jun 6, 2015', 'Mon Jun 8, 2015', 'Wed Jun 10, 2015', 'Sat Jun 13, 2015', 'Mon Jun 15, 2015', 'Wed Jun 17, 2015', '']
        now = datetime.datetime.now().strftime("%a %b %-d, %Y")
        now2 = datetime.datetime.now()
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime("%a %b %-d, %Y")

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<!DOCTYPE html>\n\
        <html lang ="en">\n\
        <head><title>Was there an NHL game last night?</title></head>\n\
        <body style="text-align: center; padding-top: 200px;">\n\
            <div class="content" style="font-weight: bold; font-size: 220px; font-family: Arial,sans-serif; text-decoration: none; color: black;">\n')

        for game in lines:
            if yesterday == game:
                self.response.write("YES")
                break
            else:
                self.response.write("NO")
                break

        self.response.write('<div class="disclaimer" style="font-size:10px; ">')
        self.response.write(now2)
        self.response.write('<!--')
        self.response.write(self.request.url)
        self.response.write('-->')
        self.response.write('</div>\n')
        self.response.write('<!-- NHL.com is the official web site of the National Hockey League. NHL, the NHL Shield, the word mark and image of the Stanley Cup, Center Ice name and logo, NHL Conference logos are registered trademarks. All NHL logos and marks and NHL team logos and marks depicted herein are the property of the NHL and the respective teams. This website is not affiliated with NHL. -->\n')
        self.response.write('</div></body></html>')



def handle_404(request, response, exception):
    """Return a custom 404 error."""
    response.write('Sorry, nothing at this URL.')
    response.set_status(404)


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
application.error_handlers[404] = handle_404
