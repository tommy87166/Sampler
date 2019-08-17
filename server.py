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
    
if __name__ == '__main__':
    host,port="127.0.0.1",8888
    loop = asyncio.get_event_loop()
    web.run_app(app,host=host,port=port)