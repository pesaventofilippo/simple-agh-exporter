import prometheus_client as prom
from http.server import HTTPServer, BaseHTTPRequestHandler
from modules.utils import env
from modules.agh_client import AGHClient

PROFILER = prom.Summary('metrics_update_seconds', 'Time spent updating metrics', namespace=env.PROMETHEUS_PREFIX)
agh = AGHClient(
    server=env.ADGUARD_SERVER,
    username=env.ADGUARD_USERNAME,
    password=env.ADGUARD_PASSWORD
)

METRICS = {
    "dhcp": {
        "enabled": prom.Gauge("dhcp_enabled", "DHCP server status",
                              namespace=env.PROMETHEUS_PREFIX),
        "active_leases": prom.Gauge("dhcp_active_leases", "Number of active DHCP leases",
                                    namespace=env.PROMETHEUS_PREFIX),
        "static_leases": prom.Gauge("dhcp_static_leases", "Number of static DHCP leases",
                                    namespace=env.PROMETHEUS_PREFIX)
    },
    "filtering": {
        "enabled": prom.Gauge("filtering_enabled", "Filtering status",
                              namespace=env.PROMETHEUS_PREFIX),
        "active_lists": prom.Gauge("filtering_active_lists", "Number of active filtering lists",
                                   namespace=env.PROMETHEUS_PREFIX),
        "total_filters": prom.Gauge("filtering_total_filters", "Number of filtering rules",
                                    namespace=env.PROMETHEUS_PREFIX),
        "user_rules": prom.Gauge("filtering_user_rules", "Number of user-defined filtering rules",
                                 namespace=env.PROMETHEUS_PREFIX)
    },
    "status": {
        "running": prom.Gauge("status_running", "Server status",
                              namespace=env.PROMETHEUS_PREFIX),
        "protection_enabled": prom.Gauge("status_protection_enabled", "Protection status",
                                         namespace=env.PROMETHEUS_PREFIX)
    },
    "rewrite": {
        "rules": prom.Gauge("rewrite_rules", "Number of DNS rewrite rules",
                            namespace=env.PROMETHEUS_PREFIX)
    },
    "dns": {
        "num_queries": prom.Gauge("dns_num_queries", "Number of DNS queries",
                                  namespace=env.PROMETHEUS_PREFIX),
        "num_blocked": prom.Gauge("dns_num_blocked", "Number of blocked DNS queries",
                                  namespace=env.PROMETHEUS_PREFIX),
        "num_replaced": prom.Gauge("dns_num_replaced", "Number of replaced DNS queries",
                                   namespace=env.PROMETHEUS_PREFIX),
        "avg_processing_time": prom.Gauge("dns_avg_processing_time", "Average DNS query processing time",
                                          namespace=env.PROMETHEUS_PREFIX)
    },
    "stats": {
        "top_domains": prom.Gauge("stats_top_domains", "Top queried domains",
                                  ["domain"], namespace=env.PROMETHEUS_PREFIX),
        "top_clients": prom.Gauge("stats_top_clients", "Top DNS clients",
                                  ["ip", "name"], namespace=env.PROMETHEUS_PREFIX),
        "top_blocked_domains": prom.Gauge("stats_top_blocked_domains", "Top blocked domains",
                                          ["domain"], namespace=env.PROMETHEUS_PREFIX),
        "top_upstreams_responses": prom.Gauge("stats_top_upstreams_responses", "Top upstream responses",
                                              ["upstream"], namespace=env.PROMETHEUS_PREFIX),
        "top_upstreams_avg_time": prom.Gauge("stats_top_upstreams_avg_time", "Top upstream average response time",
                                             ["upstream"], namespace=env.PROMETHEUS_PREFIX)
    }
}


@PROFILER.time()
def update_metrics():
    dhcp = agh.dhcp_status()
    for key in dhcp:
        METRICS["dhcp"][key].set(dhcp[key])

    filtering = agh.filtering_status()
    for key in filtering:
        METRICS["filtering"][key].set(filtering[key])

    status = agh.status()
    for key in status:
        METRICS["status"][key].set(status[key])

    rewrite = agh.dns_rewrite()
    for key in rewrite:
        METRICS["rewrite"][key].set(rewrite[key])

    dns = agh.dns_queries()
    for key in dns:
        METRICS["dns"][key].set(dns[key])

    stats = agh.dns_topstats()
    for key in stats:
        if key == "top_clients":
            for client in stats[key]:
                METRICS["stats"][key].labels(ip=client["ip"], name=client["name"]).set(client["count"])

        else:
            for domain in stats[key]:
                METRICS["stats"][key].labels(domain).set(stats[key][domain])


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            update_metrics()

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(prom.generate_latest())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")


if __name__ == "__main__":
    prom.disable_created_metrics()
    prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
    prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
    prom.REGISTRY.unregister(prom.GC_COLLECTOR)

    server = HTTPServer(("0.0.0.0", env.PROMETHEUS_PORT), MetricsHandler)
    server.serve_forever()
