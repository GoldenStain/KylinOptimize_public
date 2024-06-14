#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <net/sock.h>
#include <linux/blkdev.h>
#include <bcc/proto.h>

// TCP IO量
BPF_HASH(send_bytes, u32, u64);
BPF_HASH(recv_bytes, u32, u64);

int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 *val, zero = 0;
	val = send_bytes.lookup_or_try_init(&pid, &zero);
	if (val){
		(*val) += size;
	}
	return 0;
}

int trace_tcp_recvmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 *val, zero = 0;
	val = recv_bytes.lookup_or_try_init(&pid, &zero);
	if (val){
		(*val) += size;
	}
	return 0;
}

// 磁盘读写
BPF_HASH(disk_read_bytes, u32, u64);
BPF_HASH(disk_write_bytes, u32, u64);
BPF_HASH(disk_read_count, u32, u64);
BPF_HASH(disk_write_count, u32, u64);

int trace_block_rq_insert(struct pt_regs *ctx, struct request *req){
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 zero = 0;
	if (req->cmd_flags & REQ_OP_WRITE){
		u64 *bytes = disk_write_bytes.lookup_or_init(&pid, &zero);
		*bytes += req->__data_len;
		u64 *count = disk_write_count.lookup_or_init(&pid, &zero);
		(*count)++;
	}
	return 0;
}

int trace_disk_read(struct pt_regs *ctx, struct request *req){
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 zero = 0;
	
	u64 *bytes = disk_read_bytes.lookup_or_init(&pid, &zero);
	*bytes += req->__data_len;
	u64 *count = disk_read_count.lookup_or_init(&pid, &zero);
	(*count)++;

	return 0;
}

// CPU、内存使用
BPF_HASH(start_times, u32, u64);
BPF_HASH(cpu_usage, u32, u64);
BPF_HASH(mem_usage, u32, long);

int kprobe__finish_task_switch(struct pt_regs *ctx){
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 *val;
	u64 zero = 0;

	u64 start_time = bpf_ktime_get_ns();
	val = start_times.lookup(&pid);
	if (val) {
		u64 delta = bpf_ktime_get_ns() - *val;

		u64 *cpu_time = cpu_usage.lookup_or_init(&pid, &zero);
		*cpu_time += delta;
	}
	start_times.update(&pid, &start_time);

	// struct task_struct *task = (struct task_struct *)bpf_get_current_task();
	// long rss = get_mm_rss(task->mm);
	// mem_usage.update(&pid, &rss);

	return 0;
}



