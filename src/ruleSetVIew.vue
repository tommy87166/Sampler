<template>
<div class="col-sm" >
    <table class="table">
        <thead>
            <tr>
            <th scope="col">#</th>
            <th scope="col">名稱</th>
            <th scope="col">方法</th>
            <th scope="col">方向</th>
            <th scope="col">參數</th>
            </tr>
        </thead>
        <tbody>
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
                    <input class="form-control" min="0" required type="number" v-model.number="item.criteria" debounce="1000" />
                </td>
            </tr>
        </tbody>
    </table>
</div>
</template>


<script>
module.exports = {
  props: ['rules']
}
</script>

<style scoped></style>