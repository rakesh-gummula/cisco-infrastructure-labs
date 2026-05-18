/**
 * NetVigil-C: High-Performance Raw Socket Packet Sniffer
 * Captures Layer 2 Ethernet frames and decapsulates L3/L4 protocols.
 * Supports exporting directly to standard .pcap format.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <getopt.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/if_ether.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 65536

/* Global state for clean exit */
int keep_running = 1;
FILE *pcap_file = NULL;
int total_packets = 0;

/* PCAP Global Header */
typedef struct pcap_hdr_s {
    uint32_t magic_number;   /* magic number */
    uint16_t version_major;  /* major version number */
    uint16_t version_minor;  /* minor version number */
    int32_t  thiszone;       /* GMT to local correction */
    uint32_t sigfigs;        /* accuracy of timestamps */
    uint32_t snaplen;        /* max length of captured packets, in octets */
    uint32_t network;        /* data link type (1 = Ethernet) */
} pcap_hdr_t;

/* PCAP Packet Header */
typedef struct pcaprec_hdr_s {
    uint32_t ts_sec;         /* timestamp seconds */
    uint32_t ts_usec;        /* timestamp microseconds */
    uint32_t incl_len;       /* number of octets of packet saved in file */
    uint32_t orig_len;       /* actual length of packet */
} pcaprec_hdr_t;

/* Signal handler to catch Ctrl+C */
void handle_sigint(int sig) {
    printf("\n[!] Stopping NetVigil capture. Total packets captured: %d\n", total_packets);
    keep_running = 0;
}

/* Initialize PCAP file with global header */
void init_pcap(const char *filename) {
    pcap_file = fopen(filename, "wb");
    if (pcap_file == NULL) {
        perror("Failed to open PCAP file");
        exit(1);
    }
    pcap_hdr_t pcap_hdr = {
        .magic_number = 0xa1b2c3d4,
        .version_major = 2,
        .version_minor = 4,
        .thiszone = 0,
        .sigfigs = 0,
        .snaplen = 65535,
        .network = 1 // LINKTYPE_ETHERNET
    };
    fwrite(&pcap_hdr, sizeof(pcap_hdr_t), 1, pcap_file);
    printf("[*] PCAP logging enabled: %s\n", filename);
}

/* Write packet to PCAP file */
void write_pcap_packet(unsigned char *buffer, int size) {
    if (!pcap_file) return;

    struct timeval tv;
    gettimeofday(&tv, NULL);

    pcaprec_hdr_t rec_hdr = {
        .ts_sec = tv.tv_sec,
        .ts_usec = tv.tv_usec,
        .incl_len = size,
        .orig_len = size
    };
    fwrite(&rec_hdr, sizeof(pcaprec_hdr_t), 1, pcap_file);
    fwrite(buffer, size, 1, pcap_file);
    fflush(pcap_file);
}

/* Print standard MAC address format */
void print_mac(unsigned char* mac) {
    printf("%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

/* Process and parse the captured frame */
void process_packet(unsigned char* buffer, int size, int verbose) {
    write_pcap_packet(buffer, size);
    total_packets++;

    if (!verbose) {
        printf("\rPackets Captured: %d", total_packets);
        fflush(stdout);
        return;
    }

    struct ethhdr *eth = (struct ethhdr *)buffer;
    printf("\n\n=== Packet %d | Size: %d bytes ===", total_packets, size);
    
    // Layer 2: Ethernet
    printf("\n[Layer 2 - Ethernet]");
    printf("\n   |-Destination MAC : "); print_mac(eth->h_dest);
    printf("\n   |-Source MAC      : "); print_mac(eth->h_source);
    printf("\n   |-Protocol        : 0x%04x", ntohs(eth->h_proto));

    // Proceed only if it's an IPv4 packet (0x0800)
    if (ntohs(eth->h_proto) == ETH_P_IP) {
        struct iphdr *iph = (struct iphdr*)(buffer + sizeof(struct ethhdr));
        struct sockaddr_in source, dest;
        source.sin_addr.s_addr = iph->saddr;
        dest.sin_addr.s_addr = iph->daddr;

        unsigned short iphdrlen = iph->ihl * 4;

        // Layer 3: IP
        printf("\n[Layer 3 - IPv4]");
        printf("\n   |-Source IP       : %s", inet_ntoa(source.sin_addr));
        printf("\n   |-Destination IP  : %s", inet_ntoa(dest.sin_addr));
        printf("\n   |-TTL             : %d", (unsigned int)iph->ttl);

        // Layer 4: Transport
        printf("\n[Layer 4 - Transport]");
        switch (iph->protocol) {
            case 1: // ICMP
                printf("\n   |-Protocol        : ICMP");
                break;
            case 6: // TCP
            {
                struct tcphdr *tcph = (struct tcphdr*)(buffer + sizeof(struct ethhdr) + iphdrlen);
                printf("\n   |-Protocol        : TCP");
                printf("\n   |-Source Port     : %u", ntohs(tcph->source));
                printf("\n   |-Dest Port       : %u", ntohs(tcph->dest));
                break;
            }
            case 17: // UDP
            {
                struct udphdr *udph = (struct udphdr*)(buffer + sizeof(struct ethhdr) + iphdrlen);
                printf("\n   |-Protocol        : UDP");
                printf("\n   |-Source Port     : %u", ntohs(udph->source));
                printf("\n   |-Dest Port       : %u", ntohs(udph->dest));
                break;
            }
            default:
                printf("\n   |-Protocol        : Unknown (%d)", iph->protocol);
                break;
        }
    }
}

void print_help(char *prog_name) {
    printf("Usage: %s [OPTIONS]\n", prog_name);
    printf("Options:\n");
    printf("  -i <interface>   Bind to a specific interface (e.g., eth0, wlan0)\n");
    printf("  -w <file.pcap>   Write captured packets to a PCAP file\n");
    printf("  -v               Verbose mode (print header breakdowns to console)\n");
    printf("  -h               Print this help menu\n");
}

int main(int argc, char *argv[]) {
    int raw_sock;
    unsigned char *buffer = (unsigned char *)malloc(BUFFER_SIZE);
    
    char *interface = NULL;
    char *pcap_filename = NULL;
    int verbose = 0;
    int opt;

    // Parse command line arguments
    while ((opt = getopt(argc, argv, "i:w:vh")) != -1) {
        switch (opt) {
            case 'i': interface = optarg; break;
            case 'w': pcap_filename = optarg; break;
            case 'v': verbose = 1; break;
            case 'h': print_help(argv[0]); exit(0);
            default: print_help(argv[0]); exit(1);
        }
    }

    printf("Starting NetVigil Sniffer Daemon...\n");

    // Catch Ctrl+C for clean exit
    signal(SIGINT, handle_sigint);

    if (pcap_filename) {
        init_pcap(pcap_filename);
    }

    // Create raw socket bypassing the transport layer (Layer 2 capture)
    raw_sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (raw_sock < 0) {
        perror("Socket Error (Are you running as root/sudo?)");
        return 1;
    }

    // Bind to specific interface if provided
    if (interface != NULL) {
        struct ifreq ifr;
        memset(&ifr, 0, sizeof(ifr));
        strncpy(ifr.ifr_name, interface, IFNAMSIZ - 1);
        if (setsockopt(raw_sock, SOL_SOCKET, SO_BINDTODEVICE, (void *)&ifr, sizeof(ifr)) < 0) {
            perror("Failed to bind to interface");
            close(raw_sock);
            return 1;
        }
        printf("[*] Bound to interface: %s\n", interface);
    } else {
        printf("[*] Listening on all interfaces.\n");
    }

    printf("[*] Capture started. Press Ctrl+C to stop.\n\n");

    // Capture loop
    while (keep_running) {
        int data_size = recvfrom(raw_sock, buffer, BUFFER_SIZE, 0, NULL, NULL);
        if (data_size < 0 && keep_running) {
            perror("Recvfrom error");
            break;
        } else if (data_size > 0) {
            process_packet(buffer, data_size, verbose);
        }
    }

    // Cleanup
    if (pcap_file) fclose(pcap_file);
    close(raw_sock);
    free(buffer);
    printf("\nNetVigil terminated safely.\n");
    
    return 0;
}
