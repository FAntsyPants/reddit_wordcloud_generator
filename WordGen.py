import praw
import sys, os
from os import path
from dotenv import load_dotenv
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import http.server
import socketserver
import os
import threading
import time
load_dotenv('.env')
os.chdir(sys.path[0])
SECRET = os.environ.get("SECRET")
PASSWORD = os.environ.get("PASSWORD")

reddit = praw.Reddit(
    client_id="client_id",
    client_secret=SECRET,
    password=PASSWORD,
    user_agent="test",
    username="username",
)


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

snoo_mask = np.array(Image.open(path.join(d,"snoo.png")))

stopwords =list(STOPWORDS)

wc = WordCloud(
    background_color='black',
    stopwords=stopwords,
    height=600,
    width=900,
    mask=snoo_mask,
    colormap="OrRd"
)

# Generate a word cloud image from top comments of user
with open("comments.txt", "w", encoding='utf-8') as comments:
    for comment in reddit.redditor("username").comments.top(limit=None):
        comments.write(comment.body.split("\\n", 1)[0][:79])

text = open("comments.txt","r",encoding='utf-8').read()
wc.generate(text)
wc.to_file('output.png')

# Create a web server and define the handler to manage the
class MyHandler(http.server.SimpleHTTPRequestHandler):
    # Handler for the GET requests
    # path_to_image is the path to the image you want to serve
    path_to_image = 'output.png'
    img = open(path_to_image, 'rb')
    statinfo = os.stat(path_to_image)
    img_size = statinfo.st_size
    print(img_size)

def do_HEAD(self):
    self.send_response(200)
    # send image/png header 
    self.send_header("Content-type", "image/png")
    self.send_header("Content-length", img_size)
    self.end_headers()

def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "image/png")
    self.send_header("Content-length", img_size)
    self.end_headers() 
    f = open(path_to_image, 'rb')
    self.wfile.write(f.read())
    f.close()         

class MyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_adress, RequestHandlerClass):
        self.allow_reuse_address = True
        socketserver.TCPServer.__init__(self, server_adress, RequestHandlerClass, False)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8080
    server = MyServer((HOST, PORT), MyHandler)
    server.server_bind()
    server.server_activate()
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
