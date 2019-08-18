<template>
<div class="col-sm">
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
  props: ['rules','mapping','file_status'],
  data:function(){
      return{
        select_account:[],
        select_rule:"",
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