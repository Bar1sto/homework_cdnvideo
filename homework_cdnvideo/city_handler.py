import tornado.ioloop
import tornado.web
import redis
import requests
from geopy.distance import geodesic

db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class CityHandler(tornado.web.RequestHandler):
    def get(self):
        lat = float(self.get_argument('lat'))
        lon = float(self.get_argument('lon'))
        cities = db.keys()
        distances = []

        for city in cities:
            city_info = db.hgetall(city)
            city_lat = float(city_info['lat'])
            city_lon = float(city_info['lon'])
            distance = geodesic((lat, lon), (city_lat, city_lon)).kilometers
            distances.append((city, distance))

        distances.sort(key=lambda x: x[1])
        nearest_cities = distances[:2]

        self.write({"Ближайшие города: ": nearest_cities})

    def post(self):
        name = self.get_argument('name')
        location = self.get_location_from_api(name)

        if location:
            lat, lon = location['lat'], location['lon']
            info = {"lat": lat, "lon": lon}
            db.hmset(name, info)
            self.write(f"Город {name} успешно добавлен с координатами: {lat}, {lon}")
        else:
            self.set_status(400)
            self.write("Не удалось получить координаты города")

    def delete(self):
        name = self.get_argument('name')

        if db.delete(name):
            self.write(f"Город {name} успешно удален")
        else:
            self.set_status(404)
            self.write(f"Город {name} не найден")

    def get_location_from_api(self, city_name):
        try:
            response = requests.get(f"https://nominatim.openstreetmap.org/search?q=%7B{city_name}%7D&format=json&limit=1")
            response.raise_for_status()
            data = response.json()
            if data:
                return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
            return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выборке координат: {e}")
            return None
