from json import dumps
from random import randint

from tornado.web import RequestHandler, asynchronous, Application
from tornado import gen
import tornado.concurrent
import urllib

from tornado.websocket import WebSocketHandler

from helpers import run_async
executor = tornado.concurrent.futures.ThreadPoolExecutor(8)


@run_async
def a(callback):
    b = urllib.urlopen("http://dplogin.com/serverlist.php").read()
    print (b,)
    from time import sleep
    callback(b)


class MainHandler(RequestHandler):

    def get(self):
        r = yield gen.Task(a)
        self.write(r)
        self.finish()
        print [r]


class ChatWebSocket(WebSocketHandler):
    connections = set()
    messages = []
    id_count = [0]

    def open(self):
        self.user_id = "Guest #%d" % self.id_count[0]
        self.id_count[0] += 1
        self.connections.add(self)
        [self.write_message(dumps(msg)) for msg in self.messages]
        print "Socket opened"

    def on_message(self, message):
        print message
        self.messages.append({"from": self.user_id, "message": message})
        [conn.write_message(dumps({"from": self.user_id, "message": message}))
            if conn != self else "" for conn in self.connections]

    def on_close(self):
        self.connections.remove(self)
        print "Socket closed"


class TestHandler(RequestHandler):
    def get(self):
        self.render("templates/chat.html")


def make_app():
    return Application([
        (r'/2', MainHandler),
        (r'/', TestHandler),
        (r'/socket', ChatWebSocket),
    ], debug=True)

