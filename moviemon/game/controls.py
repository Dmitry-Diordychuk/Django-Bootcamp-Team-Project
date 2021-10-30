
def buttons_handler(
		events,
		left_button_handler=None,
		right_button_handler=None,
		up_button_handler=None,
		down_button_handler=None,
		a_button_handler=None,
		b_button_handler=None,
		start_button_handler=None,
		select_button_handler=None
	):
	if events.get('left.x'):
		if left_button_handler != None:
			return left_button_handler()
	elif events.get('right.x'):
		if right_button_handler != None:
			return right_button_handler()
	elif events.get('up.x'):
		if up_button_handler != None:
			return up_button_handler()
	elif events.get('down.x'):
		if down_button_handler != None:
			return down_button_handler()
	elif events.get('A'):
		if a_button_handler != None:
			return a_button_handler()
	elif events.get('B'):
		if b_button_handler != None:
			return b_button_handler()
	elif events.get('select'):
		if select_button_handler != None:
			return select_button_handler()
	elif events.get('start'):
		if start_button_handler != None:
			return start_button_handler()
	return None
