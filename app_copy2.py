from flask import Flask, render_template , request, redirect
import datetime
import sqlite3

_conn = sqlite3.connect('urls1.db')  # connect to the database
cur = _conn.cursor()

def createTable():
    with _conn:
        cur=_conn.cursor()
        cur.executescript("""
       CREATE TABLE urlTable (
        id                      INTEGER         PRIMARY KEY,
        long_url                TEXT            NOT NULL,
        short_url               TEXT            NOT NULL );
        
       CREATE TABLE redirections (
        id                      INTEGER         REFERENCES urlTable(id),
        long_url                TEXT            NOT NULL,
        short_url               TEXT            NOT NULL,
        year                    INTEGER         NOT NULL,          
        month                   INTEGER         NOT NULL,
        day                     INTEGER         NOT NULL,
        hour                    INTEGER         NOT NULL,
        minute                  INTEGER         NOT NULL,    
        correctly               TEXT            NOT NULL
            );
        """)

app = Flask(__name__)

numOfUrls = 0
redirectionsSoFar=0
numOfWrongRedirections=0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<shortOne>')
def findPathInDb(shortOne):
     global now
     now=datetime.datetime.now()
     global numOfUrls
     global numOfWrongRedirections

     _conn = sqlite3.connect('urls1.db')  # connect to the database
     cur = _conn.cursor()

     cur.execute("SELECT * FROM urlTable WHERE short_url = (?)", (shortOne,))
     urlTuple = cur.fetchone()
     if(urlTuple==None):
         numOfWrongRedirections+=1
         cur.execute(""" INSERT INTO redirections(id, long_url, short_url,year,month,day,hour,minute,correctly)
                                       VALUES(?,?,?,?,?,?,?,?,?) """,
                         [numOfUrls, urlTuple[1], urlTuple[2], now.year, now.month, now.day, now.hour, now.minute,"no"])

     else: #(urlTuple!=None):
        cur.execute(""" INSERT INTO redirections(id, long_url, short_url,year,month,day,hour,minute,correctly)
                          VALUES(?,?,?,?,?,?,?,?,?) """, [numOfUrls, urlTuple[1],urlTuple[2],now.year,now.month,now.day,now.hour,now.minute,"yes"])
        return redirect(urlTuple[1]) # if the path that the client entered is in the db, it will redirect to the long url tht belong to it.





@app.route('/stats')
def stats():
    _conn = sqlite3.connect('urls1.db')  # connect to the database
    cur = _conn.cursor()
    global redirectionsSoFar
    global now
    now = datetime.datetime.now()

    cur.execute("COUNT (*) FROM redirections WHERE year = (?) AND month = (?) AND day = (?) ",
                (now.year, now.month, now.day))
    result = cur.fetchone()
    redirectionsLastDay = result[0]

    cur.execute("COUNT (*) FROM redirections WHERE year = (?) AND month = (?) AND day = (?) AND hour = (?)  ",
                (now.year, now.month, now.day, now.hour))
    result = cur.fetchone()
    redirectionsLastHour = result[0]

    cur.execute(
        "COUNT (*) FROM redirections WHERE year = (?) AND month = (?) AND day = (?) AND hour = (?) AND minute = (?) ",
        (now.year, now.month, now.day, now.hour, now.minute))
    result = cur.fetchone()
    redirectionsLastMin = result[0]

    return render_template('stats.html', redirectionsSoFar=redirectionsSoFar, redirectionsLastMin=redirectionsLastMin,
                           redirectionsLastHour=redirectionsLastHour, redirectionsLastDay=redirectionsLastDay,
                           numOfWrongRedirections=numOfWrongRedirections)


@app.route('/handle_form', methods=['POST'])
def handle_form():
    _conn = sqlite3.connect('urls1.db')  # connect to the database
    cur = _conn.cursor()
    entered=request.form['urlEntered']

    urlToReturn = "localhost:5000/"

    cur.execute("SELECT * FROM urlTable WHERE long_url = (?)", (entered,))

    urlTuple = cur.fetchone()

    if (urlTuple != None):  # the url already shrinked, return the shrinked one.
        urlToReturn += str(urlTuple[2])

    else:  # lets add the long url to the db and return the new short one

        global numOfUrls
        numOfUrls += 1
        cur.execute(""" INSERT INTO urlTable(id, long_url, short_url)
              VALUES(?,?,?) """, [numOfUrls, entered, "ya" + str(numOfUrls)])

        _conn.commit()
        urlToReturn += "ya" + str(numOfUrls)

    return render_template('index.html',short_Url=urlToReturn)


if __name__ == '__main__':
    createTable()
    app.run()
