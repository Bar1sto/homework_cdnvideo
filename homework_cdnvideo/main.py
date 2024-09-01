import tornado.ioloop
import tornado.web
from city_handler import CityHandler

def make_app():
    return tornado.web.Application([
        (r"/city", CityHandler),
    ])    
    
if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    print("http://localhost:8080")
    tornado.ioloop.IOLoop.current().start()