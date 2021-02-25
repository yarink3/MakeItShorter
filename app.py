from flask import Flask, render_template , request, redirect, jsonify,url_for
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
Urls_tbl = db.collection('Urls')
# urls_docs = Urls_tbl.where(u'ShortUrl', u'==', "localhost:5000/ya7").stream()
# for doc in urls_docs:
#     print(f'{doc.id} => {doc.to_dict()}')

# urls_docs = Urls_tbl.stream()
# for url in urls_docs:
#     url_dict=f'{url.id} => {url.to_dict()}'
#     print(url_dict)

Redirections_tbl = db.collection('Redirections')


# data = {
#     u'LongUrl': u'LongEx',
#     u'ShortUrl': u'ShortEx'
# }
# Urls_tbl.document(u'ex'+str(1)).set(data)

General_tbl = db.collection('General')
info_ref = General_tbl.document(u'info')


def create_info_collection():
    info_doc = info_ref.get()
    if(info_doc.exists==False):
        data = {
        u"SITE_PREFIX" : "shorter-url1.herokuapp.com/",
        u"numOfUrls" : 0,
        u"redirectionsSoFar": 0,
        u"True_Redirects" : 0 , 
        u"False_Redirects" : 0 , 

        }
        General_tbl.document(u'info').set(data)


app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"
    short_Url=""
    pre=""
    return render_template('index.html',prefix=pre,short_Url=short_Url)

def get_url_or_None(urls_docs,URL_ENTERED):
    print(URL_ENTERED)
    for url in urls_docs: # the url already shrinked, return the shrinked one.
        url_dict=url.to_dict()
        if(url_dict['LongUrl']==URL_ENTERED):# the url already shrinked, return the shrinked one.
            return url_dict['ShortUrl']

    return None

# @app.route('/<shortOne>')
def findPathInDb(shortOne):
    info = info_ref.get()
    info_dict= info.to_dict()
    # global now
    # global Redirections_tbl
    now=datetime.datetime.now()
    # global numOfUrls
    True_Redirects=info_dict['True_Redirects']
    False_Redirects=info_dict['False_Redirects']
    SITE_PREFIX=info_dict['SITE_PREFIX']

    shortOne=SITE_PREFIX+shortOne
    urls_docs = Urls_tbl.where(u'ShortUrl', u'==', shortOne)
    print(urls_docs)
    # doc_reffer = db.collection(u'test').where(u'adminEmail', u'==', 'x@x.com')
    urls_docs = [short for short in urls_docs.stream()]
    print(type(urls_docs))
    redirect_to=None
    id=-1
    for url in urls_docs: # the url already shrinked, return the shrinked one.
        url_dict=url.to_dict()
        redirect_to=url_dict['LongUrl']
        id=url.id

    if(redirect_to == None):
        
        False_Redirects += 1
        info_dict['False_Redirects']=False_Redirects
        General_tbl.document(u'info').set(info_dict)
        # return redirect(info_dict['SITE_PREFIX'])
        return redirect(url_for('.index'))

    else:

       for url in urls_docs: # the url already shrinked, return the shrinked one.
        url_dict=url.to_dict() 
        # url_dict=urls_docs.to_dict()
        
        ShortUrl=url_dict['ShortUrl']
        
        True_Redirects += 1
        info_dict['True_Redirects']=True_Redirects
        General_tbl.document(u'info').set(info_dict)

        data = {
                u'UrlId' :id ,
                u'LongUrl': redirect_to,
                u'ShortUrl': ShortUrl,
                u'year': now.year,
                u'month': now.month,
                u'day': now.day,
                u'hour': now.hour,
                u'minute': now.minute,
                u'correctly': True,
            }
        Redirections_tbl.document(u'Redirection'+str(True_Redirects)).set(data)
        
        return redirect(redirect_to)






# @app.route('/stats')
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
                           True_Redirects=True_Redirects)



# @app.route('/handle_form', methods=['POST'])
def handle_form():
    # _conn = sqlite3.connect('urls1.db')  # connect to the database
    # cur = _conn.cursor()
    info = info_ref.get()
    info_dict= info.to_dict()
    URL_ENTERED=request.form['urlEntered']
    numOfUrls=info_dict['numOfUrls']

    # urls_docs = Urls_tbl.stream()
    urls_docs = Urls_tbl.where(u'LongUrl', u'==', URL_ENTERED).stream()
    url=get_url_or_None(urls_docs,URL_ENTERED)
    if(url!=None):
        urlToReturn=url

    else:  # lets add the long url to the db and return the new short one
            # global numOfUrls
            numOfUrls += 1
            info_dict['numOfUrls']=numOfUrls
            General_tbl.document(u'info').set(info_dict)
            urlToReturn = info_dict['SITE_PREFIX']+"ya" + str(numOfUrls)
            data = {
                u'LongUrl': URL_ENTERED,
                u'ShortUrl': urlToReturn
            }
            Urls_tbl.document(u'Url'+str(numOfUrls)).set(data)


    pre="Short URL for the one you entered: "

    return render_template('index.html',prefix=pre,short_Url=urlToReturn)


if __name__ == '__main__':
#     createTable()
    create_info_collection()
    app.run()
