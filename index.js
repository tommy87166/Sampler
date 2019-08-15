const express = require('express');
const app = express();
// 加入這兩行
const server = require('http').Server(app);
const io = require('socket.io')(server);
 
app.get('/', (req, res) => {
    res.sendFile( __dirname + '/view/index.html');
});
 
// 當發生連線事件
io.on('connection', (socket) => {
    console.log('Hello!');  // 顯示 Hello!
 
    // 當發生離線事件
    socket.on('disconnect', () => {
        console.log('Bye~');  // 顯示 bye~
    });
});
 
// 注意，這邊的 server 原本是 app
server.listen(3000, () => {
    console.log("Server Started. http://localhost:3000");
});