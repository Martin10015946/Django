'''
Functions to parse and compose lines of gcode. Next developpement
steps are raise more errors and cleaner string formatting.
'''
from collections import OrderedDict
import re

pattern = re.compile('\S*\d*[\.\d*]+')
lettere = re.compile('.')
numre = re.compile('[-?\d*\.?\d*]+')

def parseline(s):
    '''Parse a line of gcode returns an ordered dict
    >>> s = "G02 X30.149 Y0 Z-18.5 I0 J0 F166.667"
    >>> parseline(s)
    OrderedDict([('G', 2.0), ('X', 30.149), ('Y', 0.0), ('Z', -18.5), ('I', 0.0), ('J', 0.0), ('F', 166.667)])
    '''
    # get rid of comments at the end of lines
    if not s.startswith('('): s = s.split('(')[0] 
    l= pattern.findall(s)
    d= OrderedDict()
    for i in l:
        letter= lettere.match(i).group()
        num= float(numre.search(i).group())
        d[letter]= num  
    return d

def parseM12(s):
    '''parse an M12 line and returns the operation affiliation
    dictionary n.b. part options values that can be lists
    '''
    def parse(s):
        rd = {}
        sparen = re.findall('\(',s)
        cparen = re.findall('\)',s)
        if len(sparen) != len(cparen):
            parenerr = 'The following operation comments are not well formed, missing parenthesis '
            raise ValueError, parenerr  + s
        else:
            comments = re.findall('\(\w+\s*\w*: [A-Za-z0-9-\s.,]*\)', s)
            for comment in comments:
                comment = comment.split(': ')
                key = comment[0][1:]
                value = comment[1][:-1].split(', ')
                if not rd.has_key(key):
                    if len(value) > 1:
                        rd[key] = value
                    else:
                        rd[key] = value[0]
            return rd

    if s.startswith('M12'):
        return parse(s)
    else:
        M12err = 'The string that you passed should begin with a M12, not '
        raise ValueError, M12err + s

def Gformat(f):
    """get rid of floating points"""
    if f < 10:
        return "0"+str(f).split('.')[0]
    else:
        return str(f).split('.')[0]

def odict2str(d):
    """Recompose a gcode line from an 
    odict as returned by parseline
    >>> s = "G02 X30.149 Y0 Z-18.5 I0 J0 F166.667"
    >>> d =  parseline(s)
    >>> odict2str(d)
    'G02 X30.149 Y0.0 Z-18.5 I0.0 J0.0 F166.667 '
    """
    ns= ""
    allow = ['X','Y','I','J','Z','K','F','R']
    for key in d:
        if key in allow:
            ns+= key+str(round(d[key],3))+" "
        else:
            ns+= key+Gformat(round(d[key],3))+" "
    return ns

def affil2str(d):
    """recompose an operation comment"""
    s = ''
    if d != {}:
        for key in d:
            if type(d[key]) == list:
                s += '(%s: %s)' % (key, ', '.join(d[key]))
            else:
                s += '(%s: %s)' % (key, d[key])
    return s
