import math, string, sys

class Puzzle:
	''' Identifies a 9x9 sudoku puzzle grid by name.'''
	def __init__(self, name, sdku):
		self.name = name
		self.sudoku = sdku

def load_file(filename):
	''' Opens a file that contains a list of puzzles, separated by names. '''
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
	''' Converts a 9x9 sudoku puzzle list into a printable format. '''
	return '\n'.join([''.join([ y and str(y) or ' ' for y in x]) for x in sdku])
  
def to_sudoku(txt):
	''' Converts a 9-line, 9-column block of text into a sudoku puzzle list. '''
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
	''' Counts the number of times a particular value appears in a list. '''
	return len([x for x in lst if x == val])

def flatten(lst_of_lst):
	''' Flattens a list of lists into a set of unique values. '''
	result = []
	for lst in lst_of_lst:
		for i in lst:
			if not i in result:
				result.append(i)
	return result

def is_failed(sdku):
	''' Tests whether a sudoku puzzle grid is in a failed state by determining whether there are any rows, columns, or groups missing a possible number. '''
	possibles = calculate_possibles(sdku)

	for i in range(0, 9):
		possible_cols = flatten(get_col(possibles, i))
		possible_rows = flatten(possibles[i])
		possible_grp = flatten(get_group_by_number(possibles, i))
		for n in range(1, 10):
			if n not in possible_cols:
				return True
			if n not in possible_rows:
				return True
			if n not in possible_grp:
				return True
	return False

def is_solved(sdku):
	''' Tests whether a sudoku puzzle grid is fully solved. '''
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

def get_group_by_number(sdku, index):
	''' Returns a group based on an index, where 0 = the top left corner and 8 = the bottom right corner. '''
	row = math.floor(index / 3.0)
	col = index % 3
	
	result = []
	for y in range(row * 3, (row+1) * 3):
		for x in range(col * 3, (col+1) * 3):
			result.append(sdku[y][x])
			
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
				possibles.sort()
						
			result_row.append(possibles)
			
		result.append(result_row)
		
	has_changed = True
	while has_changed:
		has_changed = False
		for i in range(0, 9):
			if remove_row_multiples(result[i]):
				has_changed = True
			if remove_col_multiples(result, i):
				has_changed = True
			if remove_group_multiples(result, i):
				has_changed = True
			
		
	return result

def remove_row_multiples(row_possibles):
	''' For any N rows that have exactly the same set of possibles, remove from all other possibles in that set. '''
	duplicates = [x for x in row_possibles if value_count(row_possibles, x) == len(x) and len(x) > 1]
	
	if not duplicates:
		return False
		
	has_changed = False
	for possibles in row_possibles:
		for d in duplicates:
		
			if possibles == d:
				continue
		
			for n in d:
				if n in possibles:
					possibles.remove(n)
					has_changed = True
					
	return has_changed

def remove_col_multiples(possibles, col):
	''' For any N columns that have exactly the same set of possibles, remove from all other possibles in that set. '''
	col_possibles = get_col(possibles, col)
	duplicates = [x for x in col_possibles if value_count(col_possibles, x) == len(x) and len(x) > 1]
	
	if not duplicates:
		return False
		
	has_changed = False
	for row in range(0, 9):
		for d in duplicates:
		
			if possibles[row][col] == d:
				continue
		
			for n in d:
				if n in possibles[row][col]:
					possibles[row][col].remove(n)
					has_changed = True
					
	return has_changed
	
def remove_group_multiples(possibles, grp):
	''' For any N group items that have exactly the same set of possibles, remove from all other possibles in that set. '''
	grp_possibles = get_group_by_number(possibles, grp)
	duplicates = [x for x in grp_possibles if value_count(grp_possibles, x) == len(x) and len(x) > 1]
	
	if not duplicates:
		return False
		
	row = math.floor(grp / 3.0)
	col = grp % 3
	
	has_changed = False
	for y in range(row * 3, (row+1)	* 3):
		for x in range(col * 3, (col+1) * 3):
			for d in duplicates:
			
				if possibles[y][x] == d:
					continue
				
				for n in d:
					if n in possibles[y][x]:
						possibles[y][x].remove(n)
						has_changed = True
						
	return has_changed

def try_guess(sdku):
	''' Takes the first square that has only two possible values, picks one, resolves the rest, and tests for failure.

	If successful, returns the resulting puzzle grid. If failed, returns a puzzle grid with the other value inserted.'''
	work = sdku.copy()
	possibles = calculate_possibles(work)

	if not [x for x in flatten(possibles) if len(x) == 2]:
		return work

	for y in range(0, 9):
		for x in range(0, 9):
			if len(possibles[y][x]) == 2:
				work[y][x] = possibles[y][x][0]
				work = solve(work)

				if is_failed(work):
					work = sdku.copy()
					work[y][x] = possibles[y][x][1]

	work = solve(work)

	return work

			
def solve(sdku):
	''' Solves a partially finished sudoku puzzle grid by executing the following until no further changes have been made:

	1. Caclulate possible values for each square, based on the values in the row, column, and group.
	2. Process each square in the working copy:
		2a. If there is only one possible choice for a square, set it in the working copy.
		2b. If there is a possible value that doesn't appear elsewhere in the row, column, or group, set it in the working copy.
	
	If the puzzle is not solved by the time the loop exits, find the first square with only 2 possibilities and test each possibility
	recursively, returning the result.'''
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

	if not is_solved(work) and not is_failed(work):
		work = try_guess(work)

	return work
			
print("File: %s" % sys.argv[1])

count = 0
for p in load_file(sys.argv[1]):
	count += 1
	solved = solve(p.sudoku)
	print(p.name)
	print("Solved: %s" % (is_solved(solved)))
	print("Failed: %s" % (is_failed(solved)))
	print(to_text(solved))
	print('')
