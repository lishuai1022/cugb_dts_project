"""
    web service
"""
import logging

from tornado.options import define, options
import tornado.web, tornado.ioloop, tornado.httpserver
import tornado.netutil,tornado.process
from . import config, urls,rds
from .util.session import *

define("port", default=config.PORT, help="run on the given port", type=int)
define("debug",default=config.DEBUG,help="Debug Mode",type=bool)

class Application(tornado.web.Application):
    def __init__(self):
        # application settings
        settings = {
            'cookie_secret': config.COOKIE_SECRET,
            'autoreload': config.AUTORELOAD,
            'debug': config.DEBUG,
            'session_secret':config.SESSION_SECRET,
            'session_timeout':config.SESSION_TIMEOUT

        }
        tornado.web.Application.__init__(self, urls.handlers, **settings)
        self.redis = rds.RedisClient()
        self.session_manager = SessionManager(config.SESSION_SECRET,self.redis,config.SESSION_TIMEOUT)

# setup environment
def _setup():
    # init logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(name)s][%(levelname)s]-%(message)s-[%(filename)s, %(lineno)d]')


# start service
def start(port=options.port):
    # setup environment
    _setup()

    # log start message
    logging.info('start tools service on port %d' % port)

    # start web application
    if options.debug:
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    else:
        sockets = tornado.netutil.bind_sockets(port)
        tornado.process.fork_processes(0)
        server = tornado.httpserver.HTTPServer(Application())
        server.add_sockets(sockets)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start()