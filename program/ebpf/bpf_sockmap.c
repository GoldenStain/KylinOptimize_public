#include "vmlinux.h"
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>

#define LOCALHOST_IPV4 0x0100007F

struct sock_key {
    __u32 sip;
    __u32 dip;
    __u32 sport;
    __u32 dport;
    __u32 family;
};

struct {
	 __uint(type, BPF_MAP_TYPE_SOCKHASH);
	 __uint(max_entries, 65535);
	 __type(key, struct sock_key);
	 __type(value, int);
} sock_ops_map SEC(".maps");

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("sk_msg")
int bpf_redir(struct sk_msg_md *msg){
    if(msg->remote_ip4 != LOCALHOST_IPV4 || msg->local_ip4!= LOCALHOST_IPV4) 
        return SK_PASS;

    struct sock_key key = {
        .sip = msg->remote_ip4,
        .dip = msg->local_ip4,
        .dport = bpf_htonl(msg->local_port), /* convert to network byte order */
        .sport = msg->remote_port,
        .family = msg->family,
    };
    return bpf_msg_redirect_hash(msg, &sock_ops_map, &key, BPF_F_INGRESS);
}

SEC("sockops")
int bpf_sockops_handler(struct bpf_sock_ops *skops){
    u32 family, op;

	 family = skops->family;
	 op = skops->op;
	 if (op != BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB
		    && op != BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB) {
		    return BPF_OK;
		}

		if(skops->remote_ip4 != LOCALHOST_IPV4 || skops->local_ip4!= LOCALHOST_IPV4) {
		    return BPF_OK;
		}

	 struct sock_key key = {
		    .dip = skops->remote_ip4,
		    .sip = skops->local_ip4,
		    .sport = bpf_htonl(skops->local_port),  /* convert to network byte order */
		    .dport = skops->remote_port,
		    .family = skops->family,
		};

	 bpf_printk(">>> new connection: OP:%d, PORT:%d --> %d\n", op, bpf_ntohl(key.sport), bpf_ntohl(key.dport));

	 bpf_sock_hash_update(skops, &sock_ops_map, &key, BPF_NOEXIST);
	 return BPF_OK;
}

