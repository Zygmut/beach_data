import requests
import os
import json
from PIL import Image
from bs4 import BeautifulSoup
from unidecode import unidecode

def get_photos(location: str, beach_name: str, n_photos: int):
    try:
      for n in range(1, n_photos+1):
        img = Image.open(requests.get("http://www.disfrutalaplaya.com/es/Mallorca/"+ location + "/" + ("" if beach_name.lower().startswith("playa-") else "playa-") + beach_name.replace(" ", "-") + "/fullsize/" + str(n) + ".jpg", stream=True).raw)
        w, h = img.size
        img.crop((0, 0, w-175, h)).save(f"./photos/{location}/{beach_name}/{n}.jpg")
    except:
      return

def getDictData(id: int, location:str, beach:str) -> dict:
    def sanitize_string(string:str) -> str:
        return unidecode(string.replace("´", "").replace("'", "").replace("ç", "s"))

    def get_beach_location(soup:BeautifulSoup) -> str:
        return list(map(lambda x: str(x.text).split(",")[0], filter(lambda x: str(x.text).endswith("Mallorca"), soup.find_all("span"))))[0]

    def get_beach_name(soup: BeautifulSoup) -> str:
        return str(soup.find_all("h1")[1].text).strip()

    def get_beach_description(soup:BeautifulSoup) -> str:
        return soup.find("div", {"class": "infor-historia"}).find_all("p")[0].text;

    # Servicio de playa
    def get_service(soup: BeautifulSoup, service:str) -> str:
        return service.lower().replace(" ", "_") if soup.find(string=service.upper()).find_parent("div").findChildren()[1].text == "SI" else None

    # Tipo de playa
    def get_beach_type(soup: BeautifulSoup) -> str:
        return "arena" if get_service(soup, "ARENA") else "roca"

    def get_video(soup: BeautifulSoup) -> str:
        return "https://www.youtube.com/watch?v=" + soup.find("iframe", title="YouTube video player")['src'].split("/")[-1]


    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/es/Mallorca/"+ sanitize_string(location) + "/" + ("" if beach.lower().startswith("playa-") else "playa-") + sanitize_string(beach).replace(" ", "-") + ".html").content, "html.parser")

    get_photos(sanitize_string(location), sanitize_string(beach), 6)
    return {
      "@type": "Beach",
      "@identifier": id,
      "name": sanitize_string(get_beach_name(soup)),
      "description": [
          get_beach_description(soup), get_beach_description(BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/ct/Mallorca/"+ sanitize_string(location) + "/" + ("" if beach.lower().startswith("playa-") else "playa-") + sanitize_string(beach).replace(" ", "-") + ".html").content, "html.parser")),get_beach_description(BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/en/Mallorca/"+ sanitize_string(location) + "/" + ("" if beach.lower().startswith("playa-") else "playa-") + sanitize_string(beach).replace(" ", "-") + ".html").content, "html.parser")),
        ],
      "geo" : {
        "@type": "GeoCoordinates",
        "address": {
          "@type": "PostalAddress",
          "addressCountry": "ES",
          "addressRegion": "Mallorca",
          "addressLocality": get_beach_location(soup)
        },
        "latitude": 0,
        "longitude": 0
      },
      "photo": ["url", "url", "url"],
      "subjectOf": {
        "@type": "CreativeWork",
        "audio": ["url", "url", "url"],
        "video": get_video(soup)
      },
      "keywords":
      list(filter(None,[
        get_beach_type(soup),
        get_service(soup, "SERVICIO DE SOCORRO"),
        get_service(soup, "APARCAMIENTO"),
        get_service(soup, "DUCHAS"),
        get_service(soup, "BANDERA AZUL"),
        get_service(soup, "NUDISTA" ),
        get_service(soup, "CAMINATA")
      ]))
    }

def create_dir(dir_path: str):
  if not os.path.isdir(dir_path):
    os.makedirs(dir_path)

# locations = list(set(map(lambda x: x['href'].split("/")[1].replace(".html", "") ,filter(lambda x: x['href'][0] == 'M' , BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/es/Mallorca.html").content, "html.parser").find_all("a", href=True)))))[:3]
locations = ['Palma' ,'Muro', 'Alcudia']
beaches = list(map(lambda place: list(set(map(lambda x: x['href'].split("/")[1].replace(".html", "") ,filter(lambda x: x['href'][0] == place[0] , BeautifulSoup(requests.get("http://www.disfrutalaplaya.com/es/Mallorca/" + place + ".html").content, "html.parser").find_all("a", href=True))))),locations))

beaches_data = []
acumulator = 0
for idx, location in enumerate(locations):
    for beach_name in beaches[idx]:
        create_dir(f"./photos/{location}/{beach_name}")
        beaches_data.append(getDictData(acumulator, location, beach_name))
        acumulator += 1

# Outlier
for n in range(1, 7):
  img = Image.open(requests.get(f"http://www.disfrutalaplaya.com/es/Mallorca/Palma/Can-Pere-Antoni/fullsize/{n}.jpg", stream=True).raw)
  w, h = img.size
  img.crop((0, 0, w-175, h)).save(f"./photos/Palma/Playa-Can-Pere-Antoni/{n}.jpg")

with open('beach_data.json', 'w') as file:
    file.write(json.dumps({"@context": "http://schema.org",
                           "@type": "itemList",
                           "itemListElement": beaches_data}, indent=2))
