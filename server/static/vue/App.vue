<script setup>
import HelloWorld from './HelloWorld.vue'
</script>

<template>
 <div>
    <div class="container1">
        <div style="background-color:#b2e1f8;" class="card">
            <div>
                <h4 style="color: rgb(115, 114, 114);font-weight: 400;">磁盘I/O量</h4>
                <h2>8992/s</h2>
            </div>
            <img src="../images/cd.IO.png" class="icon">
            
        </div>
        <div style="background-color:#cef3d4;" class="card">
            <div>
                <h4 style="color: rgb(115, 114, 114);font-weight: 400;">网络I/O量</h4>
                <h2>8992/s</h2>
            </div>
            <img src="../images/intel.IO.png" class="icon">
            
        </div>
    
</div>
<div>
    <div class="container1">
        <div style="background-color:#F6F7E7;" class="card">
            <div>
                <h4 style="color: rgb(115, 114, 114);font-weight: 400;">磁盘读写次数</h4>
                <h2>8992/s</h2>
            </div>
            <img src="../images/cd.rw.png" class="icon">
            
        </div>
        <div style="background-color:#FFEDE6;" class="card">
            <div>
                <h4 style="color: rgb(115, 114, 114);font-weight: 400;">网络读写次数</h4>
                <h2>8992/s</h2>
            </div>
            <img src="../images/intel.rw.png" class="icon">
            
        </div>
    </div>
  </div>
 </div>
</template>


<style scoped>
.container1{
        display: flex;
        justify-content:space-around ;
    }
.card{
    display: flex;
    padding: 20px;
    border-radius: 20px;
    width: 50vw;
    height: 30vh;
    margin-top: 20px;
    margin-left: 20px;
    margin-right: 20px;
   }
.icon{
    height: 150px;
    width: 150px;
    margin-top: 5px;
    margin-left: 250px;
}
h4{
    size: 200px;
}
</style>
