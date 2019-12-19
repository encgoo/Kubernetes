#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, flash, jsonify
from BloomFilter.bloom_filter import BloomFilter

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234567890abcdef"
ABOUT_STR="""
<h1> Online Spell Check </h1>
<a href="http://codekata.com/kata/kata05-bloom-filters/">Bloom filter</a> for spell check.
The dictionary being used is the one on Debian /usr/share/dict/words.
"""

@app.route("/")
def about():
    return ABOUT_STR

@app.route("/check")
def check():
    return render_template("./spell-check.html")


@app.route("/check", methods=['POST'])
def check_word():
    b_filter = BloomFilter(filename="BloomFilter/bitmap.bin")
    word = request.form.get("word", None)
    if word:
        good = b_filter.check_word(word, num_checksum=2)

        if good:
            flash ("word '{}' is good".format(word))
        else:
            flash ("word '{}' is wrong".format(word))
    else:
        flash("Please enter a word")

    return render_template("./spell-check.html")


@app.route("/api/v1.0/check", methods=["GET"])
def check_word_api():
    b_filter = BloomFilter(filename="BloomFilter/bitmap.bin")
    word = request.args.get("word", None)
    ret = {
        "num_checksums": 2,
        "checksums":[
            "md5",
            "sha256"
        ],
        "word": "",
        "found": "False"
    }
    if word:
        good = b_filter.check_word(word, num_checksum=2)
        ret["word"] = word
        if good:
            ret["found"] = "True"
        else:
            ret["found"] = "False"

    return jsonify(ret)


if __name__=="__main__":
    if __package__ is None:
        import os
        os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app.run(host="0.0.0.0", port=5000)
