from aiohttp import web
import asyncio
import socketio
import webbrowser
import pandas
import json
from io import BytesIO

sio = socketio.AsyncServer()
app = web.Application()
app.router.add_static('/static', 'dist')
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    with open('dist/index.html',"rb") as f:
        return web.Response(text=f.read().decode("utf8"), content_type='text/html')
app.router.add_get('/', index)

async def load_and_check(byte,sid):
    global ledger
    byte.seek(0)
    df = pandas.read_excel(byte)
    await sio.emit('msg',"進行檢查", room=sid)
    try:
        #檢查
        assert "date"       in df,"未含有日期欄位:date"
        assert "acc_no"     in df,"未含有科目編號欄位:acc_no"
        assert "vou"        in df,"未含有傳票編號欄位:vou"
        assert "acc_name"   in df,"未含有科目名稱欄位:acc_name"
        assert "note"       in df,"未含有摘要欄位:note"
        assert "debit"      in df,"未含有借方欄位:debit"
        assert "credit"     in df,"未含有貸方欄位:credit"
    except Exception as e:
        #未通過檢查
        file_status = {
            "status":False,
            "reason":str(e),
            "row":None,
            "column":None,
            "diff":None,
            "account":None
        }
    else:
        #通過檢查
        file_status = {
            "status":True,
            "reason":None,
            "row":len(df),
            "column":len(df.columns),
            "diff":df["debit"].sum() - df["credit"].sum(),
            "account":df[["acc_no","acc_name"]].drop_duplicates().to_dict(orient="records")
        }
        ledger = df
    finally:
        await sio.emit('file_status',file_status, room=sid)
        await sio.emit('msg',"完成檢查", room=sid)

async def upload_handler(request):
    """Handle Update File."""
    reader = await request.multipart()
    socket_field,file_field = False,False
    async for field in reader:
        if field.name == "socket":
            socket_field = await field.text()
        if field.name == "file":
            file_field,size = BytesIO(),0
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                file_field.write(chunk)
    if socket_field and file_field:
        await sio.emit('msg',"Received file in size of {}.".format(size), room=socket_field)
        loop.create_task(load_and_check(file_field,socket_field))
        return web.Response(text="OK")
    else:
        return web.Response(text="Error")
app.router.add_post('/upload', upload_handler)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)


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


class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()

test_sampler  = sampler("T12_薪資支出","order","debit",3,[])
test_sampler2 = sampler("T32_銷貨","percent","credit",3,[])

rules = {"T12_薪資支出":test_sampler,"T32_銷貨":test_sampler2}

@sio.event
async def set_rule(sid, data):
    name,method,direction,criteria,exclude = data["name"],data["method"],data["direction"],data["criteria"],data["exclude"]
    rules[name] = sampler(name,method,direction,criteria,exclude)
    await sio.emit('rules',json.dumps(rules,cls=AdvancedJSONEncoder), room=sid)

@sio.event
async def delete_rule(sid, data):
    del rules[data]
    await sio.emit('rules',json.dumps(rules,cls=AdvancedJSONEncoder), room=sid)

@sio.event
async def get_rule(sid):
    await sio.emit('rules',json.dumps(rules,cls=AdvancedJSONEncoder), room=sid)

@sio.event
async def change_rule(sid,data):
    print("---Change Rule Event---")
    change = False
    for key in data:
        for field in data[key]:
            selected_sampler = rules[key]
            oldVal = getattr(selected_sampler,field)
            newVal = data[key][field]
            if newVal  != oldVal :
                print("Change Key:",key,"Field:",field,"Value:",oldVal," -> ",newVal)
                setattr(selected_sampler,field,data[key][field])
                change = True
    if change:
        await sio.emit('rules',json.dumps(rules,cls=AdvancedJSONEncoder), room=sid)
        print("Changed Rule Sent.")
    else:
        print("No Changed Rule.")
    print("------------\n\n")

@sio.event
async def sample(sid,data):
    writer = pandas.ExcelWriter('Output.xlsx', engine='xlsxwriter')
    #Load Df into Sampler and sample
    stat = []
    for key in data:
        sampler,accounts  = rules[key],data[key] 
        sampler.df  = ledger[ledger["acc_no"].isin(accounts)]
        sampler.sample()
        sampler.write(writer)
        sampler.stat(stat)
    #Stat
    stat = pandas.DataFrame(stat)
    stat.to_excel(writer,sheet_name="統計")
    writer.save()
    #IO
    await sio.emit('stat',stat, room=sid)
    


if __name__ == '__main__':
    host,port="127.0.0.1",8888
    loop = asyncio.get_event_loop()
    web.run_app(app,host=host,port=port)