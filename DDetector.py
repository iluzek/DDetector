# =============================================================================
# Section: Library Imports 
# =============================================================================
import os, sys, argparse, math, random, time
from datetime import datetime
# =============================================================================
# Section: Global values
# =============================================================================
startTime = datetime.now()

block_size = 4096   # Default block size to be used if no bs value is supplied
last_block_size = None
default_count = True# Default set to True for check count over frequency
check_count = 100   # Default checks if no values are supplied
frequency = 0.001   # Where 1 is 100%, 0.1 is 10%, 0.01 is 1% and 0.001 is 0.1%

target_path = None
target_size = None  # Size of the target in bytes
sample_blocks = []  # List of id's for selected sample blocks

focused = None		# Type of focus applied to the scan (beginning(1),middle(2),end(3))
# =============================================================================
# Section: Parser Initialisation
# =============================================================================
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
check_types_group = parser.add_mutually_exclusive_group()

# =============================================================================
# Section: Argparse Validation Functions
# =============================================================================
# =============================================================================
# Name:       validate_target(path_string)
# Arguments:  path_string = string input from the user to analyse
# Purpose:    Returns a valid path value or raises error
# =============================================================================
def validate_target(data_path):
	# This should work for files and devices..just need to exclude directories
	if (os.path.exists(data_path)):
		if (os.path.isdir(data_path)):
			raise argparse.ArgumentTypeError('\n>>>>> Provided target is not a valid file or data device!\n')
		else:
			return data_path
# =============================================================================
def validate_frequency(frequency):
	try:
		num = float(frequency)
		if (0 <= num <= 1):
			return num
		else:
			raise argparse.ArgumentTypeError('\n>>>>> Provided value is not a float between 0-1!\n')
	except:
		raise argparse.ArgumentTypeError('\n>>>>> Provided value is not a float!\n')
# =============================================================================
def validate_check_count(checks_wanted):
	try:
		num = int(checks_wanted)
		return num
	except:
		raise argparse.ArgumentTypeError('\n>>>>> Provided value is not an integer!\n')
# =============================================================================
def validate_block_size(bs_value):
	# Check if bs value is correct (mu)
	# Block Size used: 512B, 1KB, 2KB, 4KB, 8KB

	# TODO make it so it recognises K, M etc values automatically
	bs_value = bs_value.upper()

	if (bs_value == "8KB" or bs_value == "8K" or bs_value == "8192"):
		return (8192)
	elif bs_value == "4KB" or bs_value == "4K" or bs_value == "4096":
		return (4096)
	elif bs_value == "2KB" or bs_value == "2K" or bs_value == "2048":
		return (2048)
	elif bs_value == "1KB" or bs_value == "1K" or bs_value == "1024":
		return (1024)
	elif bs_value == "512B" or bs_value == "512":
		return (512)
	else:
		# Return default block size 4K
		return (4096)
# =============================================================================
def validate_focused(focus_range):
	raise argparse.ArgumentTypeError('\n>>>>> Argument not yet implemented!!\n')
# =============================================================================
# Argument Name:    target
# Argument Type:    argument value
# Functionality:    Receives target file or directory or recursive directory.
# =============================================================================
#region ArgParse Arguments
parser.add_argument("target", metavar='system_path', type=validate_target,
help="""
===============================================================================
'DDector.py file_path'          Detects data in the specified file 
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
'DDector.py file_path -bs value'    Value: 512B, 1KB, 2KB, 4KB, 8KB
===============================================================================

""")
check_types_group.add_argument("-f","--frequency", metavar='frequency', type=validate_frequency,
help="""
===============================================================================
'DDector.py file_path -f value'     Value: 1-100 as percentage of blocks.
===============================================================================

""")
check_types_group.add_argument("-c","--count", metavar='count', type=validate_check_count,
help=""" 
===============================================================================
'DDector.py file_path -c value'     Value: Number of blocks to be checked.
===============================================================================
""")
parser.add_argument("--focused", metavar='range', type=validate_focused,
help=""" 
===============================================================================
'DDector.py file_path -f value'     Value: 0B-1GB, 512MB-320GB
===============================================================================
""")
# =============================================================================
def get_target_size(targe_path):
	# Get the file size by seeking at end
	opened_file = os.open(targe_path, os.O_RDONLY)
	try:
		return os.lseek(opened_file, 0, os.SEEK_END)
	finally:
		os.close(opened_file)

# =============================================================================
def fetch_block(target, offset, bs):
	with open(target, "rb") as f:
		f.seek(offset)
		byte_block = f.read(bs)
		return byte_block
# =============================================================================

def check_mode(frequency, count):
	# If both frequency and count come back as None, count mode used
	if ((frequency == None) and (count == None)):
		return True
	# If frequnency is None, user selected count, count mode used
	elif (frequency == None):
		return True
	# If count is None, user selected freuency, frequency mode used
	elif (count == None):
		return False
# =============================================================================
def block_selection(max_block_checks):

	#check_count if default true else calculates frequency value
	if default_count:
		sample_size = check_count
	else:
		sample_size = min(math.ceil(max_block_checks*frequency), max_block_checks)

	selected_sample = random.sample(range(1,max_block_checks+1),sample_size)
	selected_sample.sort()

	return selected_sample

# =============================================================================
'''
# This might be a version of focused search. Not yet sure.
def block_selection(max_block_checks):


	blocks_range_begining= [1,math.floor((max_block_checks/3)*1)]
	blocks_range_middle = [math.floor((max_block_checks/3)*1+1), math.floor((max_block_checks/3)*2)]
	blocks_range_end = [math.floor((max_block_checks/3)*2), max_block_checks]

	sample_size = None

	if focused == None:
		pass
	if focused == 1:
		pass
		# Max block within sector + outside?
	if focused == 2:
		pass
	if focused == 3:
		pass

	# Picks smaller number between max_block_checks and sample_size.
	# Picks check_count if default true else calculates frequency value

	if default_count:
		sample_size = check_count
	else:
		sample_size = min(math.ceil(max_block_checks*frequency), max_block_checks)
	
	selected_sample = random.sample(range(1,max_block_checks),sample_size)
	selected_sample.sort()

	return selected_sample
'''
# =============================================================================
def compare_blocks(block):
	result = all(byte == block[0] for byte in block)
	# If all values inside the block are equal to the initial byte - return that byte in form of int number
	if (result):
		return int(block[0])
	# If values inside the block are not equal to the initial byte - return -1 to indicate mixed data
	else:
		return -1

	# Return 0		for 0
	# Return 255	for 11111111
	# Return 85		for 01010101
	# Return 170	for 10101010
	# Return 0-255 for custom data

def inspect_blocks(selected_blocks, max_block_checks):

	block_check_numbers = len(selected_blocks)

	current_block_num = 1
	current_block = None

	inspected_blocks_results = []

	# Determine block starting offset
	for item in selected_blocks:
		print("All blocks being checked: {0}	Current block checked: {1}".format(block_check_numbers,current_block_num), end='')
		
		# block offset starts with (num - 1) * bs + 1 ends at block side * num
		block_offset = (item - 1) * block_size + 1

		# If the last block(possibly partial) 
		if (item == max_block_checks):
			# alter block size to match the size of the last block (remainder)
			current_block = fetch_block(target_path, block_offset, last_block_size)
		else:
			current_block = fetch_block(target_path, block_offset, block_size)

		inspected_blocks_results.append(compare_blocks(current_block))

		current_block_num += 1
		print('\r', end='')

	print("\n=====================================================================")
	return inspected_blocks_results

def analyse_samples(inspected_blocks_results):
	print("Blocks filled with 00000000:		"+ str(inspected_blocks_results.count(0)))
	print("Blocks filled with 11111111:		"+ str(inspected_blocks_results.count(255)))
	print("Blocks filled with 01010101:		"+ str(inspected_blocks_results.count(85)))
	print("Blocks filled with 10101010:		"+ str(inspected_blocks_results.count(170)))
	print("Blocks filled with mixed data:		"+ str(inspected_blocks_results.count(-1)))
	print("=====================================================================")
# =============================================================================
# Name:       run_app
# Purpose:    starts off all required funcitions.
# ============================================================================= 
def print_settings(max_block_checks, selected_blocks):

	block_check_numbers = len(selected_blocks)
	print("=====================================================================")
	print("Data path is:			" + str(target_path))
	print("File size in bytes:		" + str(target_size))
	print("Block size in bytes:		" + str(block_size))
	print("Total blocks number:		" + str(max_block_checks))
	print("=====================================================================")
	print("Blocks to be checked:		" + str(block_check_numbers))
	print("First block number:		" + str(selected_blocks[0]))
	print("Last block number:		" + str(selected_blocks[-1]))
	print("=====================================================================")

def run_app():
	global block_size, last_block_size, target_path, target_size,check_count, frequency, default_count, focused
	args = parser.parse_args()

	# Settings
	target_path = args.target
	target_size = get_target_size(target_path)
	block_size = args.block_size if args.block_size != None else block_size
	remainder_block = target_size % block_size
	last_block_size = remainder_block if remainder_block != 0 else block_size
	focused = args.focused
	
	print("Target Path: "+str(target_path))
	print("Target Size: "+str(target_size))
	print("Block Size: "+str(block_size))
	print("Last Block Size: "+str(last_block_size))
	
	# Check default input values
	default_count = check_mode(args.frequency, args.count)
	
	# Adjust values that are gonna be used so that math issues do not occur due to None Type
	check_count = args.count if args.count != None else check_count
	frequency = args.frequency if args.frequency != None else frequency

	boundries = ["start","finish"]


	# checks how many blocks full and partial fit into target based on block size specified
	max_block_checks = math.ceil(target_size/block_size)
	
	# generates array of block id's to be checked
	selected_blocks = block_selection(max_block_checks)
	print(max_block_checks)
	
	print_settings(max_block_checks, selected_blocks)
	# inspected blocks are compared to blocks of 0's, 1's and checked if they match
	inspected_blocks_results = inspect_blocks(selected_blocks, max_block_checks)

	analyse_samples(inspected_blocks_results)

# =============================================================================
# Name:       main
# Purpose:    Starts runApp() and listens for keyboard interrupt to end script
# =============================================================================
if __name__ == '__main__':
	try:
		run_app()
	except KeyboardInterrupt:
		import sys
		print("\n\n{*} User Requested An Interrupt!")
		print("{*} Application Shutting Down.")
		print("Program interrupted after: " + str(datetime.now() - startTime)+"\n\n")
		sys.exit(1)
		
	print("\nProgram finished after: " + str(datetime.now() - startTime)+"\n\n")
# =============================================================================
