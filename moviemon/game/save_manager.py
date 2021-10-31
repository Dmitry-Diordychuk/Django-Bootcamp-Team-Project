from os import listdir, remove
from os.path import isfile
from os.path import isfile, join
import re

class SaveManager():
	def __init__(self):
		path = __file__
		path = path.replace('/game/save_manager.py', '')
		self.dir = path + '/saved_game'
		self.slot_a_file = None
		self.slot_b_file = None
		self.slot_c_file = None
		self.slot_a_status = "Free"
		self.slot_b_status = "Free"
		self.slot_c_status = "Free"

		self.update_files()


	def update_files(self):
		flag_a = False
		flag_b = False
		flag_c = False
		files = [f for f in listdir(self.dir) if isfile(join(self.dir, f))]
		for f in files:
			if re.match(r'slot[abc]_\d+_\d+\.mmg', f):
				parts = f.split('_')
				if parts[0] == 'slota':
					self.slot_a_file = f
					self.slot_a_status = parts[1] + '/' + parts[2].split('.')[0]
					flag_a = True
				elif parts[0] == 'slotb':
					self.slot_b_file = f
					self.slot_b_status = parts[1] + '/' + parts[2].split('.')[0]
					flag_b = True
				elif parts[0] == 'slotc':
					self.slot_c_file = f
					self.slot_c_status = parts[1] + '/' + parts[2].split('.')[0]
					flag_c = True
			if flag_a == False:
				self.slot_a_file = None
				self.slot_a_status = 'Free'
			if flag_b == False:
				self.slot_b_file = None
				self.slot_b_status = 'Free'
			if flag_c == False:
				self.slot_c_file = None
				self.slot_c_status = 'Free'


	def save(self, slot, catched, total, data):
		if slot == 'a' and self.slot_a_file != None:
			remove(join(self.dir, self.slot_a_file))
		elif slot == 'b' and self.slot_b_file != None:
			remove(join(self.dir, self.slot_b_file))
		elif slot == 'c' and self.slot_c_file != None:
			remove(join(self.dir, self.slot_c_file))
		with open(
			join(
				self.dir,
				'slot' + slot + '_' + str(catched) + '_' + str(total) + '.mmg'
			),
			'wb'
		) as f:
			f.write(data)
		self.update_files()


	def load(self, slot):
		if slot == 'a':
			if self.slot_a_file == None:
				return None
			with open(join(self.dir, self.slot_a_file), 'rb') as f:
				self.update_files()
				return f.read()
		elif slot == 'b':
			if self.slot_b_file == None:
				return None
			with open(join(self.dir, self.slot_b_file), 'rb') as f:
				self.update_files()
				return f.read()
		elif slot == 'c':
			if self.slot_c_file == None:
				return None
			with open(join(self.dir, self.slot_c_file), 'rb') as f:
				self.update_files()
				return f.read()
		self.update_files()
		return None



if __name__ == '__main__':
	save_manager = SaveManager()
	save_manager.save('a', 1, 15, 'test_a')
	data = save_manager.load('a')
	print(data)
