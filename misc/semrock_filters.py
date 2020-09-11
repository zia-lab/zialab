#!/urs/env python3

import os, pickle

class Filters():
    def __init__(self, codebase_dir):
        self.filterspkl = os.path.join(codebase_dir,'zialab/misc/filters.pkl')
        self.filters = pickle.load(open(self.filterspkl,'rb'))
        self.left_filter = None
        self.angled_filter = None
        self.bottom_filter = None
    def search(self,search_terms):
        return {filt: self.filters[filt] for filt in self.filters if search_terms in filt}
    def set_left(self,left_filter):
        self.left_filter = self.filters[left_filter]
    def set_angled_filter(self,angled_filter):
        self.angled_filter = self.filters[angled_filter]
    def set_bottom_filter(self,bottom_filter):
        self.bottom_filter = self.filters[bottom_filter]
    def collection_path(self):
        if self.angled_filter != None and self.bottom_filter != None:
            self.collection_transmission = np.array([self.angled_filter['data'][:,0],
                    self.angled_filter['data'][:,1]*self.bottom_filter['data'][:,1]])
