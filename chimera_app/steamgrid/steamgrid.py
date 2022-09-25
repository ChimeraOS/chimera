import requests
import html


class Steamgrid:

    def __init__(self, api_key):
        self.__api_key = api_key

    def search_games(self, search_string):
        url = "https://www.steamgriddb.com/api/v2/search/autocomplete/{}".format(html.escape(search_string))
        response = self.__request(url)
        return response.text

    def get_images(self, game_id, imgtype=None):
        if imgtype == 'banner':
            url = "https://www.steamgriddb.com/api/v2/grids/game/{}?dimensions=460x215,920x430".format(game_id)
        elif imgtype == 'poster':
            url = "https://www.steamgriddb.com/api/v2/grids/game/{}?dimensions=600x900".format(game_id)
        elif imgtype == 'background':
            url = "https://www.steamgriddb.com/api/v2/heroes/game/{}".format(game_id)
        elif imgtype == 'logo':
            url = "https://www.steamgriddb.com/api/v2/logos/game/{}".format(game_id)
        elif imgtype == 'icon':
            url = "https://www.steamgriddb.com/api/v2/icons/game/{}".format(game_id)
        else:
            return

        response = self.__request(url)
        return response.text

    def __request(self, url):
        headers = {
            'Authorization': "Bearer {}".format(self.__api_key)
        }
        return requests.get(url, headers=headers)
