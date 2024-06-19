<template>
  <div>
    <div class="container1">
      <div style="background-color:#b2e1f8;" class="card">
        <div>
          <h4 style="color: rgb(115, 114, 114);font-weight: 400;">磁盘I/O量</h4>
          <h2>{{ perfData.disk_read_bytes }}/{{ perfData.disk_write_bytes }}/s</h2>
        </div>
        <img src="../images/cd.IO.png" class="icon">
      </div>
      <div style="background-color:#cef3d4;" class="card">
        <div>
          <h4 style="color: rgb(115, 114, 114);font-weight: 400;">网络I/O量</h4>
          <h2>{{ perfData.recv_bytes }}/{{ perfData.sent_bytes }}/s</h2>
        </div>
        <img src="../images/intel.IO.png" class="icon">
      </div>
    </div>

    <div>
      <div class="container1">
        <div style="background-color:#F6F7E7;" class="card">
          <div>
            <h4 style="color: rgb(115, 114, 114);font-weight: 400;">磁盘读写次数</h4>
            <h2>{{ perfData.disk_read_count }}/{{ perfData.disk_write_count }}/s</h2>
          </div>
          <img src="../images/cd.rw.png" class="icon">

        </div>
        <div style="background-color:#FFEDE6;" class="card">
          <div>
            <h4 style="color: rgb(115, 114, 114);font-weight: 400;">网络读写次数</h4>
            <h2>{{ perfData.recv_count }}/{{ perfData.sent_count }}/s</h2>
          </div>
          <img src="../images/intel.rw.png" class="icon">
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="pid" label="pid" width="280">
      </el-table-column>
      <el-table-column prop="name" label="进程" width="280">
      </el-table-column>
      <el-table-column prop="disk_read_bytes" label="磁盘读写量" width="280">
      </el-table-column>
      <el-table-column prop="disk_write_bytes" label=" " width="280">
      </el-table-column>
      <el-table-column prop="sent_bytes" label="网络I/O量" width="280">
      </el-table-column>
      <el-table-column prop="recv_bytes" label=" " width="280">
      </el-table-column>
      <el-table-column prop="cpu_usage" label="cpu使用量" width="280">
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
        sent_count: '--',
        recv_count: '--',
        sent_bytes: '--',
        recv_bytes: '--',
        disk_read_bytes: '--',
        disk_write_bytes: '--',
        disk_read_count: '--',
        disk_write_count: '--',
        cpu_usage: '--'
      }
    };
  },
  methods: {
    async fetchData(url) {
      // 执行需要轮询的操作 
      try {
        const response = await fetch(url); // 等待fetch完成并返回结果  
        const data = await response.json(); // 等待解析响应数据并返回结果  
        console.log(data); // 打印解析后的数据
        return data;
      } catch (error) {
        console.error('Error:', error); // 捕获并打印错误信息  
      }
    },
    async function(){
      // 调用需要轮询的方法 
      var data = await this.fetchData('/api/proc');
      this.tableData = data;
      this.tableData.forEach(function(element){
        element.disk_read_bytes=this.convert(element.disk_read_bytes);
        element.disk_write_bytes=this.convert(element.disk_write_bytes);
        element.sent_bytes=this.convert(element.sent_bytes);
        element.recv_bytes=this.convert(element.recv_bytes);
      });
      data = await this.fetchData('/api/perf');

      this.perfData = data;
      this.perfData.disk_read_bytes=this.convert(this.perfData.disk_read_bytes);
      this.perfData.disk_write_bytes=this.convert(this.perfData.disk_write_bytes);
      this.perfData.recv_bytes=this.convert(this.perfData.recv_bytes);
      this.perfData.sent_bytes=this.convert(this.perfData.sent_bytes);
    },
    convert(bytes){
      if(bytes>1e9)
        return bytes/1e9+'GB'
      else if(bytes>1e6)
        return bytes/1e6+'MB'
      else if(bytes>1e3)
        return bytes/1e3+'KB'
      else
        return bytes+'B'
    }
  },
  async mounted() {
  //   setInterval(() => {

  //   }, 1000);
  //   // 每隔一段时间执行某个方法 
  //   this.pollingTimer = setInterval(async function(){
  //     this.fetchData();
  //     // 调用需要轮询的方法 cd
  //     this.tableData = await this.fetchData('/api/proc');
  //     var data = await this.fetchData('/api/perf');
  //     this.perfData = data;
  //   }, 1000); // 1秒为例，可以根据需求调整时间间隔 
  // },
  setInterval(() => {
    this.function();
  }, 1000);
  // this.function();
  }
}
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
