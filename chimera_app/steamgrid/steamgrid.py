import requests
import html
import difflib
import json
import re


class Steamgrid:

    def __init__(self, api_key):
        self.__api_key = api_key

    def set_api_key(self, api_key):
        self.__api_key = api_key

    def search_games(self, search_string):
        url = "https://www.steamgriddb.com/api/v2/search/autocomplete/{}".format(
            html.escape(search_string)
        )
        response = self.__request(url)
        return response.text

    def get_images(self, game_id, imgtype=None):
        if imgtype == "banner":
            url = "https://www.steamgriddb.com/api/v2/grids/game/{}?dimensions=460x215,920x430".format(
                game_id
            )
        elif imgtype == "poster":
            url = "https://www.steamgriddb.com/api/v2/grids/game/{}?dimensions=600x900".format(
                game_id
            )
        elif imgtype == "background":
            url = "https://www.steamgriddb.com/api/v2/heroes/game/{}".format(game_id)
        elif imgtype == "logo":
            url = "https://www.steamgriddb.com/api/v2/logos/game/{}".format(game_id)
        elif imgtype == "icon":
            url = "https://www.steamgriddb.com/api/v2/icons/game/{}".format(game_id)
        else:
            return

        response = self.__request(url)
        return response.text

    def __request(self, url):
        headers = {"Authorization": "Bearer {}".format(self.__api_key)}
        return requests.get(url, headers=headers, timeout=20)

    def find_best_match(self, game_name: str) -> dict:
        # strip non alpha numerica
        game_name = re.sub(r"[^a-zA-Z0-9 ]", "", game_name)

        game_name_tokens = sorted(game_name.lower().split())
        steamgridlist: dict = json.loads(self.search_games(game_name))["data"]
        best_match: dict = steamgridlist[0]
        best_similarity: float = 0.0

        for item in steamgridlist:
            item_name = re.sub(r"[^a-zA-Z0-9 ]", "", item["name"])
            steam_response_tokens = sorted(item_name.lower().split())

            similarity = difflib.SequenceMatcher(
                None, game_name_tokens, steam_response_tokens
            ).ratio()

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = item
                item["similarity_score"] = float(similarity)

        return best_match if best_match else None
