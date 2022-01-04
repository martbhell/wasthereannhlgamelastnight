from flask import request
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def root():
    
    agent=request.headers.get('User-Agent')
    try:
        short_agent=agent.split("/")[0]
    except:
        short_agent=agent
    yesorno="YES"

    if short_agent in CLIAGENTS:
        return render_template('cli.html', yesorno=yesorno, agent=agent)
    else:
        return render_template('index.html', yesorno=yesorno, agent=agent)

@app.route('/update_schedule')
def update_schedule():

    return render_template('update_schedule.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

CLIAGENTS = ["curl", "Wget", "Python-urllib"]
