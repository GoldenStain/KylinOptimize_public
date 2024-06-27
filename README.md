python版本3.7.9，从源代码编译安装
参考教程 https://blog.csdn.net/qq_42571592/article/details/122902266 1-4步骤

yum安装的库:
bcc-tools clang llvm llvm-devel llvm-static clang clang-devel clang-libs elfutils-devel elfutils-debuginfod-client-devel luajit-devel mesa-libGL

从github上安装的库：
iovisor/bcc 自己维护一份代码(bcc-source文件夹)，修改部分代码bug
项目中 src/python/bcc 文件夹内version.py文件去掉末尾的".in"再整体移动到 /usr/lib/python3.7/site-packages 里面去

eBPF监测的数据（单位时间内）:
磁盘IO量
磁盘IO次数
网络IO量
网络IO次数
CPU使用量
内存使用量

