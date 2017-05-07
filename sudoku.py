import math, string, sys

class Puzzle:
	def __init__(self, name, sdku):
		self.name = name
		self.sudoku = sdku

def load_file(filename):
	# Open file and read all lines
	f = open(filename, 'r')
	lines = f.read().replace('\r\n','\n').split('\n')
	f.close()
	lines.reverse()

	puzzles = []

	# Parse into 10-line chunks
	while lines and len(lines) >= 10:
		name = lines.pop().replace('---------','')
		txt = []
		for i in range(0, 9):
			txt.append(lines.pop())
		puzzles.append(Puzzle(name, to_sudoku('\n'.join(txt))))

	return puzzles
		

def to_text(sdku):
	return '\n'.join([''.join([ y and str(y) or ' ' for y in x]) for x in sdku])
  
def to_sudoku(txt):
	result = []
	
	lines = txt.split('\n')
	
	for line in lines:
		row = []
		
		for c in line:
			if c == ' ':
				row.append(None)
			else:
				row.append(int(c))
		while (len(row) < 9):
			row.append(None)
			
		result.append(row)
	return result

def value_count(lst, val):
	return len([x for x in lst if x == val])

def is_solved(sdku):
	# Test that no empty cells exist and sanity check each row
	for row in sdku:
		for cell in row:
			if not cell:
				return False
		for n in range(1, 10):
			if value_count(row, n) != 1:
				return False
	
	# Sanity check each column
	for col in range(0, 9):
		col_values = get_col(sdku, col)
		for n in range(1, 10):
			if value_count(col_values, n) != 1:
				return False

	# Sanity check each group
	for grpX in range(0, 3):
		for grpY in range(0, 3):
			grp_values = get_group(sdku, grpX*3, grpY*3, True)
			for n in range(1, 10):
				if value_count(grp_values, n) != 1:
					return False

	return True

def get_col(sdku, x):
	'''Get all values in the given column from the given 9x9 array'''
	result = []
	for row in sdku:
		result.append(row[x])
	return result
	
def collect_sets(lst):
	'''Merge a list of lists into a single list.'''
	result = []
	for l in lst:
		for i in l:
			if not i in result:
				result.append(i)
	return result
	
def get_group(sdku, x, y, includeCell):
	'''Given a 9x9 array, retrieve the 3x3 grouping that contains the given cell. '''
	result = []

	x_group = math.floor(x / 3.0)
	y_group = math.floor(y / 3.0)
	
	min_x = x_group * 3
	max_x = (x_group + 1) * 3
	
	min_y = y_group * 3
	max_y = (y_group + 1) * 3
	
	for row in range(min_y, max_y):
		for cell in range(min_x, max_x):
			if not includeCell and (row == y and cell == x):
				continue
			if not sdku[row][cell] in result:
				result.append(sdku[row][cell])
	
	return result

def calculate_possibles(sdku):
	'''Returns a new 9x9 array that contains all of the possible sudoku values for each cell in the given grid.'''
	result = []
	
	for row in range(0, 9):
		result_row = []
	
		for col in range(0, 9):
		
			# If space is solved, it's the only possible value
			if sdku[row][col]:
				possibles = [sdku[row][col]]
			# Otherwise, remove all numbers that don't exist in the same column, row, or grouping
			else:
				impossibles = sdku[row] + get_col(sdku, col) + get_group(sdku, col, row, False)
				possibles = [x for x in range(1, 10) if not x in impossibles]
						
			result_row.append(possibles)
			
		result.append(result_row)
	return result
	
			
def solve(sdku):
	work = sdku.copy()
	
	has_changed = True
	while has_changed:
		has_changed = False
		
		possibles = calculate_possibles(work)
				
		for row in range(0, 9):
			for col in range(0, 9):
			
				# If we've already solved a square
				if work[row][col]:
					continue
				
				# If there is only one possible choice for a square...
				if len(possibles[row][col]) == 1:
					has_changed = True
					work[row][col] = possibles[row][col][0]
				else:
					# Number is only possible in square vs. row/col/group
					row_possibles = collect_sets(possibles[row])
					col_possibles = collect_sets(get_col(possibles, col))
					grp_possibles = collect_sets(get_group(possibles, col, row, False))

					
					
					for n in possibles[row][col]:
						if (n not in row_possibles) or (n not in col_possibles) or (n not in grp_possibles):
							has_changed = True
							work[row][col] = n
							break
		
		
	
	return work
			
print("File: %s" % sys.argv[1])

count = 0
for p in load_file(sys.argv[1]):
	count += 1
	solved = solve(p.sudoku)
	print(p.name)
	print("Solved: %s" % (is_solved(solved)))
	print(to_text(solved))
	print('')
