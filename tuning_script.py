from program.optimize import set_memory, get_memory,set_mysql,get_mysql

def main():
    import argparse

    # 创建解析器
    parser = argparse.ArgumentParser(description="调优管理脚本")

    # 添加命令行参数
    parser.add_argument('action', choices=['set_memory', 'get_memory','set_mysql','get_mysql'], 
                        help='要执行的操作: set (启动调优或恢复环境), get (获取调优结果)')
    parser.add_argument('--flag', type=bool, choices=[True,False], default=0, 
                        help='控制操作的标志: False (不做处理), True (启动调优)')

    # 解析命令行参数
    args = parser.parse_args()

    if args.action == 'set_memory':
        # 根据 flag 值调用 set_memory 函数
        set_memory(args.flag)
    elif args.action == 'get_memory':
        # 调用 get_memory 函数并打印结果
        result = get_memory()
        print("调优结果:\n", result)

    elif args.action == 'set_mysql':
        # 根据 flag 值调用 set_mysql 函数
        set_mysql(args.flag)
    elif args.action == 'get_mysql':
        # 调用 get_memory 函数并打印结果
        result = get_mysql()
        print("调优结果:\n", result)

if __name__ == "__main__":
    main()