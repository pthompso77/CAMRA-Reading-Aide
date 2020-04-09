"""
Main page for Marca app (index)
"""

import logging as log
log.basicConfig(filename='marcaBP.log', level=log.DEBUG, format='%(asctime)s %(message)s')
log.info('Starting marcaBP.py')

from marca.text_tools.FullText import FullText

log.info('Starting imports in marcaBP.py')
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for
)
from werkzeug.exceptions import abort
'''example:
abort(404)  # 404 Not Found
abort(Response('Hello World'))
'''

log.info('Starting importing auth.login_required and db.get_db in marcaBP.py')
try:
    from auth import login_required
    from db import get_db, escape
except:
    try:
        from marca.auth import login_required
        from marca.db import get_db
    except Exception as e:
        log.error("Error importing login_required or get_db:", e)


#: Initialize Blueprint
log.info('Initializing Blueprint in marcaBP.py')
bp = Blueprint('marcaBP', __name__)


'''=======================Variables======================='''

# HTTP request methods
GET = 'GET'
POST = 'POST'
# HTTP codes
http_notFound = 404
http_forbidden = 403


@bp.route('/dev/db', methods=(GET, POST))
def devDB():

    if g.user['userID'] != 29: #then the user isn't me and shouldn't see this page
        return redirect(url_for('index'))

    log.info('Starting def devDB()')
    db = get_db().connect()
    cur = db.cursor()

    if request.method==POST:
        query = request.form['query']
        #query = db.escape(query)
        DBexec = cur.execute(query)
        db.commit()
        DBresult = cur.fetchall()

        return render_template('dev/db.html',query=query, DBexec=DBexec, DBresult=DBresult)

    log.info('Finished def devDB()')
    return render_template('dev/db.html')


'''=============================INDEX VIEW============================='''

# Database table names
fullTextTable = 'FullText'
userTable = 'userAccounts'


@bp.route('/')
def index():
    log.info('Starting def index()')
    #db = get_db().connect()
    #cur = db.cursor()

    # TODO -

    log.info('Finished def index()')
    return render_template('summary/index.html')


'''=============================DASHBOARD VIEW============================='''


@bp.route('/dashboard', methods=(GET, POST))
@login_required
def dashboard():
    # TODO
    #: get userAccountsID from g.user
    userAccountsID = g.user['userID']
    error = None


    ''' (as a logged-in user)
        Submit a new text document that will be uploaded to DB and available
        to review and interact with.

    request form name = newFullText
    '''
    #if method is POST
    if request.method == POST:
        # Get the text form submitted
        fullText = request.form['newFullText']
        #: remove apostrophe
        fullText = request.form['newFullText'].replace("'","`")
        title = request.form['textTitle']
        if title == "":
            title = "Untitled"


        textobject = FullText(fullText, title=title)
        FullText.submitToDB(textobject, userAccountsID)

        flash('Document Uploaded Successfully')
        if userAccountsID == 29: # (then it's me testing)
            flash('Got Text:',textobject)


    # continues if POST, jumps here if GET

    #: select texts from DB that match user
    userTexts = getTextAssociatedWithUserID(userAccountsID)


    #: render the dashboard template, send the user Texts also
    return render_template('summary/dashboard.html', userTexts=userTexts)

'''===========Dashboard helpers==========='''




def getTextAssociatedWithUserID(userAccountsID):
    # test response
    response = [{'email': 'me', 'FullText_ID': 42, 'title': 'Untitled', 'text_tokenized': "['New', 'Document', 'duh']", 'full_text': 'New Document duh'},
                {'email': 'me', 'FullText_ID': 43, 'title': '5 CONCLUSION', 'text_tokenized': "['The', 'media', 'landscape', 'has', 'experienced', 'a', 'massive', 'change', 'with', 'the', 'arrival', 'of', 'internet', 'and', 'the', 'recent', 'advent', 'of', 'Web', '3.0', 'and', 'has', 'influenced', ',', 'in', 'fact', ',', 'completely', 'changed', 'the', 'ways', 'in', 'which', 'information', 'communication', 'takes', 'place.', 'The', 'information', 'explosion', 'on', 'social', 'media', 'platforms', 'has', 'made', 'them', 'a', 'lot', 'more', 'engaging', 'than', 'stand', 'alone', 'communication', 'platforms', '[', '89', ']', '.', 'Social', 'media', 'platforms', 'are', 'utilized', 'for', 'discussions', 'surrounding', 'various', 'domains', 'including', 'healthcare', '[', '90', ']', ',', 'internet', 'of', 'things', '[', '91', ']', ',', 'politics', '[', '92', ']', ',', 'amongst', 'others.', 'In', 'the', 'current', 'scenario', ',', 'the', 'majority', 'of', 'people', 'get', 'to', 'know', 'about', 'recent', 'happenings', 'around', 'the', 'globe', 'through', 'social', 'media', 'platforms.', 'However', ',', 'the', 'content', 'being', 'shared', 'may', 'not', 'always', 'be', 'from', 'the', 'right', 'source', 'or', 'may', 'not', 'share', 'the', 'correct', 'information.', 'This', 'makes', 'these', 'platforms', 'vulnerable', 'to', 'propagation', 'of', 'misinformation.', 'Thus', ',', 'these', 'platforms', 'often', 'make', 'the', 'source', 'of', 'several', 'rumors', 'and', 'false', 'content.']", 'full_text': '\r\nThe media landscape has experienced a massive change with the arrival of internet and the recent advent of Web 3.0 and has influenced, in fact, completely changed the ways in which information communication takes place. The information explosion on social media platforms has made them a lot more engaging than stand alone communication platforms [89]. Social media platforms are utilized for discussions surrounding various domains including healthcare [90], internet of things [91], politics [92], amongst others. In the current scenario, the majority of people get to know about recent happenings around the globe through social media platforms. However, the content being shared may not always be from the right source or may not share the correct information. This makes these platforms vulnerable to propagation of misinformation. Thus, these platforms often make the source of several rumors and false content.'}
                ]
    db = get_db().connect()
    cur = db.cursor()

    query = f'''SELECT u.email, ft.FullText_ID, ft.title, ft.text_tokenized,
    ft.full_text FROM userAccounts u, pthompsoDB.FullText ft
    INNER JOIN pthompsoDB.user_FullText_assoc fta
    ON ft.FullText_ID = fta.FullTextID
    WHERE fta.userID = {userAccountsID} AND fta.userID = u.userID;
    '''
    #query = db.escape(query)
    cur.execute(query)
    response = cur.fetchall()
    return response


'''============================== REVIEW VIEW============================='''

@bp.route('/<int:textID>/review', methods=(GET, ))
@login_required
def review(textID):
    ''' Displays selected text for review:
    - Retrieves a FullText object from the database
    - sends the text object to the review template to fill:
        + First paragraph
            - with highlights highlighted
        + all other highlights in Navigation panel
            - with paragraph separators
        + First Highlight selected:
            - active-highlight span filled
            - notes filled (from DB)
            - rating filled (from DB)
    '''

    #- Retrieve a FullText object from the database
    textobject = FullText.getFullText_fromDB(textID)
    print("\n\n   GOT TEXTOBJECT:",textobject)
    #- send the text object to the review template to fill:
        #+ First paragraph
            #- with highlights highlighted
        #+ all other highlights in Navigation panel
            #- with paragraph separators
        #+ First Highlight selected:
            #- active-highlight span filled
            #- notes filled (from DB)
            #- rating filled (from DB)

        #TODO finish this

        # TODO: get more than just the text from DB, etc... (make a FullText object?)

    return render_template('summary/review.html',textID=textID, text=textobject.text, textobject=textobject)
    # (or return a redirect?)


'''===========Review helpers==========='''

def getTextByTextID(textID):
    # a test response
    response = {'FullText_ID': 40, 'title': 'Untitled', 'text_tokenized': "['Your', 'Saved', 'Documents', 'Your', 'Saved', 'Documents', 'Your', 'Saved', 'Documents']", 'full_text': 'Your Saved Documents Your Saved Documents Your Saved Documents'}

    db = get_db().connect()
    cur = db.cursor()

    query = f'''SELECT * FROM pthompsoDB.FullText WHERE FullText_ID = {textID};'''
    #query = db.escape(query)
    cur.execute(query)
    response = cur.fetchone()
    return response


'''=======================Actions======================='''


# TODO
@bp.route('/submitText', methods=(POST,))
def submitText():
    log.info('Starting submitText() in marcaBP.py')
    '''takes submitted text
        returns a summary
        name = userInput
    '''
    originalText = 'hey'
    originalText = request.form['userInput']


    # NEW: using FulLText object

    fullText = FullText(originalText)
    # put text in the database
    if g.user:
        userAccountsID = g.user['userID']
    else:
        userAccountsID = 29
    FullText_ID = FullText.submitToDB(fullText, userAccountsID)
    flash(FullText_ID)
    flash(fullText.db_ID)


    # OLD

    from marca.text_tools.extractive_summarizer import doArticleSummary
    summary = 'shorter...'
    summary, freq_table, sentences, sentence_scores, threshold = doArticleSummary(originalText, test_mode=True)


    '''Now for my_tokenize paragraph summary'''


    ts = len(summary)
    #: return redirect(?) to dashboard
    return render_template('dev/db.html', summary=summary, \
                           sentences=fullText.getSentences(), \
                           sentence_scores=sentence_scores, ft = freq_table)



# TODO
@bp.route('/<int:paragraphID>/<int:textID>/loadParagraph')
@login_required
def loadParagraph(paragraphID, textID):
    """ Retrieves FullText from DB that matches textID,
        retrieves the highlighted sections that appear in that paragraph,
        then returns the paragraph section matching paragraphID
        to display on the summary dashboard
    """

    #TODO

    return('TODO')







