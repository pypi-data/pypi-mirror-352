def image_source(name):
    image_desc_dict = {
        "deimos":"https://www.flickr.com/photos/24354425@N03/14707114439",
        "phobos":"https://itoldya420.getarchive.net/media/phobos-from-5800-kilometers-color-793655",
        "moon":"https://www.rawpixel.com/search?page=1&path=1522.sub_topic-4568&sort=curated",
        "neptune": "https://commons.wikimedia.org/wiki/File:Sub-neptune.jpg",
        "uranus": "https://commons.wikimedia.org/wiki/File:Transparent_Uranus.png",
        "saturn": "https://www.flickr.com/photos/nasahubble/45752907895/in/photostream/",
        "jupiter": "https://commons.wikimedia.org/wiki/File:Jupiter_%28January_2023%29_%28heic2303e%29.jpg",
        "mars": "https://commons.wikimedia.org/wiki/File:MARS_THE_RED_PLANET.jpg",
        "earth": "https://www.pexels.com/photo/planet-earth-87651/",
        "mercury": "https://www.flickr.com/photos/gsfc/8497942353",
        "dog": "https://commons.wikimedia.org/wiki/File:Golde33443.jpg",
        "cat": "https://commons.wikimedia.org/wiki/File:Cat03.jpg",
        "venus": "https://commons.wikimedia.org/wiki/File:Venus.png",
        "sun":"https://www.flickr.com/photos/gsfc/8673066962"
        }
    return image_desc_dict.get(name.lower(), None)
