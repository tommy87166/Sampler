from aiohttp import web
from aiohttp import streamer
import asyncio
import socketio
import webbrowser
import pandas
import json
from io import BytesIO
from sample import AdvancedJSONEncoder,AdvancedJSONEncoderResult,sampler
import concurrent.futures
from functools import partial
import os
import pickle
import itertools


sio = socketio.AsyncServer()
app = web.Application()
app.router.add_static('/static', 'dist')
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    with open('dist/index.html',"rb") as f:
        return web.Response(text=f.read().decode("utf8"), content_type='text/html')
app.router.add_get('/', index)

#For File Uploading View

#欲將 Cpu-Bounding 工作放入Process-Executor，故建立讀取函數
def load_excel(byte):
    df = pandas.read_excel(byte)
    return df

async def load_and_check(byte,sid):
    global ledger
    #發送通知-開始讀取
    await sio.emit('msg',"讀取檔案中", room=sid)
    #將BytesIO位置指向0
    byte.seek(0)
    #開始讀取
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as pool:
            df = await loop.run_in_executor(pool, partial(load_excel,byte))
        #發送通知-開始檢查
        await sio.emit('msg',"進行檢查", room=sid)
        #檢查
        assert "date"       in df,"未含有日期欄位:date"
        assert "acc_no"     in df,"未含有科目編號欄位:acc_no"
        assert "vou"        in df,"未含有傳票編號欄位:vou"
        assert "acc_name"   in df,"未含有科目名稱欄位:acc_name"
        assert "note"       in df,"未含有摘要欄位:note"
        assert "debit"      in df,"未含有借方欄位:debit"
        assert "credit"     in df,"未含有貸方欄位:credit"
        #型別轉換
        df["date"]     = df["date"].astype(str)
        df["acc_no"]   = df["acc_no"].astype(str)
        df["acc_name"] = df["acc_name"].astype(str)
        df["vou"]      = df["vou"].astype(str)
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
            "account":df[["acc_no","acc_name"]].drop_duplicates().sort_values("acc_no").to_dict(orient="records")
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

#For Rule Set View
rules = {}
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
async def read_rule(sid):
    global rules
    try:
        #讀取規則集
        with open("ruleset.json","r") as f:
            rules_in_json = json.load(f)
        #建構Sampler
        rules = {key:sampler(data["name"],data["method"],data["direction"],data["criteria"],[])  for (key,data) in rules_in_json.items()}
        await sio.emit('rules',json.dumps(rules,cls=AdvancedJSONEncoder), room=sid)
    except Exception as e:
        await sio.emit('error',str(e), room=sid)

@sio.event
async def save_rule(sid):
    global rules
    try:
        with open("ruleset.json","w") as f:
            json.dump(rules,f,cls=AdvancedJSONEncoder)
        await sio.emit('msg',"規則集已儲存", room=sid)
    except Exception as e:
        await sio.emit('error',str(e), room=sid)

#For Sampling View
@sio.event
async def sample(sid,data):
    #驗證參數
    await sio.emit('msg',"檢查參數", room=sid)
    apply_rules,apply_accounts = set(data.keys()),set(itertools.chain.from_iterable(data.values()))
    try:
        for rule in apply_rules:
            assert rule in rules, "規則 {} 不在定義的規則集中".format(rule)
        for account in apply_accounts:
            selected_df = ledger[ledger["acc_no"] == account]
            assert len(selected_df) > 0,"明細帳中找不到科目 {}".format(account)
    #將資料載入Sampler中
        for key,accounts in data.items():
            rules[key].load( ledger[ledger["acc_no"].isin(accounts)] )
    except Exception as e:
        await sio.emit('error',str(e), room=sid)
    finally:
        await sio.emit('msg',"資料載入完成", room=sid)
    
@sio.event
async def result(sid):
    try:
        await sio.emit('result',json.dumps(rules,cls=AdvancedJSONEncoderResult), room=sid)
    except Exception as e:
        await sio.emit('error',str(e), room=sid)

@sio.event
async def skip(sid,data):
    try:
        rules[ data["rule"] ].exclude.append( data["vou"] )
        await sio.emit('result',json.dumps(rules,cls=AdvancedJSONEncoderResult), room=sid)
    except Exception as e:
        await sio.emit('error',str(e), room=sid)

@sio.event
def connect(sid, environ):
    print("connect ", sid)
@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@streamer
async def stream(writer,reader=None):
    while True:
        chunk = reader.read(2 ** 16)
        if not chunk:
            break
        await writer.write(chunk)

async def download(request):
    #建立物件
    io     = BytesIO()
    writer = pandas.ExcelWriter(io, engine='xlsxwriter')
    #建立檔案
    stat = []
    for sampler in rules.values():
        sampler.to_excel(writer)
        sampler.export_stat(stat)
    pandas.Dataframe(stat).to_excel(writer,sheet_name="抽核比例")
    #存檔並傳送
    writer.save()
    io.seek(0)
    headers = {
        "Content-disposition": "attachment; filename={file_name}".format(file_name="Output.xlsx")
    }
    return web.Response(
        body=stream(io),
        headers=headers
    )
app.router.add_get('/download', download)


if __name__ == '__main__':
    host,port="127.0.0.1",8888
    loop = asyncio.get_event_loop()
    web.run_app(app,host=host,port=port)