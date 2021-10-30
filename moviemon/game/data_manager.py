import random
import pickle
import requests
import game.game_settings as game_settings
from copy import copy

class DataManager():
	class DataManagerException(Exception):
		def __init__(self, message):
			message = "DataManager Error: " + message
			super().__init__(message)

	def __init__(self, data=None):
		self.grid_size = None
		self.player_position = None
		self.player_strength = None
		self.player_movieballs = None
		self.film_ids = []
		self.captured_moviemons = []
		self.moviemons_info = []
		self.loaded_data = data
		self.isMoviemonEncountered = False
		self.isMovieballFound = False

	def __str__(self):
		return """
Player position: {0}
Player strength: {1}
Player movieballs: {2}
Films ids: {3}
Captured Moviemons Ids: {4}
Moviemons Info: {5}
Is data loaded?: {6}
		""".format(
			self.player_position,
			self.player_strength,
			self.player_movieballs,
			self.film_ids,
			self.captured_moviemons,
			[x["Title"] for x in self.moviemons_info],
			self.loaded_data != None,
		)


	def load(self):
		self = pickle.loads(self.loaded_data)
		return self


	def dump(self):
		return pickle.dumps(self)


	def get_random_movie(self):
		all_movies = self.film_ids
		captured = self.captured_moviemons
		not_captured = [m for m in all_movies if m not in captured]
		return random.choice(not_captured)


	def __request_movie(self, id):
		return requests.get(
			'http://www.omdbapi.com/',
			{
				'apikey': game_settings.APIKEY,
				'i': id
			}
		).json()


	def __init_moviemons(self, film_ids):
		moviemons_info = []
		for id in film_ids:
			moviemons_info.append(self.__request_movie(id))
		return moviemons_info


	def load_default_settings(self):
		self.grid_size = copy(game_settings.GRID_SIZE)
		self.player_position = copy(game_settings.PLAYER_START_POSSITION)
		self.player_strength = 1
		self.player_movieballs = copy(game_settings.PLAYER_START_MOVIEBALLS)
		self.film_ids = copy(game_settings.FILMS)
		self.moviemons_info = self.__init_moviemons(self.film_ids)
		self.captured_moviemons = []
		self.isMovieballFound = False
		self.isMoviemonEncountered = False
		return self


	def get_strength(self):
		return self.player_strength


	def get_movie(self, moviemon_name):
		for m in self.moviemons_info:
			if m['Title'] == moviemon_name:
				return m
		return None


	def get_map(self):
		map = []
		for y in range(self.grid_size[1]):
			map.append([])
			for x in range(self.grid_size[0]):
				if [x, y] == self.player_position:
					map[y].append(1)
				else:
					map[y].append(0)
		return map


	def check_encounter(self):
		if random.randrange(0, 100, 1) < 10:
			if random.randrange(0, 2, 1) == 0:
				self.isMoviemonEncountered = True
			else:
				self.isMovieballFound = True


	def go(self, direction):
		if direction == 'left':
			if self.player_position[0] > 0:
				self.player_position[0] -= 1
		elif direction == 'right':
			if self.player_position[0] < self.grid_size[0] - 1:
				self.player_position[0] += 1
		elif direction == 'up':
			if self.player_position[1] > 0:
				self.player_position[1] -= 1
		elif direction == 'down':
			if self.player_position[1] < self.grid_size[1] - 1:
				self.player_position[1] += 1


	def pick_movieball(self):
		self.player_movieballs += 1




if __name__ == '__main__':
	manager = DataManager()
	manager.load_default_settings()
	print(manager)

	manager.player_position = [4, 5]
	manager.captured_moviemons.append(manager.film_ids[4])
	print(manager)

	saved_obj = manager.dump()
	print(saved_obj)

	manager2 = DataManager(saved_obj)
	manager2.load_default_settings()
	print(manager2)

	manager2 = manager2.load()
	print(manager2)
	print(manager2.get_strength())
	print(manager2.get_movie('The Resort'))
	print(manager2.get_random_movie())
