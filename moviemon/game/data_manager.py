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
		self.bushes = []
		self.player_position = None
		self.player_strength = None
		self.player_movieballs = None
		self.film_ids = []
		self.captured_moviemons = []
		self.moviemons_info = []
		self.loaded_data = data
		self.isMoviemonEncountered = False
		self.isMovieballFound = False
		self.isMovieballThrown = False
		self.isMoviemonCatched = False
		self.session = requests.session()
		self.frame_size = [9, 7]
		self.selected = 1
		self.moviemon_selected = 0
		self.isGameLoaded = False
		self.current_page = '/'


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
		data = pickle.loads(self.loaded_data)
		self.player_position = data[0]
		self.player_movieballs = data[1]
		self.player_strength = data[2]
		self.captured_moviemons = data[3]
		self.film_ids = data[4]
		self.grid_size = data[5]
		self.moviemons_info = data[6]
		self.bushes = data[7]
		return self


	def dump(self):
		data = [
			self.player_position,
			self.player_movieballs,
			self.player_strength,
			self.captured_moviemons,
			self.film_ids,
			self.grid_size,
			self.moviemons_info,
			self.bushes
		]
		return pickle.dumps(data)


	def get_random_movie(self):
		if len(self.film_ids) == 0:
			raise self.DataManagerException("Lack of moviemons")
		all_movies = self.film_ids
		captured = self.captured_moviemons
		not_captured = [m for m in all_movies if m not in captured]
		return random.choice(not_captured)


	def __request_movie(self, id):
		params = {
				'apikey': game_settings.APIKEY,
				'i': id
		}
		return self.session.get('http://www.omdbapi.com/', params=params).json()


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
		self.__generate_bushes()
		return self


	def get_strength(self):
		return self.player_strength


	def get_movie(self, moviemon_id):
		for m in self.moviemons_info:
			if m['imdbID'] == moviemon_id:
				return m
		return None


	def __calculate_frame_index(self, x_or_y):
		offset = int((self.frame_size[x_or_y] - 1) / 2)
		left_index = self.player_position[x_or_y] - offset
		right_index = self.player_position[x_or_y] + offset

		if (left_index < 0):
			right_index += -left_index
			left_index = 0
		elif (right_index > self.grid_size[x_or_y] - 1):
			left_index += self.grid_size[x_or_y] - 1 - right_index
			right_index = self.grid_size[x_or_y] - 1
		return left_index, right_index


	def __generate_bushes(self):
		x_max = self.grid_size[0]
		y_max = self.grid_size[1]
		total_bushes = x_max * y_max / 10
		counter = 0
		while counter < total_bushes:
			coor = [random.randint(0, x_max), random.randint(0, y_max)]
			if coor not in self.bushes:
				self.bushes.append(coor)
				counter += 1
		self.bushes


	def get_frame(self):
		gridmap = []
		for y in range(self.grid_size[1]):
			gridmap.append([])
			for x in range(self.grid_size[0]):
				if [x, y] == self.player_position:
					gridmap[y].append(1)
				elif [x, y] in self.bushes:
					gridmap[y].append(2)
				else:
					gridmap[y].append(0)

		left_index, right_index = self.__calculate_frame_index(1)
		frame = gridmap[left_index:right_index + 1]

		left_index, right_index = self.__calculate_frame_index(0)
		for i in range(len(frame)):
			frame[i] = frame[i][left_index:right_index + 1]

		return frame


	def __check_encounter(self):
		if random.randrange(0, 100, 1) < 20:
			if random.randrange(0, 2, 1) == 0:
				if len(self.film_ids) != 0:
					self.isMoviemonEncountered = True
			else:
				self.isMovieballFound = True


	def go(self, direction):
		if direction == 'left':
			if self.player_position[0] > 0:
				self.player_position[0] -= 1
				self.__check_encounter()
		elif direction == 'right':
			if self.player_position[0] < self.grid_size[0] - 1:
				self.player_position[0] += 1
				self.__check_encounter()
		elif direction == 'up':
			if self.player_position[1] > 0:
				self.player_position[1] -= 1
				self.__check_encounter()
		elif direction == 'down':
			if self.player_position[1] < self.grid_size[1] - 1:
				self.player_position[1] += 1
				self.__check_encounter()


	def pick_movieball(self):
		self.player_movieballs += 1


	def calculate_chance(self, moviemon_id):
		moviemon = self.get_movie(moviemon_id)
		chance = 50 - (round(float(moviemon["imdbRating"])) * 10) \
					+ (self.player_strength * 5)
		if chance < 1:
			chance = 1
		elif chance > 90:
			chance = 90
		return chance


	def throw_movieball(self, target_id):
		if self.player_movieballs > 0:
			self.player_movieballs -= 1
		else:
			raise self.DataManagerException("Lack of movieballs")

		chance = self.calculate_chance(target_id)
		if random.randint(0, 100) < chance:
			self.film_ids.remove(target_id)
			self.captured_moviemons.append(self.get_movie(target_id))
			self.player_strength += 1
			return True

		return False


if __name__ == '__main__':
	manager = DataManager()
	manager.load_default_settings()
	print(manager)

	manager.player_position = [4, 5]
	manager.captured_moviemons.append(manager.get_movie(manager.film_ids[4]))
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
