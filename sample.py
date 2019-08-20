import pandas
import json

class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()

class sampler(object):
    def __init__(self,name,method,direction,criteria,exclude=[]):
        self.name      = name
        self.method    = method
        self.direction = direction
        self.criteria  = criteria
        self.exclude   = exclude
        #
        self.mutipier  = 12
        self.df        = pandas.DataFrame()
        self.flag      = False
    def __jsonencode__(self):
        return {
            "name"      : self.name, 
            "method"    : self.method,
            "direction" : self.direction,
            "criteria"  : self.criteria,
            "exclude"   : self.exclude
        }
    def sample(self):
        print("Sample:",self.name)
        
        try:
            df = self.df.sort_values(self.direction,ascending=False)
            if self.method == "order":
                self.result = df[:self.criteria]
            
            elif self.method == "percent":
                p,pm = self.population()
                target = pm * self.criteria
                for row in range(0,len(df)+1):
                    selected = df[0:row]
                    if selected[self.direction].sum() >= target:
                        break
                self.result = selected
            
            else:
                raise Exception("No Implement Method")
        except:
            self.flag = False
        
        else:
            self.size    = self.result[self.direction].sum()
            self.flag    = True

    def population(self):
        total = self.df["debit"].sum() -  self.df["credit"].sum()
        if self.direction == "credit":
            total = total * -1
        return total,total/self.mutipier*12

    def write(self,writer):
        if self.flag:
            self.result.to_excel(writer,sheet_name=self.name)
    
    def stat(self,stat):
        if self.flag:
            p,pm   = self.population()
            data = {
                "名稱"     : self.name,
                "母體"     : p,
                "換算月數" : self.mutipier,
                "換算母體" : pm,
                "抽樣金額" : self.size,
                "抽樣比例" : round(self.size/pm*100,2),
                #para
                "參數-method"   :self.method,
                "參數-direction":self.direction,
                "參數-criteria" :self.criteria
            }
            stat.append(data)