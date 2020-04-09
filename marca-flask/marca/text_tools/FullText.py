"""
created 2020-04-07
fleshing out the FullText object details
"""


"""
updated 2020-02-07 to follow the model I created
then again 2020-04-07 :-D

Create FullText object
    identify paragraph sections (new line or sentence max)
      store as a list of integer tuples, where the integers correspond to the index of the words that start and end the section, with exclusive upper bound.
        e.g. the first paragraph is identified as [0, 100) and contains 100 words; the second paragraph as [100,200), which  begins with the 101st word in the text
    Tokenize sentence sections
    Tokenize words by sentence
      store as list of integers (as above)

Summarize/Highlight
    (words are compared as stemmed and lowercase, original text is not modified)
    for each section selected for highlighting, store the range as integer tuple with exclusive upper bound: [0:12)
    Store in tables
        FullText
        Paragraph_Delims
        Sentence_Delims
        Highlight_Delims
after insert into database, get textID and store in FullText object

"""

from flask import flash

# full text reference (tokenized)
class FullText():
    ''' inputText must be a list of tokenized words from the original text,
    with the original formatting and punctuation

    '''
    def __init__(self, inputText, title='Untitled', FullText_ID=None):
        self.text = inputText
        self.title = title
        self.db_ID = FullText_ID
        self.owner = None
        self.paragraphList = getParagraphList(inputText)
        #store as a list of integer tuples, where the integers correspond to the index of the words that start and end the section, with exclusive upper bound.
            #e.g. the first paragraph is identified as [0, 100) and contains 100 words; the second paragraph as [100,200), which  begins with the 101st word in the text
        if FullText_ID is None:
            self.paragraphDelims = getDelims_Paragraph(self.paragraphList)
            # (currently, paragraph tokens start at the beginning of new lines, and sentences append whitepace to the end of tokens)
            #Tokenize sentence sections
            self.sentenceDelims = getDelims_Sentence(inputText)
            #Tokenize words by sentence
              #store as list of integers (as above)
            self.wordDelims = getDelims_Words(inputText)
            self.highlightDelims = self._getHightlightDelims()
        else:
            '''TODO?'''
            # retrieve delims from DB
            #like this?
            try:
                self = getFullText_fromDB(FullText_ID)
            except Exception as e:
                print('uh oh: ',e)


    def _getHightlightDelims(self):
        from marca.text_tools import extractive_summarizer as summr
        from marca.text_tools import my_tokenize as tokenizer
        wordList = tokenizer.word_tokenize_withDelims(self.text, self.wordDelims)
        #: creating a dictionary for the word frequency table
        freq_table = summr.create_frequency_table(self.text, wordList=wordList)
        #: tokenizing the sentences
        sentences = tokenizer.sent_tokenize_withDelims(self.text, self.sentenceDelims)
        #: find weighted frequencies of sentences
        sentence_scores = summr.find_weighted_frequencies(sentences, freq_table)
        #: getting the threshold
        threshold = summr.getThresholdUsingSentenceWeights(sentence_scores)
        #: summarize and return the highlighted section delimeters
        highlightDelims = summr.assembleSummary_withDelims(sentences, self.sentenceDelims, sentence_scores, 1.0 * threshold)

        return highlightDelims


    def getSentences(self):
        from marca.text_tools import my_tokenize as tokenizer
        return tokenizer.sent_tokenize_withDelims(self.text, self.sentenceDelims)


    def updateHighlightRating(highlightStart, rating):
        '''TODO'''
        return False


    def updateHighlightNotes(highlightStart, notes):
        '''TODO'''
        return False


    def getFullText_fromDB(FullText_ID):
        '''TODO'''
        from marca.db import get_db
        db = get_db().connect()
        cur = db.cursor()

        # create an obj
        textobject = FullText('''Social media platforms, specifically Twitter, experience several evidences of misinformation and disinformation in the form of rumors, conspiracies, and works of fiction in the current scenario. These stories have created substantial social and political unrest in recent times, which makes it pertinent to address them through policy-level interventions. These platforms are even flooded with memes citing fake stories and crime statistics designed to feed rightist conspiracy theories. Studies also explore the impact of non-verified information on critical events, like the outcome of the 2016 U.S. Presidential election [7]. Another popular event surrounding the Parkland shooting generated a host of hoax and disinformation theories. Several families of the victims were falsely accused and had to face social ostracism. Some doctored tweets even raised questions surrounding racism that led to social unrest.
        Academic literature also highlights several instances of misinformation propagation on Twitter in the form of rumors, digital vigilantes, and false flags, amongst which was a popular case of rumors that emerged from Twitter after the 2013 Boston Marathon Bombing [8, 9]. The results from these studies reported that about 29% of the most viral posts turned out to be rumors and misinformation propagated surrounding the crisis. There have been similar instances in the domain of healthcare, politics, and natural disasters. The outbreak of Ebola was another event that triggered a series of false information trails [10]. The findings reported that about 59% of the content was misinformation and amongst that, the most common discussions stated that Ebola could have been cured by the plant Ewedu or by blood transfusion.
        ''')

        # get things from DB
        query = f'''SELECT * FROM FullTextObject WHERE  FullText_ID = {FullText_ID}'''
        cur.execute(query)
        GET_FROM_DB = cur.fetchone()
        flash(f'query is {query}')
        #flash(f'Got GET_FROM_DB: {GET_FROM_DB}')
        textobject.text = GET_FROM_DB['full_text']
        textobject.title = GET_FROM_DB['title']
        textobject.owner = GET_FROM_DB['userID']
        textobject.paragraphDelims = stringToList(GET_FROM_DB['paragraph_delims'])
        textobject.sentenceDelims = stringToList(GET_FROM_DB['sentence_delims'])
        textobject.highlightDelims = stringToList(GET_FROM_DB['highlight_delims'])
        textobject.wordDelims = stringToList(GET_FROM_DB['word_delims'])

        flash(textobject)

        #return the obj
        return textobject


    def submitToDB(fulltextObj, userAccountsID):
        if fulltextObj.owner is None:
            fulltextObj.owner = userAccountsID
        FullText_ID = -1 #get from DB after insert
        fullText = fulltextObj.text
        from marca.db import get_db
        db = get_db().connect()
        cur = db.cursor()

        # submit text to DB
        fullText = fullText.replace('"','\\"')
        query = f'''INSERT INTO `FullText` (title, text_tokenized, full_text)
        VALUES ("%s","%s","%s");''' % (fulltextObj.title, fulltextObj.paragraphList, fullText)
        print('\n',query)
        cur.execute(query)
        db.commit()

        # get return value of new text insert (fulltextObj.db_ID)
        q1 = '''SELECT FullText_ID from pthompsoDB.FullText ORDER BY FullText_ID DESC LIMIT 1;'''
        cur.execute(q1)
        tokenizedTextRetrieved =  cur.fetchone()
        fulltextObj.db_ID = tokenizedTextRetrieved['FullText_ID']

        # insert statement for text/user association
        fullText_UserAccount_assoc_Query = f'''INSERT INTO `pthompsoDB`.`user_FullText_assoc`
                (`userID`,
                `FullTextID`)
            VALUES
                ({userAccountsID},
                {fulltextObj.db_ID});
            '''
        cur.execute(fullText_UserAccount_assoc_Query)
        db.commit()

        # put the object attributes (delimeters) in DB
        delimQuery = f'''INSERT INTO Delims
        (
            fulltext_ID,
            paragraph_delims,
            sentence_delims,
            highlight_delims,
            word_delims
        )
        VALUES
        (
            {fulltextObj.db_ID},
            "{fulltextObj.paragraphDelims}",
            "{fulltextObj.sentenceDelims}",
            "{fulltextObj.highlightDelims}",
            "{fulltextObj.wordDelims}"
        );'''
        cur.execute(delimQuery)
        db.commit()
        # if this is -1, something went wrong
        return fulltextObj.db_ID


    def __str__(self):
        textlen = len(self.text)
        return f'''FullText object:\n
        my ID: {self.db_ID}
        Title:"{self.title}", with text of {textlen} characters
        Belongs to user with ID={self.owner}
        '''


def stringToList(stringIn, replaceStr="), ", replaceWith=")|", splitOn="|"):
    listOut = []
    #: get rid of opening and closing brackets
    stringIn = stringIn[1:-1]
    #: listify the string
    #tempList = stringIn.replace('[','').replace(']','').replace(replaceStr,replaceWith).split("|")
    tempList = stringIn.replace(replaceStr,replaceWith).split(splitOn)
    #: evaluate each item in the list
    for thing in tempList:
        listOut.append(eval(thing))
    return listOut


def getDelims_Words(inputText):
    '''
        Returns:
        a list of integer tuples, where the integers correspond to the index of
        the characters that start and end each word, with exclusive upper bound.
        [start, end)
    '''
    from nltk.tokenize import TreebankWordTokenizer
    word_tokenizer = TreebankWordTokenizer()
    wordDelims = []
    #previous_start = 0
    for this_start, this_end in word_tokenizer.span_tokenize(inputText):
        #delims = slice(previous_start, this_start)
        delims = slice(this_start, this_end)
        wordDelims.append(delims)
        #previous_start = this_start

    #: add the last slice (ending at the end of the inputText)
    #wordDelims.append(slice(previous_start, len(inputText)))
    #: remove the first slice [0:0]
    #wordDelims.pop(0)

    return wordDelims



def getDelims_Sentence(inputText):
    '''
        Returns:
        a list of integer tuples, where the integers correspond to the index of
        the words that start and end each sentence, with exclusive upper bound.
        [start, end)
    '''
    from nltk.tokenize import PunktSentenceTokenizer
    sent_tokenizer = PunktSentenceTokenizer()
    sentenceDelims = []
    previous_start = 0
    for this_start, this_end in sent_tokenizer.span_tokenize(inputText):
        delims = slice(previous_start, this_start)
        sentenceDelims.append(delims)
        previous_start = this_start

    #: add the last slice (ending at the end of the inputText)
    sentenceDelims.append(slice(previous_start, len(inputText)))
    #: remove the first slice [0:0]
    sentenceDelims.pop(0)
    return sentenceDelims



def getDelims_Paragraph(paragraphList):
    '''
        Returns:
        a list of integer tuples, where the integers correspond to the index of
        the words that start and end each paragraph, with exclusive upper bound.
        [start, end)
    '''
    paragraphDelims = []
    startDelim = 0
    for paragraph in paragraphList:
        paragraphLength = startDelim + len(paragraph)
        delims = slice(startDelim, paragraphLength)
        paragraphDelims.append(delims)

        startDelim = paragraphLength
    return paragraphDelims


def getParagraphList(inputText):
    from nltk.tokenize.texttiling import TextTilingTokenizer
    tiling_tokenizer = TextTilingTokenizer(demo_mode=False)
    try:
        paragraphList = tiling_tokenizer.tokenize(inputText)
    except ValueError: # maybe the input was too short or didn't have a newline ending
        inputText += '\n\n'
        paragraphList = tiling_tokenizer.tokenize(inputText)

    return paragraphList


def testLen(textStr, textList):
    ''' just testing - compares length of original text and paragraph tokens
    '''
    a = len(textStr)
    b = 0
    for t in textList:
        b += len(t)
    return a, b




def do_testing():
        ''' for testing this file '''
        with open('demo_text.txt', mode='r') as f:
            demotext1 = f.readlines()
        demotext = ''.join(demotext1)
        print(testLen(demotext, demotext1))

        ft = FullText(demotext)

        True


if __name__ == '__main__':
    do_testing()
