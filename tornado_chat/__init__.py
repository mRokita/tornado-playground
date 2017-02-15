import app
import tornado.ioloop


def main():
    application = app.make_app()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
