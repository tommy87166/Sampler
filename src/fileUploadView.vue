<template>
    <div class="col-sm">
        <div class="card no-border">
            <div class="card-body">
                <h5 class="card-title"><b>選擇檔案</b></h5>
                <input type="file" id="file" multiple="multiple"/>
                
                <ul class="list-group list-group-flush">
                    <li class="list-group-item no-border">
                        檔案狀態 
                        <span v-if="file_status.status == true" class="badge badge-success">正確</span>
                        <span v-if="file_status.status == false" class="badge badge-danger">錯誤</span>
                        <span v-if="file_status.status == null" class="badge badge-secondary">請選擇檔案</span>
                    </li>
                    <li v-if="file_status.status == false"  class="list-group-item no-border">錯誤原因 {{file_status.reason}}</li>
                    <li v-if="file_status.status == true" class="list-group-item no-border">{{file_status.row}} 列 X {{file_status.column}} 欄，借貸方差額 = {{file_status.diff}}</li>
                </ul>

            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h5 class="card-title"><b>說明</b></h5>
                <p class="card-text">你的 Excel 明細帳檔案需包含以下欄位，並且依以下規則命名欄位。</p>
                <p class="card-text">明細帳借貸方加總應相等，系統會提示借貸方差額。</p>
                <table class="table">
                    <thead>
                        <tr>
                            <th scope="col">欄位</th>
                            <th scope="col">命名</th>
                            <th scope="col">備註</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>日期</td>
                            <td>date</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>科目編號</td>
                            <td>acc_no</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>科目名稱</td>
                            <td>acc_name</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>傳票編號</td>
                            <td>vou</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>摘要</td>
                            <td>note</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>借方</td>
                            <td>debit</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>貸方</td>
                            <td>credit</td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
module.exports = {
  props: ['file_status']
}
</script>


<style scoped></style>

