<template>
<div class="col-sm" >
    
    <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups" style="margin-bottom: 10px;">
        <div class="btn-group mr-2" role="group" aria-label="First group">
            <button type="button" class="btn btn-outline-secondary" v-on:click="saveRule" >保存規則集</button>
        </div>
        <div class="btn-group mr-2" role="group" aria-label="Second group">
            <button type="button" class="btn btn-outline-secondary" v-on:click="readRule" >讀取規則集</button>
        </div>
    </div>
    
    <table class="table">
        <thead>
            <tr>
                <th scope="col">#</th>
                <th scope="col">名稱</th>
                <th scope="col">方法</th>
                <th scope="col">方向</th>
                <th scope="col">參數</th>
                <th scope="col"></th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <th scope="row"></th>
                <td>
                    <input v-model="name" class="form-control" required type="text" placeholder="名稱" />
                </td>
                <td>
                    <select v-model="method" class="custom-select">
                        <option value="order">個數</option>
                        <option value="percent">比例</option>
                    </select>
                </td>
                <td>
                    <select v-model="direction" class="custom-select">
                        <option value="debit">借方</option>
                        <option value="credit">貸方</option>
                    </select>
                </td>
                <td>
                    <div class="input-group mb-3">
                        <input v-model="criteria" class="form-control" min="0" required type="number" />
                         <div class="input-group-append">
                            <span v-if=' method == "order" ' class="input-group-text">筆</span>
                            <span v-if=' method == "percent" ' class="input-group-text">%</span>
                        </div>
                    </div>
                </td>
                <td>
                    <button v-on:click="addRule" type="button" class="btn btn-success">新增</button>
                </td>
            </tr>

            <tr v-for="(item, key, index) in rules">
                <th scope="row">{{index + 1}}</th>
                <td>{{item.name}}</td>
                <td>
                    <select v-model="item.method" class="custom-select">
                        <option value="order">個數</option>
                        <option value="percent">比例</option>
                    </select>
                </td>
                <td>
                    <select v-model="item.direction" class="custom-select">
                        <option value="debit">借方</option>
                        <option value="credit">貸方</option>
                    </select>
                </td>
                <td>
                    <div class="input-group mb-3">
                        <input class="form-control" min="0" required type="number" v-model.number="item.criteria" />
                        <div class="input-group-append">
                            <span v-if=' item.method == "order" ' class="input-group-text">筆</span>
                            <span v-if=' item.method == "percent" ' class="input-group-text">%</span>
                        </div>
                    </div>
                </td>
                <td>
                    <button type="button" class="btn btn-danger" v-on:click="deleteRule" :data-name="item.name">刪除</button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
</template>


<script>
module.exports = {
  props: ['rules'],
  data:function(){
      return{
        name:"",
        method:"order",
        direction:"debit",
        criteria:3
      }
  },
  methods:{
      deleteRule:function(event){
          var name = event.target.getAttribute("data-name")
          console.log("Delete Rule",name)
          this.$socket.emit("delete_rule",name)
      },
      addRule:function(){
        console.log("Add Rule",this.name,this.method,this.direction,this.criteria)
        console.log(this.rules)
        if (this.name != "" && this.name.length > 0 && Object.keys(this.rules).indexOf(this.name) == -1 ){
            var rule = {
                "name"     : this.name, 
                "method"   : this.method,
                "direction": this.direction,
                "criteria" : this.criteria,
                "exclude"  : []
            }
            this.$socket.emit("set_rule",rule)
        } else {
            alert("名稱不得為空或已經存在")
        }
      },
      readRule:function(){
          this.$socket.emit("read_rule")
      },
      saveRule:function(){
          this.$socket.emit("save_rule")
      },
  }
}
</script>

<style scoped></style>