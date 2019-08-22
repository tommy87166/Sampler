import json

class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()

class sampler(object):
    def __init__(self,name,method,direction,criteria,exclude=[]):
        #Parameter
        self.name      = name
        self.method    = method
        self.direction = direction
        self.criteria  = criteria
        self.exclude   = exclude
        #Input
        self.df        = None 
        #Result
    def __jsonencode__(self):
        return {
            "name"      : self.name, 
            "method"    : self.method,
            "direction" : self.direction,
            "criteria"  : self.criteria,
            "exclude"   : self.exclude
        }
    def sample(self,multiplier):
        pass