from gcode import parseline, odict2str
from nc import nc_parser, list_boards
try:
    import cairo
except:
    pass
import sys
from os.path import basename, sep
from math import radians, sqrt, pow
from wx import Point2D
from PIL import Image, ImageDraw, ImageFont

OURGREY = 0.75

log= []
moves = {'airmove': 'G00','opmove': 'G01',
                    'G02': 'G02','G03': 'G03'}
DATA_PATH = sys.path[0] + sep + '..' + sep

def reverse_y(line):
    try:
        d = parseline(line)
        if d.has_key('Y'): d['Y'] = 1224 - d['Y']
        if d.has_key('J'): d['J'] = 1224 - d['J']
        return d
    except:
        return None

def draw_gcode(previous_line, current_line, grey_lines=False):
    """Decides whether to draw an air move / cut 
    / arc cw / arc ccw."""

    d = current_line
    p = previous_line 

    def radius():
        return sqrt(pow(p['X']-d['I'],2)+pow(p['Y']-d['J'],2))  

    def angle(i):
        if i == 1:
            angle = Point2D(p['X']-d['I'], p['Y']-d['J']).GetVectorAngle()
            return radians(angle)   
        elif i == 2:
            angle = Point2D(d['X']-d['I'], d['Y']-d['J']).GetVectorAngle()
            return radians(angle)   
    
    line = odict2str(d)

    if grey_lines: col = OURGREY 
    else: col = 0

    if line.startswith(moves['airmove']) and d.has_key('X'):
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(p['X'], p['Y'])
        cr.line_to(d['X'], d['Y'])
    elif line.startswith(moves['opmove']):
        cr.set_source_rgb(col, col, col)
        cr.move_to(p['X'], p['Y'])
        cr.line_to(d['X'], d['Y'])
    elif line.startswith('G03'):
        cr.set_source_rgb(col, col, col)
        cr.arc_negative(d['I'], d['J'], radius(), angle(1), angle(2))
    elif line.startswith('G02'):
        cr.set_source_rgb(col, col, col)
        cr.arc(d['I'], d['J'], radius(), angle(1), angle(2))

def clean_title(s):
    '''Clean the string printed in the canvas'''
    s = s.replace('.nc','')
    s = s.replace('.jpg','')
    s = s.replace('_',' ')
    return s

def split_title(s):
    '''...into material and name for lamination 
    list purpose.'''
    bs = s.split('-')
    if len(bs) >= 3:
        return '-'.join(bs[:2]), '-'.join(bs[2:]).strip()
    else:
        return s, ''

def draw_face(face, image_path, duration, grey_background=False, grey_lines=False):
    """face is a list of strings"""

    fname = basename(image_path).split('_board')[0]
    material, title = split_title(clean_title(fname))

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 2448, 1500)
    global cr
    cr = cairo.Context(surface)
    cr.save()
    cr.set_line_width(2)
    cr.set_source_rgb(1,1,1)
    cr.paint()
    
    if grey_lines: col = OURGREY 
    else: col = 0

    cr.set_line_width(10)
    cr.set_source_rgb(col, col, col)
    cr.rectangle(0,0,2440,1220)
    cr.stroke()

    cr.set_source_rgb(col, col, col)
    cr.select_font_face("Verdana", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(102)
    cr.move_to(20,1325)
    cr.show_text(material)
    cr.set_font_size(72)
    cr.move_to(20,1410)
    cr.show_text(title)
    cr.move_to(2150, 1410)
    cr.show_text(duration + ' min')

    previous_line = {"X":0,"Y":0} 
    cr.set_line_width(2)

    for o in face:
        l = [reverse_y(s) for s in o.string.splitlines()]
        for d in l:
            if d:
                current_line = d  
                if current_line.has_key('X') and current_line.has_key('Y'):
                    draw_gcode(previous_line, current_line, grey_lines)
                    previous_line = current_line
                    ### If I don't do this here the air move are black
                    ### check if I use the right function to change color of lines
                    ### this takes time to do 
                    cr.stroke()

    
    if grey_background:
        cr.set_line_width(8)
        cr.set_source_rgb(0.49,0.49,0.49)
        cr.rectangle(2190,970,250,250)
        cr.fill()
        cr.stroke()
    
    im = Image.frombuffer("RGBA",( surface.get_width(),surface.get_height() ),surface.get_data(),"raw","RGBA",0,1)
    im = im.resize((350,214),Image.ANTIALIAS)
    im.save(image_path)
    surface.finish()

def draw_empty_face(image_path, duration, grey_background=False):

    surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, 2448, 1500)
    global cr
    cr = cairo.Context (surface)
    cr.save()
    cr.set_line_width(2)
    if grey_background: cr.set_source_rgb(0.49,0.49,0.49)
    else: cr.set_source_rgb(1,1,1)
    cr.paint()
    
    cr.set_line_width(8)
    cr.set_source_rgb(0, 0, 0)
    cr.rectangle(0,0,2440,1220)
    cr.stroke()

    cr.select_font_face("Verdana", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(102)
    cr.move_to(20,1325)
    fname = basename(image_path).split('_board')[0]
    cr.show_text(clean_title(fname))
    cr.move_to(2150, 1410)
    cr.set_font_size(72)
    cr.show_text(duration)
    
    im = Image.frombuffer("RGBA",( surface.get_width(),surface.get_height() ),surface.get_data(),"raw","RGBA",0,1)
    im = im.resize((350,214),Image.ANTIALIAS)
    im.save(image_path)
    surface.finish()

def draw_nc(path, image_path, duration, grey_background=False, grey_lines=False):
    """
        Implement the convention that we render Face B on two 
        face sheets and Face A on single face sheet.

        Also: failsafe, render a blank board if it rendering 
        bugs for some reason.
    """
    
    f = open(path)
    s = f.read()
    f.close()
    
    boards = list_boards(s)
    bnr = 1
    for board in boards :
        try:
            nc = nc_parser(board)
            list_of_faces = nc.faces()
            # pick the right face to render
            if len(list_of_faces) == 2:
                face = list_of_faces[1]
            else:
                face = list_of_faces[0]
            draw_face(face, image_path, duration, grey_background, grey_lines)
        except: 
            # it was too hard to draw a blank rectangle will do
            draw_empty_face(image_path, duration, grey_background)
        bnr += 1
