<template>
  <div>
    <div class="container1">
      <div style="background-color:#b2e1f8;" class="card">
        <div>
          <h4 style="color: rgb(115, 114, 114);font-weight: 400;">磁盘I/O量</h4>
          <h2>{{perfData.block_io}}/s</h2>
        </div>
        <img src="../images/cd.IO.png" class="icon">
      </div>
      <div style="background-color:#cef3d4;" class="card">
        <div>
          <h4 style="color: rgb(115, 114, 114);font-weight: 400;">网络I/O量</h4>
          <h2>{{perfData.net_io}}/s</h2>
        </div>
        <img src="../images/intel.IO.png" class="icon">
      </div>
    </div>

    <div>
      <div class="container1">
        <div style="background-color:#F6F7E7;" class="card">
          <div>
            <h4 style="color: rgb(115, 114, 114);font-weight: 400;">磁盘读写次数</h4>
            <h2>{{ perfData.block_io_cnt }}/s</h2>
          </div>
          <img src="../images/cd.rw.png" class="icon">

        </div>
        <div style="background-color:#FFEDE6;" class="card">
          <div>
            <h4 style="color: rgb(115, 114, 114);font-weight: 400;">网络读写次数</h4>
            <h2>{{ perfData.net_io_cnt }}/s</h2>
          </div>
          <img src="../images/intel.rw.png" class="icon">
        </div>
      </div>
    </div>
  </div>
  
  <div>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="name" label="进程" width="380">
      </el-table-column>
      <el-table-column prop="block_io" label="磁盘I/O量" width="380">
      </el-table-column>
      <el-table-column prop="net_io" label="网络I/O量">
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { ElTable, ElTableColumn } from 'element-plus';

export default {
    components: { ElTable, ElTableColumn },
    data() {
        return {
          tableData: [],
          perfData: {
            cpu: '--',
            memory: '--',
            block_io: '--',
            block_io_cnt: '--',
            net_io: '--',
            net_io_cnt: '--'
          }
        };
    },
    methods: {
      async fetchData(url){  
        try {
          const response = await fetch(url); // 等待fetch完成并返回结果  
          const data = await response.json(); // 等待解析响应数据并返回结果  
          console.log(data); // 打印解析后的数据
          return data;
        } catch (error) {  
          console.error('Error:', error); // 捕获并打印错误信息  
        }  
      }
    },
    async mounted(){
      setInterval(() => {
        this.tableData = await this.fetchData('/api/proc');
        var data= await this.fetchData('/api/perf');
        this.perfData=data;
      }, 1000);
    }
};
</script>

<style scoped>
.container1 {
  display: flex;
  justify-content: space-around;
}

.card {
  display: flex;
  padding: 20px;
  border-radius: 20px;
  width: 40vw;
  height: 30vh;
  margin-top: 20px;
  margin-left: 20px;
  margin-right: 20px;
}

.icon {
  height: 150px;
  width: 150px;
  margin-top: 5px;
  margin-left: 250px;
}

h4 {
  size: 200px;
}
</style>
