import re
from UserDict import UserDict
from gcode import parseline, odict2str
from tempfile import TemporaryFile
from math import sin, cos, radians
from os.path import sep, basename, dirname
from string import digits
import sys

NC_CODES = """registration_startcode:(Reg)
flip_endcode:A
flip_startcode:Z-300
toolchange_endcode:G97
toolchange_startcode:G00 T
header_endcode:G75
operation_endcode:M22
endcode:(End)
operation_startcode:M12
airmove_startcode:M22
airmove_encode:M12"""

def split_multiple(path):
    f = open(path)
    nc_string = f.read()
    f.close()
    sheets = list_boards(nc_string) 

    if len(sheets) > 1:
        i = 1
        for sheet in sheets:
            # compose file name preserving the file number if there is one
            filename = basename(path)
            if filename.lstrip().rstrip()[0] in digits and len(filename.split('-')) > 1:
                filename = filename.split('-')[0] + ' - sheet ' + str(i) + ' of ' + '-'.join(filename.split('-')[1:]) 
            else:
                filename = 'sheet ' + str(i) + ' of ' + basename(path)
            
            # fix the beg and end of the splitted file
            if i == 1 and sheet.find('(End)') == -1:
                sheet = '\n'.join(sheet.splitlines()[:-2]) + "M22\n(End)\nG00 X2440 Y1220 Z-299\nM02"   
            elif i > 1 and sheet.find('(End)') == -1:
                sheet = "G90\nM90\n(Header= placeholder)\nG71\nM25\nG75\n(Reg)" + sheet + "M22\n(End)\nG00 X2440 Y1220 Z-299\nM02"
            else:
                sheet = "G90\nM90\n(Header= placeholder)\nG71\nM25\nG75\n(Reg)" + sheet

            f = open(dirname(path) + sep + filename, 'w')
            f.write(sheet)
            f.close()
            i += 1
        return True
    else:
        return False

def list_boards(s):
    """utility function to return a list of boards 
    when an NC file contains more than two faces"""
    
    return s.split('(Flip)\nM25\n(Reg)')    

def list_faces(s):
    """utility functions to quickly return a list of faces strings"""

    return s.split('(Flip)')

def extend_header(path,new_header):
    '''utility function to add key value pairs to a file's header'''
    f = open(path)
    nc_string = f.read()
    nc = nc_parser(nc_string)
    f.close()
    
    header = nc.header()
    for key in new_header:
        header[key] = new_header[key]

    header = '\n'.join(['('+key+'= '+header[key]+')' for key in header]) + '\n'
    new_nc_sting = '\n'.join(['G90\nM90', header, nc_string[nc_string.find('G71'):]])

    f = open(path,'w')
    f.write(new_nc_sting)
    f.close()

def reduce_header(path,remove_key):
    '''utility function to remove key value pairs to a file's header'''
    f = open(path)
    nc_string = f.read()
    nc = nc_parser(nc_string)
    f.close()
    
    header = nc.header()
    new_header = {}
    for key in header:
        if key != remove_key:
            new_header[key] = header[key]

    header = '\n'.join(['('+key+'= '+new_header[key]+')' for key in new_header])
    new_nc_sting = '\n'.join(['G90\nM90', header, nc_string[nc_string.find('G71'):]])

    f = open(path,'w')
    f.write(new_nc_sting)
    f.close()

class nc_parser:
    def __init__(self, s):
        self.string = self.remreg(s)[0]
        self.reg = self.remreg(s)[1]
        self.thickness = self.get_thickness(s)
        self.nc_codes = self._nc_codes()
        self.partlist = self.get_partlist()
        self.array_values = self.get_array_values()

    def get_array_values(self):
        s = self.string
        if s.find('(Array') != -1:
            b = s.find('(Array')
            b = s.find('=',b)
            e = s.find(')',b)
            return [int(float(i)) for i in s[b+1:e].split(',')]
        else:
            return None 

    def orhpan_ops(self):
            if self.string.find('M12\n') != -1:
                return True
            else:
                return False

    def get_partlist(self):
        s = self.string
        p= re.compile("\(part:.[^\(]*\)")
        l= re.findall(p,s)

        #delete duplicates
        if len(l) > 1:
            nl = []
            [nl.append(i[7:-1]) for i in l if i[7:-1] not in nl]
            if self.orhpan_ops() is True:
                nl.append('rest')
        else: nl = ['single part']

        return nl
    
    def get_thickness(self, s):
        """find an return a file thickness"""
        pass

    def remreg(self, s):
        b = s.find("(Reg)")
        e = s.find("(Reg)",b+6)

        return [s[:b] + s[e+6:], s[b:e+6]]

    def flip_index(self):
        """return the flip index"""
        flip_startcode = self.nc_codes['flip_startcode']
        flip_index = self.string.find(flip_startcode)
        i = self.string.rfind('\n', 0, flip_index)
        
        return i
    
    def ops_range(self):
        """return pairs of indexes and ends of the operations from a string of g-code"""
        
        s = self.string
        
        M12 = [match.start() for match in re.finditer(re.escape('M12'), s)]
        G00 = [s[:i].rfind('G00') for i in M12]
        ops = [(i,s.find('M22',i)+3) for i in G00]
        
        return ops
    
    def tool_change_indexes(self):
        """return the list of every tool changes"""
        return [match.start() for match in re.finditer(re.escape('G00 T'), self.string)]
    
    def faces(self):
        """return the list of ops for each two faces"""
        s = self.string
        l = self.ops_range()
        i = self.flip_index()
        t = self.tool_change_indexes()

        def fa(x): return x[0] < i
        def fb(x): return x[0] > i      
        def tool(o,index):
            ti = filter(lambda i: i < index, t)[-1]
            te = self.nc_codes['toolchange_endcode']
            te = s.find(te, ti)
            te = s.find('\n', te)       
            return s[ti:te]

        def part(s):
            ps = s.find('(part:')
            if ps !=-1:
                pe = s.find(')',ps)
                return s[ps+7:pe]
            else :
                return None

        def face(f):
            face_list = []
            op_index = 0
            for o in f:
                this_op_tool = tool(s[o[0]:o[1]], f[op_index][0])
                this_op_string = s[o[0]:o[1]]
                this_op_part = part(s[o[0]:o[1]])
                face_list.append(op(this_op_string,this_op_tool,this_op_part))
                op_index += 1   

            return face_list

            #return [op(self.string[o[0]:o[1]], tool(self.string[o[0]:o[1]]), part(self.string[o[0]:o[1]])) for o in f]
                        #return [op(self.string[o[0]:o[1]]) for o in f]

        a = face(filter(fa,l))
        b = face(filter(fb,l))
        
        if b == []:
            return [a]
        else:
            return [face(filter(fa,l)), face(filter(fb,l))]
    
    def header(self):
        """return a dictionary of the header values"""
        s = self.string
        i = s.find(self.nc_codes['header_endcode'])
        sh = s[:i]
        d = {}
        
        for line in sh.splitlines(): 
            l = line[1:len(line)-1].split('=') # we do this because the format of header strings is (balh = blu)
            if len(l) > 1:
                d[l[0]] = l[1].lstrip().rstrip()
        
        return d

    def _nc_codes(self):
        """return a dictionary of the preferences from the text file"""
        s= NC_CODES #f.read()
        d= {}
        for line in s.splitlines():
            line=line.split(':')
            d[line[0]]=line[1]

        return d

class op:
    def __init__(self, s, t, p):
        self.string = s
        self.tool = t
        self.part = p

    def time ():
        '''lenght of vectors * speed * coeff'''
        pass

class nc (UserDict):
    def __init__(self):
        UserDict.__init__(self)
        self['meta']= {}
        self['faces'] = []
        self['nc_codes']= self._nc_codes()
        # stop this business of user dict subclassing, it's useless here
        self['reg'] = self._reg()

    def _reg(self):
        f = open(sys.path[0] + sep + '..' + sep + "reg.txt")
        s = f.read()
        f.close()
        return s

    def _offset(self, x, y):
        """offset a NC XI YJ by x y"""
        def offseter(d,x,y):
            D = {'X':x,'Y':y,'I':x,'J':y}
            for k in d:
                if k in ['X','Y','I','J']:
                    d[k] = d[k] + D[k]
                    return d
        def do_face(l,x,y):
            nf = []
            for o in l:
                nl = [odict2str(offseter(parseline(line),x,y)) for line in o.string.splitlines()]
                no = op('\n'.join(nl),o.tool, o.part)
                nf.append(no)

            return nf

        nf = do_face(self['faces'][0],x,-y)
        self['faces'][0] = nf
        nf = do_face(self['faces'][1],x,y)
        self['faces'][1] = nf

    def rotate(self, centroid, angle):
        """rotate the NC around a centroid"""
        def offseter(d,x,y):
            D = {'X':x,'Y':y,'I':x,'J':y}
            for k in d:
                if k in ['X','Y','I','J']:
                    d[k] = d[k] + D[k]
                    return d
        def rotater(d,angle):
            if d.has_key('X') and d.has_key('Y'):
                x = d['X']
                y = d['Y']
                rx = x*cos(radians(angle)) - y*sin(radians(angle))
                ry = x*sin(radians(angle)) + y*cos(radians(angle)) 
                d['X'] = rx
                d['Y'] = ry

            if d.has_key('I') and d.has_key('J'):
                x = d['I']
                y = d['J']
                rx = x*cos(radians(angle)) - y*sin(radians(angle))
                ry = x*sin(radians(angle)) + y*cos(radians(angle)) 
                d['I'] = rx
                d['J'] = ry

            return d

        def do_face_b(l,x,y,angle):
            nf = []
            for o in l:
                nl = []
                for line in o.string.splitlines():
                    d = parseline(line)
                    d = offseter(d,-x,-y)
                    d = rotater(d,angle)                
                    d = offseter(d,x,y)
                    nl.append(odict2str(d))
                no = op('\n'.join(nl),o.tool, o.part)
                nf.append(no)
            return nf

        def do_face_a(l,x,y,angle):
            nf = []
            for o in l:
                nl = []
                for line in o.string.splitlines():
                    d = parseline(line)
                    d = offseter(d,-x,-(1220-y))
                    d = rotater(d,-angle)               
                    d = offseter(d,x,1220-y)
                    nl.append(odict2str(d))
                no = op('\n'.join(nl),o.tool, o.part)
                nf.append(no)
            return nf

        x = centroid[0]
        y = centroid[1]
        nf = do_face_a(self['faces'][0],x,y,angle)
        self['faces'][0] = nf
        nf = do_face_b(self['faces'][1],x,y,angle)
        self['faces'][1] = nf

    def by_tool(self, face):
        """returns a list of lists of operations grouped by tools, face is an index"""
        face = self['faces'][face]

        ops_by_tool = []
        current_tool = ''
        for op in face:
            if op.tool != current_tool:
                current_tool = op.tool
                ops_by_tool.append([op])
            else:
                ops_by_tool[-1].append(op)

        return ops_by_tool

    def make_part(self, partname, debug=False):
        """create a rat for a part in a temporary file
        and returns
            the file object
            the coordinates of the part in the orignal file
            the bounding box of the part
        """
        
        part_nc = nc()

        flag = 0

        if partname != 'single part' and partname != 'rest':
            part_nc['faces'].append([o for o in self['faces'][0] if o.part == partname]) 
            part_nc['faces'].append([o for o in self['faces'][1] if o.part == partname]) 
        elif partname == 'rest':
            faceA = [o for o in self['faces'][0] if o.part is None]
            faceB = [o for o in self['faces'][1] if o.part is None]
            if faceB == []:
                flag = 1    
            else:
                part_nc['faces'].append(faceA) 
                part_nc['faces'].append(faceB) 
        else:
            part_nc['faces'].append([o for o in self['faces'][0]]) 
            part_nc['faces'].append([o for o in self['faces'][1]]) 

        X = 0
        Y = 0
        x = 2250
        y = 1230
        for o in part_nc['faces'][1]:
            for s in o.string.splitlines():
                d = parseline(s)
                if d.has_key('X'):
                    if d['X'] > X: X = d['X']
                    elif d['X'] < x: x = d['X']
                if d.has_key('Y'):
                    if d['Y'] > Y: Y = d['Y']
                    elif d['Y'] < y: y = d['Y']
                if d.has_key('I'):
                    if d['I'] > X: X = d['I']
                    elif d['I'] < x: x = d['I']
                if d.has_key('J'):
                    if d['J'] > Y: Y = d['J']
                    elif d['J'] < y: y = d['J']
        if debug is True:
            f = part_nc.to_file(sys.path[0] + sep + '..' + sep + 'tmp\\' +partname + '.nc',self['reg'])
        f = part_nc.to_file('',self['reg'])
    
        if flag == 0:
            return f, [x,y], [X-x,Y-y]
        else:
            return flag 

    def to_string(self, list_of_ops):
        """print a collection of ops to string"""
        
        def mark(op):
            if op.string.find('M12 (part') == -1 and op.part is not None:
                i = op.string.find('\n', op.string.find('M12'))
                part = ' (part: %(part)s )'% {'part':op.part} 
                return op.string[:i] + part + op.string[i:]
            else: return op.string

        #join of the operations should be the rapid plane code
        #rapid = "G00 Z-" + str(self['meta']['Material']+13) + "\n"
        #TODO write the code to select the material thickness
        rapid = "\nG00 Z-" + str(18+13) + "\n"
        last_tool = ''
        l = []
        for o in list_of_ops:
            if o.tool != last_tool:
                last_tool = o.tool
                l.append(o.tool)

            l.append(mark(o))
            l.append(rapid)

        #l = map(lambda key: key + '\n' + rapid.join([o.string for o in d[key]]), [key for key in d])
        
        return '\n'.join(l) 
                
    def to_file(self, filename, reg):
        """write a NC file"""
        header = ["G90\nM90","(def meta to string)","G71\nM25\nG75\n",reg]
        s = '\n'.join(header) + '\n'                        
        flip = 'G00 X2440 Y1220 Z-300\n(Flip)\nM25\nA180.'
        endcode = self['nc_codes']['endcode'] + '\nG00 X2440 Y1220 Z-299\nM02'
        l = [self.to_string(faces) for faces in self['faces']]
        s += l[0] + flip + "\n" + l[1] + endcode

        if filename != '':
            f = open(filename,'w')
            f.write(s) 
            f.close()

        f = TemporaryFile(dir=sys.path[0] + sep + '..' + sep + 'tmp')
        f.write(s)
        return(f)

    def _nc_codes(self):
        """return a dictionary of the preferences from the text file"""
        s= NC_CODES #f.read()
        d= {}
        for line in s.splitlines():
            line=line.split(':')
            d[line[0]]=line[1]

        return d
    

def merge(nc, dest_nc):
    """merge an nc class operations into another"""
    
    def merge_one_face(face):

        dest_nc_bt = dest_nc.by_tool(face)
        part_nc = nc.by_tool(face)

        if dest_nc_bt == []:
            dest_nc_bt = part_nc
        else:
            index = 0
            for group in part_nc:
                used = 0
                for dgroup in dest_nc_bt[index:]:
                    if group[0].tool == dgroup[0].tool and used == 0:
                        dgroup.extend(group)
                        used = 1
                        index += 1
                if used == 0:
                    dest_nc_bt.insert(index + 1, group)
                    index += 1


        dest_nc['faces'][face] = []

        for l in dest_nc_bt:
            for o in l:
                dest_nc['faces'][face].append(o)

    
    merge_one_face(0)
    merge_one_face(1)

def nc_composer(l,path):
    """transform an assembly structure into a NC file"""    

    l = de_array(l, is_part = False)

    dest_nc = nc()
    dest_nc['faces'] = [[],[]]
        
    reg = ''
    #thickness = ''
    i = 0
    for mu in l:
        mu['path'].seek(0)
        str_nc = mu['path'].read()    
        p = nc_parser(str_nc)
        
        if i == 0 : reg = p.reg 
        #if i == 0 : thickness = p.thickness

        part_nc = nc()
        part_nc['meta'] = p.header()
        part_nc['faces'] = p.faces()

        #part_nc.rotate(mu['centroid'], mu['angle'])
        part_nc._offset(round(mu['delta'][0],2),round(mu['delta'][1],2))        # offset
        merge(part_nc, dest_nc)                                 # merge

        i += 1

    dest_nc.to_file(path, reg)

def parts_nc_composer(l):

    l = de_array(l)

    dest_nc = nc()
    dest_nc['faces'] = [[],[]]
        
    reg = ''
    #thickness = ''
    i = 0
    for mu in l:
        mu['path'].seek(0)
        str_nc = mu['path'].read()
            
        p = nc_parser(str_nc)
        
        if i == 0 : reg = p.reg 
        #if i == 0 : thickness = p.thickness

        part_nc = nc()
        part_nc['meta'] = p.header()
        part_nc['faces'] = p.faces()

        part_nc.rotate(mu['centroid'], mu['angle'])
        part_nc._offset(round(mu['delta'][0],2),round(mu['delta'][1],2))        # offset
        merge(part_nc, dest_nc)                                 # merge

        i += 1

    return dest_nc.to_file('', reg)


def de_array(l, is_part = True):
    """transform a list of nested merge_units
    into a flat list of dicts for composer"""

    nl = []

    for mu in l:

        if mu.show == True:
            d = {}
            d['path'] = mu.path
            if is_part == True:
                d['delta'] = (mu.cx - mu.ocx, mu.cy - mu.ocy)
            else:
                d['delta'] = (0,0)
            d['centroid'] = (mu.ocx, mu.ocy)
            d['angle'] = mu.angle

            nl.append(d)

            if mu.nx > 1:
                for i in range(1,mu.nx):
                    d = {}
                    d['path'] = mu.path
                    if is_part == True:
                        d['delta'] = ((mu.cx - mu.ocx) + (i * mu.ax), mu.cy - mu.ocy)
                    else:
                        d['delta'] = (i * mu.ax, 0)
                    d['centroid'] = (mu.ocx, mu.ocy)
                    d['angle'] = mu.angle
                    
                    nl.append(d)

                    if mu.ny > 1:
                        for j in range(1,mu.ny):
                            d = {}
                            d['path'] = mu.path
                            if is_part == True:
                                d['delta'] = ((mu.cx - mu.ocx) + (i * mu.ax), (mu.cy - mu.ocy) + (j * mu.ay))
                            else:
                                d['delta'] = (i * mu.ax,j * mu.ay)
                            d['centroid'] = (mu.ocx, mu.ocy)
                            d['angle'] = mu.angle
                            
                            nl.append(d)
            if mu.ny > 1:
                for i in range(1, mu.ny):
                    d = {}
                    d['path'] = mu.path
                    if is_part == True:
                        d['delta'] = (mu.cx - mu.ocx, (mu.cy - mu.ocy) + (i * mu.ay))
                    else:
                        d['delta'] = (0, i * mu.ay)
                    d['centroid'] = (mu.ocx, mu.ocy)
                    d['angle'] = mu.angle
                    
                    nl.append(d)


    return nl
