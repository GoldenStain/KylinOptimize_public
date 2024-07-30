#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>

// 定义 sock_ops 程序
int sock_ops_prog(struct bpf_sock_ops *ctx) {
    int op = (int)ctx->op;
    switch (op) {
        case BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB:
            // 连接建立后的处理逻辑
            bpf_sock_ops_cb_flags_set(ctx, BPF_SOCK_OPS_RETRANS_CB_FLAG);
            return 0;
        case BPF_SOCK_OPS_RETRANS_CB:
            // 重传事件的处理逻辑
            // 检查是否为本地回环连接
            if (ctx->family == AF_INET && ctx->local_ip4 == ctx->remote_ip4) {
                // 减小重传间隔
                // ctx->snd_cwnd = 1024;
                // ctx->srtt_us = 1000;
            }
            return 0;
        default:
            // 其他事件的默认处理
            return 0;
    }
}