#import all relevant packages
from flask import Flask, url_for, render_template, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
#look for a config file to associate with a db/port/ip/servername
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))
db = SQLAlchemy(app)
app.secret_key = 'submission' #allows message flashing, var not actually used

#create the quote table with all relevant columns
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitter = db.Column(db.String(80))
    quote = db.Column(db.String(200), unique=True)
    speaker = db.Column(db.String(50))
    quoteTime = db.Column(db.DateTime)

    #initialize a row for the Quote table
    def __init__(self, submitter, quote, speaker):
        self.quoteTime = datetime.now()
        self.submitter = submitter
        self.quote = quote
        self.speaker = speaker

#run the main page by creating the table(s) in the CSH serverspace and rendering the mainpage template
@app.route('/', methods=['GET'])
def main():
    db.create_all()
    return render_template('quotefaultmainpage.html')

#run when the form submission button is clicked
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        submitter = request.headers.get("x-webauth-user") #submitter will grab UN from webauth when linked to it
        quote = request.form['quoteString']
        speaker = request.form['nameString']
        # check for quote duplicate
        quoteCheck = Quote.query.filter(Quote.quote == quote).first()
        if quoteCheck is None:
            # create a row for the Quote table
            new_quote = Quote(submitter=submitter, quote=quote, speaker=speaker)
            db.session.add(new_quote)
            db.session.flush()
            # upload the quote
            db.session.commit()
            # create a message to flash for successful submission
            flash('Submission Successful!')
            # return something to complete submission
            return render_template('quotefaultmainpage.html'), 200
        else:
            flash('Quote already submitted!')
            return render_template('quotefaultmainpage.html'), 200

#display stored quotes
@app.route('/storage', methods=['GET'])
def get():
    quotes = Quote.query.all() #collect all quote rows in the Quote db
    #create a list to display on the templete using a formatted version of each row as individual items
    quote_lst = []
    for quote_obj in quotes:
        quote_lst.append(str(quote_obj.id) + " \"" + quote_obj.quote + "\" - " + quote_obj.speaker + ", submitted by " + quote_obj.submitter + " on " + str(quote_obj.quoteTime))
    return render_template('quotefaultstorage.html', quotes=quote_lst)