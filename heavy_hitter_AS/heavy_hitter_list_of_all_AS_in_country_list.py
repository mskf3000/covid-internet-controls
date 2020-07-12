import codecs
from html.parser import HTMLParser
import sys

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Data  :", data)


f=codecs.open(sys.argv[1], 'r')
parser = MyHTMLParser()
parser.feed(f.read())


