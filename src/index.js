import io from "socket.io-client"
import jQuery from "jquery"
import "bootstrap"
import 'bootstrap/dist/css/bootstrap.min.css'
import Vue from 'vue/dist/vue.js'
import VueSocketIO from 'vue-socket.io';
import fileUploadView from "./fileUploadView.vue"

var socket = io();

Vue.use(new VueSocketIO({
    debug: true,
    connection: socket
}));

document.addEventListener('DOMContentLoaded', function () {
    const fileUploader = document.querySelector('#file');
    fileUploader.addEventListener('change', (e) => {
        let form = new FormData();
        form.append("socket",socket.id)
        form.append("file",fileUploader.files[0])
        fetch("/upload",{method:'post',body:form})
    });
});

new Vue({
    el: '#notify',
    data: {
        message: [],
    },
    updated:function(){
        var obj = jQuery("#notify > .col-sm > .card")
        obj.animate({scrollTop: obj.offset().top})
    },
    sockets:{
        connect:function(data){
            this.message.push("Info:已連線到伺服器")
        },
        msg:function(data){
            this.message.push("Info:"+data)
        },
        error:function(data){
            this.message.push("Error:"+data)
        }
    }
})

window.jQuery = jQuery;
window.Vue    = Vue;
window.fileUploadView  = fileUploadView;