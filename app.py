__author__ = 'tushar'

import os
from collections import Counter
import operator
import re

import requests
from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup as bs
import nltk

from stop_words import stops



#
# Configurations
#
app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
db = SQLAlchemy(app)

from models import Result


#
# routes
#

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        # get user provided url
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again"
            )
            return render_template('index.html', errors=errors)
        if r:
            # process text
            raw = bs(r.text).get_text()
            nltk.data.path.append('./nltk_data/')
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)

            # remove punctuations, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_words_count = Counter(raw_words)

            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)

            # save results
            results = sorted(no_stop_words_count.items(), key=operator.itemgetter(1), reverse=True)
            try:
                result = Result(
                    url=url,
                    result_all=raw_words_count,
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database")
        return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    app.run()
