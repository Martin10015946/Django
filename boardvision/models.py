import os
import shutil
from string import digits
from django.conf import settings
from render import draw_nc
from nc import nc_parser, split_multiple
from nc import extend_header, reduce_header
import timer


class FolderSorter:

    def __init__(self, path):

        self.path = path
        self.ls = self._list_files()
        self.longest = self._get_longest_seq()
    
    def _test_fn(self, path):
        '''Pick:
            * .nc files
            * wich name starts with [0,...,9]
            * and contians a dash
        '''
        if os.path.isfile(path) \
            and path.split('.')[-1] == 'nc' \
            and os.path.basename(path).rstrip().lstrip()[0] in digits \
            and not os.path.basename(path).find('-') == -1:
            return True
        else:
            return False
    
    def _list_files(self):
        # Split multiple sheets 
        l = os.listdir(self.path)
        for p in l:
            p = self.path + os.sep + p
            if self._test_fn(p):
                if split_multiple(p):
                    shutil.move(p, p + ' AUTO SPLITTED')
        
        rl = []
        l = os.listdir(self.path)
        for p in l:
            fullp = self.path + os.sep + p
            if self._test_fn(fullp):
                rl.append(p)
        
        return rl

    def _get_sort_seq(self, s):
        return [int(i) for i in s.split('-')[0].split('.')]

    def _get_longest_seq(self):
        longest = 0
        for e in self.ls:
            n = self._get_sort_seq(e)
            if len(n) > longest: longest = len(n) 
        return longest

    def _get_list_pre_sort(self):
        rl = []
        for e in self.ls:
            re = []
            [re.append(seqed) for seqed in self._get_sort_seq(e)]
            re += [0]*(self.longest-len(re))
            re.append(e)
            rl.append(re)
        return rl

    def _get_days_list(self,l):
        '''Assumes that files are numbered from 0 to 5'''
        rl = [[],[],[],[],[],[]]
        for e in l:
            rl[e[0]].append(e)
        return rl

    def _sort_by_days(self, l):
        return sorted(l, key=lambda e: e[0])

    def _sort_a_day(self, l):
        return sorted(l, key=lambda e: e[1])

    def get_sorted_list(self):
        sl = self._sort_by_days(self._get_list_pre_sort())
        rl =[]
        for d in [self._sort_a_day(e) for e in self._get_days_list(sl)]:
            rl.append([e[-1] for e in d])
        return rl


class BoardHandler:
    '''This class centralise access to the previewing and 
    timing fuctions developed in the context of BoardVision.
    
    It is not meant to be persistent. It is invoked each time
    the board train view is called.''' 
    
    def __init__(self, path):
        self.path = path
        
        us_name = os.path.basename(self.path).replace(' ', '_')

        self.preview_path = settings.BOARDS_CACHE + os.sep
        self.preview_path += us_name + '.jpg' 
        
        self.board_url = 'http://169.254.184.4/img/boards/' + os.path.basename(self.preview_path)
        
        try:
            f = open(self.path)
            ncs = f.read()
            f.close()
            nc = nc_parser(ncs)
            self.header = nc.header()
        except:
            self.header = {}

    def is_preview_cached(self):
        if os.path.exists(self.preview_path):
            if os.path.getmtime(self.path) < os.path.getmtime(self.preview_path):
                return True 
            else: # expired cache
                return False
        else: # no cache
            return False

    def get_preview(self, force=False):
        if not self.is_preview_cached() or force:
            if force: 
                extend_header(self.path,{'Ready':'False'})
                reduce_header(self.path, 'Start time')
                self.header.pop('Start time')
            draw_nc(self.path, 
                    self.preview_path, 
                    str(self.get_duration()),
                    grey_lines=self.is_transfered())
        return self.board_url

    def set_ready(self):
        draw_nc(self.path, 
                self.preview_path,
                str(self.get_duration()), 
                grey_background=True)
        extend_header(self.path,{'Ready':'True'})
        reduce_header(self.path,'Start time')

    def is_ready(self):
        if 'Ready' in self.header:
            if self.header['Ready'] == 'True' and not 'Start time' in self.header:
                return True
            else:
                return False
        else:
            return False

    def is_transfered(self):
        if 'Start time' in self.header:
            return True
        else:
            return False

    def get_duration(self):
        '''Return the running time of the file in minutes (int)
        Either getting it from the header of the file "Duration" key,
        or calculating it with timer.py
        '''
        if 'Duration' in self.header:
            return int(round(float(self.header['Duration']),0))
        else: # stamp the file with duration
            try:
                dur = timer.total(self.path)
                dur = ((dur * settings.BOARDS_BREAK) / 100) + dur
                dur = str(int(dur))
            except:
                dur = '0'
            extend_header(self.path,{'Duration':str(dur)})
            return int(dur)
