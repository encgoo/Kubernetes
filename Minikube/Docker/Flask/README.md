# Online Spell Check
This is a POC to create an online spell checker using Bloom Filter. 

The [Bloom Filter](http://codekata.com/kata/kata05-bloom-filters/) for spell check.
The python code is in this [folder](BloomFilter). 

Python Flask is used to provide web service and REST API for online spell check.
## Design
Use [flask web form](https://pythonspot.com/flask-web-forms/) to generate a html page. 
The [template](templates/spell-check.html) is straightforward.

## Test
Use this to start the Flask server in standalone mode
```python3 app.py```
![screenshot](images/SpellCheck.png)

Now ready to go up to Docker