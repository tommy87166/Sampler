<template>
<div class="col-sm">

    <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups" style="margin-bottom: 10px;">
        <div class="btn-group mr-2" role="group" aria-label="First group">
            <button type="button" class="btn btn-outline-secondary" v-on:click="toggleuploadmappingview">上傳對應</button>
            <button type="button" class="btn btn-outline-secondary" v-on:click="downloadMapping">下載對應</button>
            <button type="button" class="btn btn-outline-secondary" v-on:click="toggleexpandview">母體放大設定</button>
        </div>
        <div class="btn-group mr-2" role="group" aria-label="Second group">
            <button type="button" class="btn btn-outline-success" v-on:click="sample" >執行對應</button>
        </div>
        <a id="download_link" style="display: none;" download="mapping.json"></a>
    </div>

    <div v-if = "uploadmappingview" class="card no-border" style="margin-bottom: 10px;">
        <div class="card-body">
            <input type="file" @change="loadTextFromFile" id="file_mapping"/>
        </div>
    </div>

    <div v-if = "expandview" class="card no-border" style="margin-bottom: 10px;">
        <div class="card-body">
            <h5 class="card-title"><b>母體放大設定</b></h5>
            <p class="card-text">期中執行抽樣時，可能需要將母體放大至整個查核期間。下面可以指定目前資料涵蓋月份和欲放大至月份。</p>
            <p class="card-text">以下設定將會將母體 / {{ expand[0] }} * {{ expand[1] }}</p>

            <div class="form-group">
                <label for="exampleInputEmail1">目前期間</label>
                <div class="input-group mb-3">
                    <input type="number" min = "1" v-model.number="expand[0]" class="form-control" >
                    <div class="input-group-append">
                        <span class="input-group-text" id="basic-addon2">月(或任何單位)</span>
                    </div>
                </div>
            </div>

            <div class="form-group">
                <label for="exampleInputEmail1">目標期間</label>
                <div class="input-group mb-3">
                    <input type="number" min = "1" v-model.number="expand[1]" class="form-control" >
                    <div class="input-group-append">
                        <span class="input-group-text" id="basic-addon2">月(或任何單位)</span>
                    </div>
                </div>
            </div>

            
        </div>
    </div>

    <table class="table">
            <thead>
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">規則</th>
                    <th scope="col">科目</th>
                    <th scope="col"></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th scope="row"></th>
                    <td>
                        <select v-model="select_rule"  class="custom-select">
                            <option v-for="(item , key , index) in rules" :value="key">{{key}}</option>
                        </select>
                    </td>
                    <td>
                        <select v-model="select_account" class="custom-select" multiple style="min-height: 300px">
                            <option v-for="(item , index) in leftaccount" :value="item.acc_no">{{item.acc_no}} {{item.acc_name}}</option>
                        </select>
                    </td>
                    <td>
                        <button type="button" class="btn btn-success" v-on:click="addMapping">新增/修改</button>
                    </td>
                </tr>

                <tr v-for="(item,key,index) in mapping">
                    <th scope="row">{{index + 1}}</th>
                    <td>{{key}}</td>
                    <td>
                        <p v-for="acc_no in item">{{acc_no}} {{accno2name(acc_no)}}</p>
                    </td>
                    <td><button type="button" class="btn btn-danger" v-on:click="deleteMapping" :data-name="key">刪除</button></td>
                </tr>
            </tbody>
    </table>
</div>
</template>

<script>
module.exports = {
  props: ['rules','file_status'],
  data:function(){
      return{
        select_account:[],
        select_rule:"",
        expand:[12,12],
        mapping:{},
        uploadmappingview:false,
        expandview:false,
      }
  },
  methods:{
    addMapping:function(){
        if (this.select_rule != "" && this.select_account.length > 0){
            var newObj = Object.assign({}, this.mapping);
            newObj[this.select_rule] = this.select_account
            this.mapping = newObj
        }
    },
    deleteMapping:function(event){
        var name = event.target.getAttribute("data-name")
        var newObj = Object.assign({}, this.mapping);
        delete newObj[name]
        this.mapping = newObj
    },
    accno2name:function(acc_no){
        var result = this.file_status.account.filter(
            function(data){
                if (data.acc_no == acc_no) {
                    return true
                }else{
                    return false
                }
            }
        )
        if (result.length==1){
            return result[0].acc_name
        }else{
            return ""
        }
    },
    sample:function(){
        var sample_setting = {
            mapping : this.mapping,
            expand  : this.expand
        }
        this.$socket.emit("sample",sample_setting)
    },
    downloadMapping:function(){
        var text = JSON.stringify(this.mapping)
        var data = new Blob([text], {type: 'text/plain'})
        var url = window.URL.createObjectURL(data)
        document.getElementById('download_link').href = url
        document.getElementById('download_link').click()
        window.URL.revokeObjectURL(url)
    },
    toggleuploadmappingview:function(){
        if (this.uploadmappingview){
            this.uploadmappingview = false
        }else{
            this.uploadmappingview = true
        }
    },
    toggleexpandview:function(){
        if (this.expandview){
            this.expandview = false
        }else{
            this.expandview = true
        }
    },
    loadTextFromFile:function(ev){
        const file = ev.target.files[0];
        const reader = new FileReader();
        reader.onload = function(e){
            var data = JSON.parse(e.target.result)
            console.log(data)
            this.mapping = data
        }.bind(this)
        reader.readAsText(file);
    }
  },
  computed:{
        leftaccount:function(){
            var selected = mergeDedupe(Object.values(this.mapping))
            var unselected = this.file_status.account.filter(
                function(data){
                    if (selected.indexOf(data.acc_no) == -1) {
                        return true
                    }else{
                        return false
                    }
                }
            )
            return unselected
        }
    },
}
</script>

<style scoped></style>