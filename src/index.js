console.log("Hello!")

import io from "socket.io-client"
import jQuery from "jquery"

var socket = io();
//Msg
socket.on("msg", function (data) {
    console.log("Info:",data)
    jQuery("#notify").append("<p>Info:"+data+"</p>")
});
socket.on("error", function (data) {
    console.log("Error:",data)
    jQuery("#notify").append("<p>Error:"+data+"</p>")
});
//Set Account
socket.on("set_account", function (data) {
    console.log("set_account:",data)
});

document.addEventListener('DOMContentLoaded', function () {
    const fileUploader = document.querySelector('#file');
    fileUploader.addEventListener('change', (e) => {
        let form = new FormData();
        form.append("socket",socket.id)
        form.append("file",fileUploader.files[0])
        fetch("/upload",{method:'post',body:form})
    });
});

window.jQuery = jQuery;