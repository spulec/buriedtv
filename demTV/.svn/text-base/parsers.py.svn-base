from xml.parsers import expat

"""
Note that these parsers grab all data except attributes between the desired 
tags including other tags and the info within them
"""

class SimpleParserSingle:
    """
    A parser that looks for all occruences of the inputted tag and appends
    all the data within them to a string
    """
    def __init__(self):
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.CharacterDataHandler = self.data

    def feed(self, data, tag):
        self.tag = tag
        self.processing = False
        self.data = ""
        result = self.parser.Parse(data)

    def start(self, tag, attrs):
        if tag == self.tag:
            self.processing = True
        if self.processing:
            self.data += "<" + tag + ">"
    def end(self, tag):
        if self.processing:
            self.data += "</" + tag + ">"
        if tag == self.tag:
            self.processing = False
    def data(self, data):
        if self.processing:
            self.data += data

class SimpleParserMultiple:
    """
    A parser that looks for any occurence of an inputted tag and appends 
    the data to a list
    """
    def __init__(self):
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.CharacterDataHandler = self.data

    def feed(self, data, tag):
        self.tag = tag
        self.processing = False
        self.data = []
        self.currData = ""
        result = self.parser.Parse(data)

    def start(self, tag, attrs):
        if tag == self.tag:
            self.processing = True
        if self.processing:
            self.currData += "<" + tag + ">"
    def end(self, tag):
        if self.processing:
            self.currData += "</" + tag + ">" 
        if tag == self.tag:
            self.processing = False
            self.data.append(self.currData)
            self.currData = ""
    def data(self, data):
        if self.processing:
            self.currData += data

class SimpleParserDict:
    """
    A parser that looks for occurences of the inputted array of tags and sets 
    the dict data to the data inside that tags. Not stable if tags in the
    inputted dict overlap.
    """
    def __init__(self):
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.CharacterDataHandler = self.data

    def feed(self, data, tag):
        self.tag = tag
        self.currTag = None
        self.processing = False
        self.data = {}
        result = self.parser.Parse(data)

    def start(self, tag, attrs):
        if tag in self.tag:
            self.processing = True
            self.currTag = tag
    def end(self, tag):
        if tag == self.currTag:
            self.processing = False
            self.currTag = None
    def data(self, data):
        if self.processing:
            # Only set data if not already set
            if self.currTag not in self.data:
                self.data[self.currTag] = data


