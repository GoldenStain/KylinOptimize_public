#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

BPF_HASH(send_bytes, struct sock *, u64);
BPF_HASH(recv_bytes, struct sock *, u64);

int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 *val, zero = 0;
	val = send_bytes.lookup_or_try_init(&sk, &zero);
	if (val){
		(*val) += size;
	}
	return 0;
}

int trace_tcp_recvmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 *val, zero = 0;
	val = recv_bytes.lookup_or_try_init(&sk, &zero);
	if (val){
		(*val) += size;
	}
	return 0;
}
