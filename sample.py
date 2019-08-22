import json
import pandas

class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()

class AdvancedJSONEncoderResult(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonresult__'):
            return obj.__jsonresult__()

class sampler(object):
    def __init__(self,name,method,direction,criteria,exclude=[]):
        #Parameter
        self.name       = name
        self.method     = method
        self.direction  = direction
        self.criteria   = criteria
        self.exclude    = exclude
        self.multiplier = 12,12
        #Input
        self.df        = pandas.DataFrame()
        #Result
        self.result    = pandas.DataFrame()
        #Flag
        self.flag_load   = False
        self.flag_sample = False
        
    def load(self,df):
        print("[{}] Load Data: {} Rows".format(self.name,len(df)))
        self.df         = df
        self.flag_load  = True

    @property
    def stat(self):
        if self.flag_sample:
            population        =  self.df["debit"].sum() - self.df["credit"].sum()
            population_expand =  population / self.multiplier[0] * self.multiplier[1]
            size              =  self.result["debit"].sum() - self.result["credit"].sum()
            ratio             =  size / population_expand
            return population,population_expand,size,ratio
        else:
            return 0,0,0,0

    def __sample(self):
        if self.flag_load:
            print("[{}] Run Sampling".format(self.name))
            #排除不想要的傳票
            exclude = self.df [ self.df["vou"].isin(self.exclude) ].index
            df      = self.df.drop(exclude)
            #依抽樣方式抽樣
            if   self.method == "order"  :
                self.__order_sampler(df)
            elif self.method == "percent":
                self.__percent_sampler(df)
            else:
                raise Exception("Not Implemented Method")
            #標示為已抽樣
            self.flag_sample = True

    def __order_sampler(self,df):
        self.result = df.sort_values(self.direction,ascending=False)[:self.criteria]
    
    def __percent_sampler(self,df):
        pass

    #Json Encorder
    def __jsonencode__(self):
        return {
            "name"       : self.name, 
            "method"     : self.method,
            "direction"  : self.direction,
            "criteria"   : self.criteria,
            "exclude"    : self.exclude,
        }
    
    def __jsonresult__(self):
        self.__sample()
        return {
            "df"         : self.df.to_dict(orient="records"),
            "result"     : self.result.to_dict(orient="records"),
            "parameter"  : self.__jsonencode__(),
            "stat"       : self.stat   
        }