import os

import requests
from django.shortcuts import render
from dotenv import load_dotenv

from .models import Place

def fetch_coordinates(address):
    load_dotenv()
    apikey = os.getenv('API_KEY')
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_coordinates(addresses):
    matching_addresses = Place.objects.filter(address__in=addresses)
    places = {}
    for place in matching_addresses:
        places[place.address] = (place.latitude, place.longitude)
        addresses.pop(addresses.index(place.address))

    if addresses:
        for address in addresses:
            try:
                lat, lon = fetch_coordinates(address)
                Place.objects.update_or_create(address=address, latitude=lat, longitude=lon)
            except TypeError:
                continue

            places[address] = (lat, lon)
        
    
    return places

        

