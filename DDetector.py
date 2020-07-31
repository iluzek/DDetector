# =============================================================================
# Section: Library Imports 
# =============================================================================
import os, sys, argparse, math, random
from datetime import datetime
# =============================================================================
# Section: Parser Initialisation
# =============================================================================
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
# =============================================================================
# Section: Argparse Validation Functions
# =============================================================================
# =============================================================================
# Name:       validate_target(path_string)
# Arguments:  path_string = string input from the user to analyse
# Purpose:    Returns a valid path value or raises error
# =============================================================================
def validate_target(system_path):
	# TODO make this hack work with drives in windows and Linux
	if "/dev/sd" in system_path:
		return system_path
	# Check if system_path is a file
	elif os.path.isfile(system_path):
		return system_path
	else:
		raise argparse.ArgumentTypeError('\n>>>>> Provided target is not a valid file!\n')
# =============================================================================
# Name:       validate_target(path_string)
# Arguments:  path_string = string input from the user to analyse
# Purpose:    Returns a valid path value or raises error
# =============================================================================
def validate_block_size(bs_value):
	# Check if bs value is correct (mu)
	# Block Size used: 1B, 512B, 1KB, 2KB, 4KB, 8KB
	bs_value = bs_value.upper()

	if (bs_value == "8KB" or bs_value == "8K" or bs_value == "8192"):
		return (1024 * 8)
	elif bs_value == "4KB" or bs_value == "4K" or bs_value == "4096":
		return (1024 * 4)
	elif bs_value == "2KB" or bs_value == "2K" or bs_value == "2048":
		return (1024 * 2)
	elif bs_value == "1KB" or bs_value == "1K" or bs_value == "1024":
		return (1024 * 1)
	elif bs_value == "512B" or bs_value == "512":
		return (512)
	elif bs_value == "1B" or bs_value == "1":
		return (1)
	else:
		# Return default block size 4K
		return (1024 * 4)
# =============================================================================
# Name:       validate_target(path_string)
# Arguments:  path_string = string input from the user to analyse
# Purpose:    Returns a valid path value or raises error
# =============================================================================
def validate_frequency(number):
	try:
		num = float(number)
		if (0 <= num <= 100):
			return num
		else:
			raise argparse.ArgumentTypeError('\n>>>>> Provided value is not number between 0-100!\n')
	except:
		raise argparse.ArgumentTypeError('\n>>>>> Provided value is not a number (float or integer)!\n')
# =============================================================================
# Argument Name:    target
# Argument Type:    argument value
# Functionality:    Receives target file or directory or recursive directory.
# =============================================================================
#region ArgParse Arguments
parser.add_argument("target", metavar='system_path', type=validate_target,
help="""
===============================================================================
'DDector.py file_path'          	- Detects data in the specified file 
===============================================================================           
""")
# =============================================================================
# =============================================================================
# Argument Name:    -block_size 
# Argument Type:    argument value
# Functionality:    Receives hash_type
# =========================================================================
parser.add_argument("-bs","--block_size", metavar='block_size', type=validate_block_size,
help="""
===============================================================================
'DDector.py file_path -bs value'	- Values: 1B, 512B, 1KB, 2KB, 4KB, 8KB
===============================================================================

""")
parser.add_argument("-f","--frequency", metavar='frequency', type=validate_frequency,
help="""
===============================================================================
'DDector.py file_path -f value'	- Values: 1-100 as percentage of blocks.
===============================================================================

""")
# =============================================================================
# Argument Name:    -d
# Argument Type:    flag
# Functionality:    Toggles ON recursive mode for file discovery.
# =============================================================================
parser.add_argument("-d", "--device", action='store_true',
help="""
===============================================================================
'DDector.py file_path -d'        - Treats device path as a valid
===============================================================================

""")
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
def generate_comparison_blocks(file_size,block_size):

	full_blocks, part_block_bytes = divmod(file_size, block_size)

	# byte of 0 is [0x00] while byte of 1's is [0xFF] or alternatively [0] and [255] since it's cast to bytes object.
	block_zeros 		= generate_block([0],block_size)
	block_ones 			= generate_block([255],block_size)
	block_part_zeros 	= generate_block([0],part_block_bytes)
	block_part_ones 	= generate_block([255],part_block_bytes)

	return (block_zeros,block_ones,block_part_zeros,block_part_ones)
# =============================================================================
def fetch_block(target, offset, bs):
	with open(target, "rb") as f:
		f.seek(offset)
		byte_block = f.read(bs)
		return byte_block
# =============================================================================
def compare_blocks(data_block, zeros_block, ones_block):
	# return 1 or 0 or -1
	if (data_block == zeros_block):
		return (0)
	elif(data_block == ones_block):
		return (1)
	else:
		return (-1)
# =============================================================================

def block_selection(max_block_checks, frequency):

	block_id_list = [*range(1, max_block_checks+1)] # generates a list from 1 to max block checks + 1 as range ignores last value
	sample_size = math.ceil(max_block_checks * (frequency/100))

	selected_sample = random.sample(block_id_list, sample_size) # this works to pick numbers
	selected_sample.sort()

	return selected_sample
# =============================================================================

def inspect_blocks(target, file_size, selected_blocks, block_size, last_block_size, max_block_checks):


	block_zeros,block_ones,block_part_zeros,block_part_ones = generate_comparison_blocks(file_size,block_size)

	inspected_blocks_results = []
	print("Blocks to be checked: " + str(len(selected_blocks)))
	print("First block number: " + str(selected_blocks[0]))
	print("Last block number: " + str(selected_blocks[-1]))


	# Determine block starting offset
	for item in selected_blocks:
		print("Current block number: " + str(item), end='')
		# block offset starts with (num - 1) * bs + 1 ends at block side * num
		block_offset = (item - 1) * block_size + 1

		# If the last/partial block
		if (item == max_block_checks):
			# alter block size to match the size of the last block (remainder)
			current_block = fetch_block(target, block_offset, last_block_size)
			inspected_blocks_results.append(compare_blocks(current_block, block_part_zeros, block_part_ones))
		else:
			current_block = fetch_block(target, block_offset, block_size)
			inspected_blocks_results.append(compare_blocks(current_block, block_zeros, block_ones))
		print('\r', end='')
	return inspected_blocks_results
# =============================================================================
def output_results(block_results, block_size):

	result_len = len(block_results)
	zeros_count = block_results.count(0)
	ones_count = block_results.count(1)
	mixed_count = block_results.count(-1)

	print("\n")
	print ("Out of "+str(result_len)+" checked blocks with block size of: "+ str(block_size)+" bytes.\n"
		"\nZeros block count: " + str(zeros_count) +
		"\nOnes block count: " + str(ones_count) +
		"\nMixed block count: " + str(mixed_count))
	print("\n")
# =============================================================================
# =============================================================================
# Name:       run_app
# Purpose:    starts off all required funcitions.
# =============================================================================	
def run_app():
	args = parser.parse_args()
	# ================================================
	target = args.target
	file_size = os.path.getsize(target)
	#file_size = 1000204886016
	#file_size = 100020000
	#file_size = 10737418240
	block_size = validate_block_size(str(args.block_size))
	last_block_size = file_size % block_size
	max_block_checks = math.ceil(file_size/block_size)
	frequency = args.frequency
	# ================================================
	selected_blocks = block_selection(max_block_checks, frequency) 
	# ================================================

	# an array of numbers indicating blocks selected in order by block size
	inspected_blocks_results = inspect_blocks(target, file_size, selected_blocks, block_size, last_block_size, max_block_checks)

	output_results(inspected_blocks_results, block_size)

# =============================================================================
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
