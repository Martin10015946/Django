from math import sqrt, pow, pi, atan2
from copy import copy
import operator
from os import walk, sep

from gcode import parseline
from nc import list_faces, nc_parser, extend_header

AIR_MOVE_SPEED = 254
TOOL_CHANGE_TIME = 36
FLIP_TIME = 5 * 60
CHANGE_BOARD_TIME = 10 * 60

moves = {
	'airmove': 'G00',
	'opmove': 'G01',
	'G02': 'G02',
	'G03': 'G03',
	}

def readnc(path):
        f = open(path)
        s = f.read()
        f.close()
        return s

def radius(d):
	return sqrt(pow(d['X']-d['I'],2)+pow(d['Y']-d['J'],2))	

def length(p,d):
	return sqrt(pow(d['X']-p['X'],2)+pow(d['Y']-p['Y'],2)+pow(d['Z']-p['Z'],2))

def vecangle(p,d):
	x1 = p['X'] - d['I']
	y1 = p['Y'] - d['J']
	x2 = d['X'] - d['I']
	y2 = d['Y'] - d['J']
	angle = atan2(x1*y2-x2*y1,x1*x2+y1*y2) % (2 * pi) 
	
	return angle

def consolidate(p,d):
	if d.has_key('X') == False:
		d['X'] = p['X'] 
	if d.has_key('Y') == False:
		d['Y'] = p['Y']
	if d.has_key('Z') == False:
		d['Z'] = p['Z']
	if d.has_key('F') == False:
		d['F'] = 166
	
	return d

def measure(face):
	
	nc_string = face
	nc_list = [line for line in nc_string.splitlines() if line.startswith('G') and not line.startswith('G98')]

	prev_X = 0
	prev_Y = 0
	prev_Z = 0
	current_tool = ''
	
	#totals
	air_move = []
	cut_move = []
	
	log = []
	tool_list = []
	
	for line in nc_list:
		p = {'X':prev_X, 'Y':prev_Y, 'Z':prev_Z}
		d = consolidate(p, parseline(line))
	
		# tools logic
		if line.startswith('G00 T'):
			if current_tool != '':
				#dump the tool values
				tool_dict = {current_tool: []}
				tool_dict[current_tool] = [copy(air_move), copy(cut_move)]
				tool_list.append(tool_dict)
				#aknowledge the new tool
				current_tool = line
				air_move = [] 
				cut_move = []
			else:
				current_tool = line
	
		elif line.startswith('G97'):
			pass
	
		else: # start measuring
			if line.startswith(moves['airmove']):
				air_move.append((length(p,d),AIR_MOVE_SPEED))
	
			elif line.startswith(moves['opmove']):
				cut_move.append((length(p,d),d['F']))
		
			# arcs (treated in 2D)
			elif line.startswith('G03') or line.startswith('G02'):
				if [p['X'],p['Y']] == [d['X'],d['Y']]:
					cut_move.append((pi * 2 * radius(d),d['F']))
				else:
					if line.startswith('G03'):
						angle = vecangle(p,d) 
					if line.startswith('G02'):
						angle = (2*pi) - vecangle(p,d) 
					
					cut_move.append((radius(d) * angle,d['F']))
			
			prev_X = d['X']
			prev_Y = d['Y']
			prev_Z = d['Z']
		
	tool_dict = {current_tool: []}
	tool_dict[current_tool] = [copy(air_move), copy(cut_move)]
	tool_list.append(tool_dict)

	return tool_list

def time(tool_list):
	face = []
	total = 0

	def time_coef(l,coef,limit):
		time = round(reduce(operator.add,[x[0] / x[1] for x in l if x[0] > limit],0),2)
		time += round(reduce(operator.add,[x[0] / (x[1] / 100 * coef) for x in l if x[0] < limit],0),2)
		return time

	for tool in tool_list:
		log = {}
		log['Tool # '] = tool.keys()[0].splitlines()[0]
		val = tool.values()
		air_moves = val[0][0]
		cut_moves = val[0][1]
		log['Air moves '] = round(reduce(operator.add,[x[0] for x in air_moves],0),2) 
		log['Air moves time '] = time_coef(air_moves, 100, 150)
		log['Cut moves '] = round(reduce(operator.add,[x[0] for x in cut_moves],0),2)
		log['Cut moves time '] = time_coef(cut_moves, 70, 400)
		face.append(log)
	
	return face 

def time_file(path):
	nc = readnc(path)
	faces = list_faces(nc)
	if len(faces) > 2: faces = faces[:2]
	times = []
	for gcode in faces[:]: 
		tool_list = measure(gcode)
		times.append(time(tool_list))
	
	return times # for each face


def total(path, log=False):
	times = time_file(path)
	facelist = []
	file_total = 0
	for face in times:
		s = ''
		total = 0
		current_tool = 0
		for tool in face:
			key = 'Tool # '
			s += key + tool[key] + '\n'
			tool_number = parseline(tool[key])['T']
			if current_tool != tool_number:
				total += TOOL_CHANGE_TIME
				current_tool = tool_number
			key = 'Air moves '
			s += key + str(tool[key]) + '\n'
			key = 'Air moves time '
			s += key + str(tool[key]) + '\n'
			total += tool[key]
			key = 'Cut moves '
			s += key + str(tool[key]) + '\n'
			key = 'Cut moves time '
			s += key + str(tool[key]) + '\n'
			total += tool[key]
	
		file_total += total
		s += 'Face total time ' + str(total) + '\n'
		facelist.append(s)
	
	#print len(times)
	if len(times) == 2:
		file_total += FLIP_TIME
	if len(times) == 4:
		file_total += 2 * FLIP_TIME
		file_total += CHANGE_BOARD_TIME
	
	facelist.append('\nFile total time: ' + str(file_total) + '\n')
	
	if log == True:
		f = open('time_log.txt', 'w')
		f.write('\n\n'.join(facelist))
		f.close()
	
	return file_total / 60

def filter_folder(path):
	def get_list(path):
		"""returns a list of files in a directory tree"""
		l=[]
		for item in walk(path):
			for filenames in item[2]:
				#include a test to verify that the files are NC?
				l.append(item[0]+sep+filenames)
		
		return l
	
	for nc_file in get_list(path):
		f = open(nc_file)
		nc_string = f.read()
		f.close()
		nc = nc_parser(nc_string)
		header = nc.header()
		if header.has_key('Duration'):
			duration = int(round(float(header['Duration']),0))
			if header.has_key('Start time'):
				start = header['Start time']
				ticked = True
			else:
				start = next_start_time
				ticked = False
		else:
			duration = total(nc_file)	
			extend_header(nc_file,{'Duration': str(duration)})

