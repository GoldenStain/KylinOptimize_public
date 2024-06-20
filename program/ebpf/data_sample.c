#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <net/sock.h>
#include <linux/blkdev.h>
#include <bcc/proto.h>

// TCP IO量
BPF_HASH(sent_bytes, u32, u64);
BPF_HASH(recv_bytes, u32, u64);
BPF_HASH(sent_count, u32, u64);
BPF_HASH(recv_count, u32, u64);

int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 *val, zero = 0;
	val = sent_bytes.lookup_or_try_init(&pid, &zero);
	if (val){
		(*val) += size;
	}
	val = sent_count.lookup_or_try_init(&pid, &zero);
	if (val){
		(*val)++;
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
	val = recv_count.lookup_or_try_init(&pid, &zero);
	if (val){
		(*val)++;
	}
	return 0;
}

// 磁盘读写
BPF_HASH(disk_read_bytes, u32, u64);
BPF_HASH(disk_write_bytes, u32, u64);
BPF_HASH(disk_read_count, u32, u64);
BPF_HASH(disk_write_count, u32, u64);

// IO等待时间
BPF_HASH(disk_read_wait, u32, u64);
BPF_HASH(disk_write_wait, u32, u64);

int trace_block_rq_insert(struct pt_regs *ctx, struct request *req){
	u32 pid = bpf_get_current_pid_tgid() >> 32;
	u64 zero = 0;
	if (req->cmd_flags & REQ_OP_READ){
		// ...
	} else if (req->cmd_flags & REQ_OP_WRITE){
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

	if (req->cmd_flags & REQ_OP_READ){
		u64 *time = disk_read_wait.lookup_or_init(&pid, &zero);
		(*time) += bpf_ktime_get_ns() - req->start_time_ns;
	} else if (req->cmd_flags & REQ_OP_WRITE){
		u64 *time = disk_write_wait.lookup_or_init(&pid, &zero);
		(*time) += bpf_ktime_get_ns() - req->start_time_ns;
	}

	return 0;
}

// CPU、内存使用
BPF_HASH(start_times, u32, u64);
BPF_HASH(cpu_usage, u32, u64);
BPF_HASH(mem_usage, u32, u64);

BPF_HASH(task_nvcsw, u32, u64);
BPF_HASH(task_nivcsw, u32, u64);

int kprobe__finish_task_switch(struct pt_regs *ctx, struct task_struct *prev, struct task_struct *next){
	u32 prev_pid = prev->pid;
	u32 next_pid = next->pid;
	u64 *val;
	u64 zero = 0;

	u64 start_time = bpf_ktime_get_ns();
	val = start_times.lookup(&prev_pid);
	if (val) {
		u64 delta = bpf_ktime_get_ns() - *val;
		*(cpu_usage.lookup_or_init(&prev_pid, &zero)) += delta;
	}
	start_times.update(&next_pid, &start_time);

	*(task_nvcsw.lookup_or_init(&prev_pid, &zero)) += prev->nvcsw;
	*(task_nivcsw.lookup_or_init(&prev_pid, &zero)) += prev->nivcsw;

	u64 total_vm = prev->mm->total_vm;
	mem_usage.update(&prev_pid, &total_vm);

	return 0;
}


