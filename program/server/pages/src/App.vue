<template>
  <div class="full-page">
    <div class="title">系统监测平台</div>
    <div class="line">
      <hr style="width: 25%; ">
    </div>
    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick" type="card">
      <el-tab-pane label="性能数据" name="first" class="demo-tab-pane">
        <div class="back">
          <div class="wrap" style="margin-top: 20px;">
            <div class="board">
              <div id="myChart1" style="width:20vw;height:300px;"></div>
              <div class="show">
                <img src="../src/assets/planet.png">
                <div class="text">磁盘读取量:</div>
                <div class="data">{{ perfData.disk_read_bytes }}/s</div>
              </div>
              <div class="show">
                <img src="../src/assets/data.png">
                <div class="text">磁盘写入量:</div>
                <div class="data">{{ perfData.disk_write_bytes }}/s</div>
              </div>
            </div>
            <div class="board">
              <div id="myChart2" style="width:20vw;height:300px;"></div>
              <div class="show">
                <img src="../src/assets/planet.png">
                <div class="text">网络发送量:</div>
                <div class="data">{{ perfData.sent_bytes }}/s</div>
              </div>
              <div class="show">
                <img src="../src/assets/data.png">
                <div class="text">网络接收量:</div>
                <div class="data">{{ perfData.recv_bytes }}/s</div>
              </div>
            </div>
          </div>
          <div class="wrap">
            <div class="board">
              <div id="myChart3" style="width:20vw;height:300px;"></div>
              <div class="show">
                <img src="../src/assets/planet.png">
                <div class="text">磁盘读取次数:</div>
                <div class="data">{{ perfData.disk_read_count }}/s</div>
              </div>
              <div class="show">
                <img src="../src/assets/data.png">
                <div class="text">磁盘写入次数:</div>
                <div class="data">{{ perfData.disk_write_count }}/s</div>
              </div>
            </div>
            <div class="board">
              <div id="myChart4" style="width:20vw;height:300px;"></div>
              <div class="show">
                <img src="../src/assets/planet.png">
                <div class="text">网络发送次数:</div>
                <div class="data">{{ perfData.sent_count }}/s</div>
              </div>
              <div class="show">
                <img src="../src/assets/data.png">
                <div class="text">网络接收次数:</div>
                <div class="data">{{ perfData.recv_count }}/s</div>
              </div>
            </div>
          </div>
        </div>

        <div class="table-wrap">
          <el-scrollbar class="scrollbar-wrapper">
            <el-table :data="tableData" style="width: 100%"
              :header-cell-style="{ background: '#100c2a30', color: '#C0C2C6' }">
              <el-table-column prop="pid" label="pid" width="160" :sortable="true">
              </el-table-column>
              <el-table-column prop="name" label="进程" width="160" :sortable="true">
              </el-table-column>
              <el-table-column prop="disk_read_bytes" label="磁盘读取量" width="160" :sortable="true">
              </el-table-column>
              <el-table-column prop="disk_write_bytes" label="磁盘写入量" width="160" :sortable="true">
              </el-table-column>
              <el-table-column prop="sent_bytes" label="网络发送量" width="160" :sortable="true">
              </el-table-column>
              <el-table-column prop="recv_bytes" label="网络接受量" width="160" :sortable="true">
              </el-table-column>
              <el-table-column prop="cpu_percent" label="CPU使用量" width="160" :sortable="true">
              </el-table-column>
            </el-table>
          </el-scrollbar>
        </div>
      </el-tab-pane>

      <el-tab-pane label="性能火焰图" name="second" class="flame-graph-pane">
        <iframe class="flame-graph" id="flame-graph" :src="url"></iframe>
        <div style="display: flex; flex-direction: row; align-items: center;">
          <button class="regen-btn" @click="onRegen">重新生成</button>
          <span style="color: white;">目标进程PID:</span><input type="text" class="regen-pid" v-model="regenPID">
        </div>
      </el-tab-pane>

      <el-tab-pane label="调优策略" name="third">
        <div class="way">
          <div id="main" style="width: 800px; height: 400px"></div>
          <div>
            <div class="button">
              <el-switch v-model="optimizers[0]" />
              <div class="text">NUMA节点适配</div>
              <el-switch v-model="optimizers[1]" />
              <div class="text">本地网络回环流量优化</div>
              <el-switch v-model="optimizers[2]" />
              <div class="text">策略三</div>
              <el-switch v-model="optimizers[3]" />
              <div class="text">策略四</div>
              <el-switch v-model="optimizers[4]" />
              <div class="text">策略五</div>
            </div>
            <img src="../src/assets/data.jpg" style="margin-top: 20px; width: 800px;">
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { ElTable, ElTableColumn, ElTabs, ElTabPane, ElScrollbar, ElSwitch } from 'element-plus';

const DATA_LENGTH = 7;

export default {
  components: {
    'el-scrollbar': ElScrollbar,
    'el-table': ElTable,
    'el-table-column': ElTableColumn,
    'el-tabs': ElTabs,
    'el-tab-pane': ElTabPane,
    'el-switch': ElSwitch,
  },
  name: 'LineChart',
  data() {
    return {
      optimizers: [false, false, false, false, false],
      activeName: 'first',
      regenPID: '',
      url: '/static/flame_graph.svg',
      tableData: [
      ],
      perfname: [['disk_write_bytes', 'disk_read_bytes'], ['sent_bytes', 'recv_bytes'], ['disk_write_count', 'disk_read_count'], ['sent_count', 'recv_count']],
      convertname: ['disk_write_bytes', 'disk_read_bytes', 'sent_bytes', 'recv_bytes'],
      echartsOption1: {    // echarts选项，所有绘图数据和样式都在这里设置
        legend: {   //图表上方的图例
          data: ['磁盘写入量', '磁盘输出量']
        },
        animation: false,
        xAxis: {
          type: 'category',
          data: [...Array(DATA_LENGTH)].map((v, idx) => idx + 1),   // x轴数据
          name: '',   // x轴名称
          nameTextStyle: {    // x轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '数量',   // y轴名称
          nameTextStyle: {    // y轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        tooltip: {   //鼠标放到图上的数据展示样式
          trigger: 'axis'
        },
        series: [   //每条折线的数据系列
          {
            name: '磁盘写入量',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          },
          {
            name: '磁盘读取量',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          }
        ],
      },
      echartsOption2: {    // echarts选项，所有绘图数据和样式都在这里设置
        legend: {   //图表上方的图例
          data: ['网络发送量', '网络接收量']
        },
        animation: false,
        xAxis: {
          type: 'category',
          data: [...Array(DATA_LENGTH)].map((v, idx) => idx + 1),   // x轴数据
          name: '',   // x轴名称
          nameTextStyle: {    // x轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '数量',   // y轴名称
          nameTextStyle: {    // y轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        tooltip: {   //鼠标放到图上的数据展示样式
          trigger: 'axis'
        },
        series: [   //每条折线的数据系列
          {
            name: '网络发送量',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          },
          {
            name: '网络接收量',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          }
        ],
      },
      echartsOption3: {    // echarts选项，所有绘图数据和样式都在这里设置
        legend: {   //图表上方的图例
          data: ['磁盘写入次数', '磁盘读入次数']
        },
        animation: false,
        xAxis: {
          type: 'category',
          data: [...Array(DATA_LENGTH)].map((v, idx) => idx + 1),   // x轴数据
          name: '',   // x轴名称
          nameTextStyle: {    // x轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '次数',   // y轴名称
          nameTextStyle: {    // y轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        tooltip: {   //鼠标放到图上的数据展示样式
          trigger: 'axis'
        },
        series: [   //每条折线的数据系列
          {
            name: '磁盘写入次数',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          },
          {
            name: '磁盘读入次数',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          }
        ],
      },
      echartsOption4: {    // echarts选项，所有绘图数据和样式都在这里设置
        legend: {   //图表上方的图例
          data: ['网络发送次数', '网络接收次数']
        },
        animation: false,
        xAxis: {
          type: 'category',
          data: [...Array(DATA_LENGTH)].map((v, idx) => idx + 1),   // x轴数据
          name: '',   // x轴名称
          nameTextStyle: {    // x轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '次数',   // y轴名称
          nameTextStyle: {    // y轴名称样式
            fontWeight: 400,
            fontSize: 12
          }
        },
        tooltip: {   //鼠标放到图上的数据展示样式
          trigger: 'axis'
        },
        series: [   //每条折线的数据系列
          {
            name: '网络写入次数',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          },
          {
            name: '网络读入次数',
            data: [0, 0, 0, 0, 0, 0, 0],
            type: 'line'
          }
        ],
      },
      option: {
        title: {
          text: '场景分析'
        },
        tooltip: {},
        legend: {
          type: 'scroll',
          width: '20%',
          pageButtonItemGap: 4,
          show: true,
          icon: 'rect',
          top: '14',
          left: '430',
          itemWidth: 20,
          itemHeigth: 10,
          itemGap: 30,
          orient: 'horizontal',
          data: ['数据库系统']
        },
        radar: {
          center: ['50%', '56%'],
          radius: 160,
          startAngle: 90,
          name: {
            formatter: '{value}',
            textStyle: { fontSize: 15, color: 'green' }
          },
          indicator: [
            { name: '常态', max: 1.00 },
            { name: '集中式数据库', max: 1.00 },
            { name: 'CPU瓶颈', max: 1.00 },
            { name: '分布式数据库', max: 1.00 },
            { name: '文件IO瓶颈', max: 1.00 },
            { name: '内存瓶颈', max: 1.00 },
            { name: '网络瓶颈', max: 1.00 },
          ]
        },
        color: ['#45C2E0'],
        series: [
          {
            itemStyle: {
              normal: { lineStyle: { width: 1 }, opacity: 0.2 },
              emphasis: { lineStyle: { width: 5 }, opacity: 1 }
            },
            type: 'radar',
            data: [
              {
                value: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                name: '数据库系统'
              }
            ]
          }
        ]
      },
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
      },
    }
  },
  mounted() {
    let myChart1 = echarts.init(document.getElementById("myChart1"), 'dark'); // 初始化echarts, theme为dark
    myChart1.setOption(this.echartsOption1)   // echarts设置选项
    let myChart2 = echarts.init(document.getElementById("myChart2"), 'dark'); // 初始化echarts, theme为dark
    myChart2.setOption(this.echartsOption2)   // echarts设置选项
    let myChart3 = echarts.init(document.getElementById("myChart3"), 'dark'); // 初始化echarts, theme为dark
    myChart3.setOption(this.echartsOption3)   // echarts设置选项
    let myChart4 = echarts.init(document.getElementById("myChart4"), 'dark'); // 初始化echarts, theme为dark
    myChart4.setOption(this.echartsOption4)   // echarts设置选项
    let myChart5 = echarts.init(document.getElementById("main"), 'dark'); // 初始化echarts, theme为dark
    myChart5.setOption(this.option);   // echarts设置选项

    setInterval(async () => {
      var data = await this.fetchData('/api/perf');
      this.tableData = await this.fetchData('/api/proc');
      Object.assign(this.perfData, data);
      for (var i = 0; i < this.convertname.length; i++) {
        this.perfData[this.convertname[i]] = this.convert(data[this.convertname[i]]);
      }

      //console.log(this.echartsOption2.series[0].data);
      for (var i = 0; i < this.perfname.length; i++) {
        this.replace(`echartsOption${i + 1}`, data[this.perfname[i][0]], data[this.perfname[i][1]]);
      }
      myChart1.setOption(this.echartsOption1);
      myChart2.setOption(this.echartsOption2);
      myChart3.setOption(this.echartsOption3);
      myChart4.setOption(this.echartsOption4);
    }, 1000);

    setInterval(async () => {
      var confidence = await this.fetchData('/api/confidence');
      for (var i = 0; i < confidence[0].length; i++){
        confidence[0][i] = this.clamp(1.0 + Math.log10(confidence[0][i]) * 0.4, 0.0, 1.0);
      }
      this.option.series[0].data[0].value = confidence[0];
      myChart5.setOption(this.option);
    }, 2000);
  },
  methods: {
    handleClick(tab, event) {
      console.log(tab, event)
    },
    clamp(x, a, b){
      return x < a ? a : x > b ? b : x;
    },
    async onRegen(){
      alert('开始生成，需要等待几秒钟');
      await fetch(`/api/flame_graph?${this.regenPID}`);
      const frame = document.getElementById('flame-graph').contentWindow;
      frame.location.reload();
      alert("生成已完成");
    },
    async fetchData(url) {
      // 执行需要轮询的操作 
      try {
        const response = await fetch(url); // 等待fetch完成并返回结果  
        const data = await response.json(); // 等待解析响应数据并返回结果  
        //console.log(data); // 打印解析后的数据
        return data;
      } catch (error) {
        console.error('Error:', error); // 捕获并打印错误信息  
      }
    },
    convert(bytes) {
      if (bytes > 1e9)
        return (bytes / 1e9).toFixed(2) + 'GB'
      else if (bytes > 1e6)
        return (bytes / 1e6).toFixed(2) + 'MB'
      else if (bytes > 1e3)
        return (bytes / 1e3).toFixed(2) + 'KB'
      else
        return bytes.toFixed(2) + 'B'
    },
    async convertProcs() {
      // 调用需要轮询的方法 
      var data = await this.fetchData('/api/proc');
      this.tableData = data;
      this.tableData.forEach((element) => {
        element.disk_read_bytes = this.convert(element.disk_read_bytes);
        element.disk_write_bytes = this.convert(element.disk_write_bytes);
        element.sent_bytes = this.convert(element.sent_bytes);
        element.recv_bytes = this.convert(element.recv_bytes);
      });
    },
    replace(name, data1, data2) {
      for (var t in [0, 1]) {
        var arr = this[name].series[t].data;
        var temp = [];
        for (var i = 1; i < arr.length; i++) {
          temp.push(arr[i]);
        }
        temp.push([data1, data2][t]);
        this[name].series[t].data = temp;
      }
    },
    convert(bytes) {
      if (bytes > 1e9)
        return (bytes / 1e9).toFixed(2) + 'GB'
      else if (bytes > 1e6)
        return (bytes / 1e6).toFixed(2) + 'MB'
      else if (bytes > 1e3)
        return (bytes / 1e3).toFixed(2) + 'KB'
      else
        return bytes.toFixed(2) + 'B'
    }
  }
}
</script>

<style scoped>
.demo-tabs>.el-tabs__content {
  padding: 32px;
  color: #fff;
  font-size: 100px;
  font-weight: 800;
}

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

.demo-tabs>.el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

.full-page {
  width: 100vw;
  height: 100vh;
  background-image: url('assets/background.jpg');
  /* 设置背景图片 */
  background-size: cover;
  /* 背景图片覆盖整个div */
  background-position: center;
  /* 背景图片居中 */
  position: fixed;
  top: 0;
  left: 0;
  z-index: 0;
}

.title {
  color: aliceblue;
  font-size: 50px;
  font-weight: 500;
  letter-spacing: 7px;
  text-align: center;
}

.line {
  display: flex;
  justify-content: center;
}

hr {
  height: 20px;
  background: radial-gradient(circle at 50% -300%, #5080FF 5%, transparent 95%);
  border: 0;
}

.show {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-top: 3px;
}

.text {
  color: #fff;
  font-weight: 300;
  font-size: 15px;
  margin-top: 3px;
  margin-left: 2px;
  letter-spacing: 2px;
}

.data {
  color: #fff;
  font-size: 20px;
}

.board {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px;
}

.wrap {
  display: flex;
  justify-content: flex-start;
  width: 650px;
}

.back {
  background-image: url('assets/border.png');
  /* 设置背景图片 */
  background-size: cover;
  /* 背景图片覆盖整个div */
  background-position: center;
  width: 45vw;
  border-radius: 30px;
  padding-top: 10px;
  border-color: #1f3779;
  border-width: 2px;
  box-shadow: 1px 1px 1px 1px #5080FF;
  /* 背景图片居中 */
}

.scrollbar-wrapper {
  height: 790px;
  /* 设置你希望的滑动区域的高度 */
}

.table-wrap {
  background-image: url('assets/border.png');
  /* 设置背景图片 */
  background-size: cover;
  /* 背景图片覆盖整个div */
  background-position: center;
  border-radius: 30px;
  position: absolute;
  width: 50vw;
  top: 0;
  right: 0;
  padding: 30px;
  box-shadow: 1px 1px 1px 1px #5080FF;
}

/* 修改头部背景 */
::v-deep .el-table th {
  background-color: rgba(0.06, 0.05, 0.2, 0.2);
}

/* 修改行背景 */
::v-deep .el-table tr {
  background: radial-gradient(#20306F, #101c7a);
}

/* 修改行内文字居中 */
::v-deep .el-table td,
.el-table th {
  text-align: center;
  color: #fff;
}

/* 修改行内线 */
::v-deep .el-table td,
.building-top .el-table th.is-leaf {
  border-bottom: 1px solid #007ACC;
}

.el-table th.el-table__cell {
  color: #fff;
}

.el-table-border .el-table__header-wrapper tr {
  border-bottom: 1px solid #ff0000;
  /* 设置行线颜色为红色 */
}

.el-table {
  --el-table-border: 1px solid #007ACC !important;
  --el-table-row-hover-bg-color: rgb(2, 2, 189) !important;
}

.way {
  display: flex;
}

.button {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  margin-left: 20px;
}

.text {
  margin-left: 15px;
  margin-right: 15px;
  color: green;
}

.flame-graph-pane {
display: flex;
align-items: center;
justify-content: center;
flex-direction: column;
}

.flame-graph {
display: block;
height: 670px;
width: 1210px;
}

.regen-btn {
display: block;
height: 60px;
width: 120px;
color: white;
background: radial-gradient(#20306F, #101c7a);
margin: 20px;
}


.regen-pid {

}

</style>
