import json

from aiogram.utils.markdown import text, bold, italic

import aiohttp
import imdb

URL = 'https://api.themoviedb.org/3/'
API_KEY = '38d82697124e1e1ba9ad389d6257e0da'


class Response:
    def __init__(self):
        self.description = ''
        self.photo = None
        self.title = ''
        self.query = ''
        self.movie_info = ''

    async def set_query(self, query: str) -> None:
        self.query = query

    async def get_query(self) -> str:
        return self.query

    async def set_movie_info(self, movie_info: str) -> None:
        self.movie_info = movie_info

    async def get_movie_info(self) -> str:
        return self.movie_info

    async def get_films_by_name(self, session: aiohttp.ClientSession, name: str) -> str:
        try:
            async with session.get('{}search/movie?api_key={}&query={}&language=ru-RU'.format(URL, API_KEY, name)) as resp:
                response = json.loads(await resp.text())
                output_text = ''
                if len(response['results']) > 0:
                    output_text += 'Найденные по Вашему запросу фильмы\n'
                    for movie in response['results']:
                        output_text += "{}\t[{}]\t{}\n".format(movie['original_title'], movie['release_date'][:4] if 'release_date' in movie.keys() else '',
                                                               movie['id'])
                else:
                    output_text += 'К сожалению, по вашему запросу ничего не найдено\n'
                return output_text
        except KeyError:
            return 'К сожалению, по вашему запросу ничего не найдено\n'

    async def response_id_query(self, session: aiohttp.ClientSession, film_id) -> None:
        async with session.get(
                "{}movie/{}?api_key={}&append_to_response=videos&language=ru-RU".format(URL, film_id,
                                                                                        API_KEY)) as result:
            movie = json.loads(await result.text())
            self.title = movie['original_title']
            genres = [genre['name'] for genre in movie['genres']]
            self.description = text(bold(self.title))  + "\n\n📅 {},\n⭐️ {} \n".format(movie['release_date'][:4],
                                                                          movie['vote_average'])

            # Duration
            if movie['runtime'] is not None:
                self.description += "⏱️ {} мин.\n".format(movie['runtime'])
            # Genres
            if len(genres) > 0:
                genres = ", ".join(genres)
                self.description += "🎭 {}\n\n\n".format(genres)
            if movie['overview'] is not None and len(movie['overview']):
                self.description += "📄 {}\n\n".format(movie['overview'])

            if movie['poster_path'] is not None and len(movie['poster_path']) > 0:
                self.photo = "https://image.tmdb.org/t/p/original/{}".format(movie['poster_path'])
            else:
                self.photo = None
