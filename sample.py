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

mapper = {
    "date":"日期",
    "acc_no":"科目編號",
    "acc_name":"科目名稱",
    "vou" :"傳票編號",
    "note":"摘要",
    "debit":"借方金額",
    "credit":"貸方金額"
}

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
                sampler = self.__order_sampler
            elif self.method == "percent":
                sampler = self.__percent_sampler
            else:
                raise Exception("Not Implemented Method")
            #抽樣 + 後處理
            self.result = sampler(df)
            #標示為已抽樣
            self.flag_sample = True

    def __order_sampler(self,df):
        return df.sort_values(self.direction,ascending=False)[:self.criteria]
    
    def __percent_sampler(self,df):
        return None

    #Json Encorder
    def __jsonencode__(self):
        return {
            "name"       : self.name, 
            "method"     : self.method,
            "direction"  : self.direction,
            "criteria"   : self.criteria,
        }
    
    def __jsonresult__(self):
        self.__sample()
        return {
            #"df"         : json.loads(self.df.to_json(orient="records")),
            "result"     : json.loads(self.result.to_json(orient="records")),
            "parameter"  : self.__jsonencode__(),
            "stat"       : self.stat   
        }