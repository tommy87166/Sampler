from aiohttp import web
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
            print("Received file in size of {}.".format(size))
    
    if socket_field and file_field:
        await sio.emit('msg',"Received file in size of {}.".format(size), room=socket_field)
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

@sio.event
async def openledger(sid, data):
    global ledger
    df = pandas.read_excel(data)
    await sio.emit('msg',"已開啟明細帳{}，共{}列{}欄".format(data,len(df),len(df.columns)), room=sid)
    await sio.emit('msg',"進行檢查...", room=sid)
    try:
        assert "date"       in df,"未含有日期欄位:date"
        assert "acc_no"     in df,"未含有科目編號欄位:acc_no"
        assert "vou"        in df,"未含有傳票編號欄位:vou"
        assert "acc_name"   in df,"未含有科目名稱欄位:acc_name"
        assert "note"       in df,"未含有摘要欄位:note"
        assert "debit"      in df,"未含有借方欄位:debit"
        assert "credit"     in df,"未含有貸方欄位:credit"
        #顯示借貸方差額
        diff = df["debit"].sum() - df["credit"].sum()
        await sio.emit('msg',"借貸方差額={}".format(diff), room=sid)
    except Exception as e:
        await sio.emit('error',str(e), room=sid)
    else:
        await sio.emit('msg',"通過檢查", room=sid)
        ledger = df
        unique = ledger[["acc_no","acc_name"]].drop_duplicates().to_json(orient="records")
        await sio.emit('set_account',unique, room=sid)


#async def output(sid):
#    await sio.emit('msg',df.to_json(),room=sid)

class sampler(object):
    def __init__(self,df,column,method,criteria,exclude=[]):
        self.df       =  df
        self.column   =  column
        self.method   =  method
        self.criteria =  criteria
        self.exclude  =  exclude
    
if __name__ == '__main__':
    host,port="127.0.0.1",8888
    web.run_app(app,host=host,port=port)