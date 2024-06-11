#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

// 定义 TCP 发送和接收字节数的 BPF 映射
BPF_HASH(tcp_loopback_bytes, struct sock *, u64);

// 监测 TCP 流量
int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk,  struct msghdr *msg, size_t size) {
    // 检查是否为本地环回流量
    if (sk->__sk_common.skc_daddr == sk->__sk_common.skc_rcv_saddr) {
        u64 *bytes = tcp_loopback_bytes.lookup_or_init(sk, &(u64){0});
        *bytes += size;
    }
    return 0;
}
