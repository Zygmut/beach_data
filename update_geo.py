import os
import json


with open("geo_data.json", "r") as file:
	geo_data = json.load(file)

with open("beach_data.json.raw", "r") as file:
	beach_data = json.load(file)


for idx, beach in enumerate(beach_data["itemListElement"]):
	# print(f'{idx=} name={beach["name"]}')

	try:
		if (geo_data[beach["name"]] is not None):
			beach_data["itemListElement"][idx]["geo"]["latitude"] = geo_data[beach["name"]]["lat"]
			beach_data["itemListElement"][idx]["geo"]["longitude"] = geo_data[beach["name"]]["lon"]
	except Exception:
		pass


with open("beach_data.json", "w") as file:
	file.write(json.dumps(beach_data, indent=2))

