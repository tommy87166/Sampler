import io from "socket.io-client"
import jQuery from "jquery"
import "bootstrap"
import 'bootstrap/dist/css/bootstrap.min.css'
import Vue from 'vue/dist/vue.js'
import VueSocketIO from 'vue-socket.io';

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

window.jQuery = jQuery;
window.Vue    = Vue;