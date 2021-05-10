import json
import os
# import sys
# import pygame

mapFolder = os.path.join(os.path.dirname(__file__), 'maps')

with open('config.json') as f:
    config = json.load(f)


def resetComplete(mapData):
    if "completion" in mapData and "completed" in mapData["completion"]:
        mapData["completion"]["completed"] = False
    return mapData


def resetScore(mapData):
    if "score" in mapData:
        mapData["score"] = 0
    return mapData


def resetLocked(mapData):
    mapData["locked"]["isLocked"] = True
    return mapData


for key, level in dict(
    **config["maps"]["builtIn"],
        **config["maps"]["custom"]).items():

    m = os.path.join(mapFolder, level)
    with open(m) as f:
        data = json.load(f)

    if data:
        data = resetComplete(data)
        data = resetScore(data)
        data = resetLocked(data)
        with open(m, "w") as f:
            json.dump(data, f)
