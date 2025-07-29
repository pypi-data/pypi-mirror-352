def image(name):
    image_dict = {
        "deimos":"https://live.staticflickr.com/5575/14707114439_1ff30dbdd3_c.jpg",
        "phobos":"https://cdn2.picryl.com/photo/2008/04/09/phobos-from-5800-kilometers-color-793655-1024.jpg",
        "moon":"https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvcGQzNi0xLWdzZmNfMjAxNzEyMDhfYXJjaGl2ZV9lMDAwODY4LWt6cHl3MG90LmpwZw.jpg",
        "neptune": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Sub-neptune.jpg/960px-Sub-neptune.jpg",
        "uranus": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transparent_Uranus.png/600px-Transparent_Uranus.png",
        "saturn": "https://live.staticflickr.com/7823/45752907895_295bd37423_b.jpg",
        "jupiter": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupiter_%28January_2023%29_%28heic2303e%29.jpg/960px-Jupiter_%28January_2023%29_%28heic2303e%29.jpg?20230416215004",
        "mars": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/MARS_THE_RED_PLANET.jpg/960px-MARS_THE_RED_PLANET.jpg",
        "earth": "https://images.pexels.com/photos/87651/earth-blue-planet-globe-planet-87651.jpeg",
        "dog": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Golde33443.jpg",
        "cat": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg",
        "mercury": "https://live.staticflickr.com/8374/8497942353_f0756442f5_b.jpg",
        "venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Venus.png/600px-Venus.png",
        "sun":"https://live.staticflickr.com/8256/8673066962_f8ffaab262_b.jpg"
        }
    return image_dict.get(name.lower(), None)
