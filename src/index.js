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
window.socket = socket;