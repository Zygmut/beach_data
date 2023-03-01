import requests
import json
from bs4 import BeautifulSoup
from unidecode import unidecode
from functools import reduce

def getDictData(location:str, beach:str) -> dict:
    def sanitize_string(string:str) -> str:
        return unidecode(string.replace("´", "").replace("'", "").replace("ç", "s"))

    def get_beach_location(soup:BeautifulSoup) -> str:
        return list(map(lambda x: str(x.text).split(",")[0], filter(lambda x: str(x.text).endswith("Mallorca"), soup.find_all("span"))))[0]

    def get_beach_name(soup: BeautifulSoup) -> str:
        return str(soup.find_all("h1")[1].text).strip()

    # Superficie playa
    def get_beach_surface(soup: BeautifulSoup) -> int:
        try:
            return reduce(lambda x, y: x * y, map(lambda x: int(x), filter(lambda x: str(x).isdigit(), soup.find("div", {"class": "infor-historia"}).find_all("p")[1].text.split(" "))))
        except:
            return 0

    # Servicio de playa
    def get_service(soup: BeautifulSoup, service:str) -> bool:
        return soup.find(string=service.upper()).find_parent("div").findChildren()[1].text == "SI"

    # Tipo de playa
    def get_beach_type(soup: BeautifulSoup) -> str:
        return "sand" if get_service(soup, "ARENA") else "rock"

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/es/Mallorca/"+ sanitize_string(location) + "/" + ("" if beach.lower().startswith("playa-") else "playa-") + sanitize_string(beach).replace(" ", "-") + ".html").content, "html.parser")

    return {"name":                 sanitize_string(get_beach_name(soup)),
            "location":             sanitize_string(get_beach_location(soup)),
            "geo_location":         {"latitude": 0, "longitude": 0},
            "type":                 get_beach_type(soup),
            "surface_area_meters":  get_beach_surface(soup),
            "lifeguard":            get_service(soup, "SERVICIO DE SOCORRO"),
            "parking":              get_service(soup, "APARCAMIENTO"),
            "showers":              get_service(soup, "DUCHAS"),
            "blue_flag":            get_service(soup, "BANDERA AZUL"),
            "nudist":               get_service(soup, "NUDISTA" ),
            "car_accesible":    not get_service(soup, "CAMINATA")
            }

locations = list(set(map(lambda x: x['href'].split("/")[1].replace(".html", "") ,filter(lambda x: x['href'][0] == 'M' , BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/es/Mallorca.html").content, "html.parser").find_all("a", href=True)))))
beaches = list(map(lambda place: list(set(map(lambda x: x['href'].split("/")[1].replace(".html", "") ,filter(lambda x: x['href'][0] == place[0] , BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/es/Mallorca/" + place + ".html").content, "html.parser").find_all("a", href=True))))),locations))

beaches_data = []
for idx, location in enumerate(locations):
    for beach_name in beaches[idx]:
        try:
            beaches_data.append(getDictData(location, beach_name))
        except:
            print(f"Could not scrape {location = }, {beach_name = }")

beaches_json = json.dumps(beaches_data, indent=2)

with open('beach_data.json', 'w') as file:
    file.write(beaches_json)
