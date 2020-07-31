# =============================================================================
# Section: Library Imports 
# =============================================================================
from datetime import datetime

def save_to_file(path, pattern):
	f = open(path, 'wb')
	binary_format = bytearray(pattern)
	f.write(binary_format)
	f.close()
    
# =============================================================================
def generate_block(value,bs):
	# Fills out bytes value in this case [0x00] and [0xFF] bytes to block size 
	# Can also take value as [0] or [255] and casts it into single byte object.
	try:
		block = bytes(value * bs)
	except ValueError as verr:
		print("Generating block failed because: "+ str(value)+" is not convertible to byte object")
		sys.exit()
	except Exception as ex:
		print("Generating block failed because: Exception occurred while converting to byte object")
		sys.exit()

	return block
# =============================================================================
def get_pattern(pattern_type, length):

	byte_data = []

	if pattern_type == 'zero':
		# [00000000] = 0
		byte_data = generate_block([0],length)
	elif pattern_type == 'one':
		# [11111111] = 255
		byte_data = generate_block([255],length)
	elif pattern_type == 'zero_one':
		# [01010101] = 85
		byte_data = generate_block([85],length)
	elif pattern_type == 'one_zero':
		# [10101010] = 170
		byte_data = generate_block([170],length)
	else:
		pass

	return byte_data
# =============================================================================
def run_app():
	pattern = get_pattern('zero', 1024*1024)
	path = "F:\\scripts\\scripts\\00000000_1M.raw"
	save_to_file(path, pattern)

	pattern = get_pattern('one', 1024*1024)
	path = "F:\\scripts\\scripts\\11111111_1M.raw"
	save_to_file(path, pattern)

	pattern = get_pattern('one_zero', 1024*1024)
	path = "F:\\scripts\\scripts\\10101010_1M.raw"
	save_to_file(path, pattern)

	pattern = get_pattern('zero_one', 1024*1024)
	path = "F:\\scripts\\scripts\\01010101_1M.raw"
	save_to_file(path, pattern)
# =============================================================================
# Name:       main
# Purpose:    Starts runApp() and listens for keyboard interrupt to end script
# =============================================================================
if __name__ == '__main__':
	startTime = datetime.now()
	try:
		run_app()
	except KeyboardInterrupt:
		import sys
		print("\n\n{*} User Requested An Interrupt!")
		print("{*} Application Shutting Down.")
		time_delta = datetime.now() - startTime
		print("Program interrupted after: " + str(time_delta))
		sys.exit(1)
		
	time_delta = datetime.now() - startTime
	print("Program finished after: " + str(time_delta))
# =============================================================================
