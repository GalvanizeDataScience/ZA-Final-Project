# web stuff
from flask import Flask, url_for, request, json, render_template

app = Flask(__name__)

@app.route('/')
def show():
    return render_template('index.html', myjson = x )

if __name__ == '__main__':

    #TODO


    # check for which user screen name pickles have been created
    # this should be passed to the flask app as a list

    x = json.load(open('data/data.json', 'r'))
    app.run(debug=True)
