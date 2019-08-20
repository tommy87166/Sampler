<template>
<div class="col-sm">

    <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups" style="margin-bottom: 10px;">
        <div class="btn-group mr-2" role="group" aria-label="First group">
            <button type="button" class="btn btn-outline-secondary" v-on:click="toggleuploadmappingview">上傳對應</button>
            <button type="button" class="btn btn-outline-secondary" v-on:click="downloadMapping">下載對應</button>
        </div>
        <div class="btn-group mr-2" role="group" aria-label="Second group">
            <button type="button" class="btn btn-outline-success" v-on:click="sample" >執行抽樣</button>
        </div>
        <a id="download_link" style="display: none;" download="mapping.json"></a>
    </div>

    <div v-if = "uploadmappingview" class="card no-border" style="margin-bottom: 10px;">
        <div class="card-body">
            <input type="file" @change="loadTextFromFile" id="file_mapping"/>
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
        mapping:{},
        uploadmappingview:false
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
        this.$socket.emit("sample",this.mapping)
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