import time
import requests


class AGHClient:
    def __init__(self, server: str, username: str, password: str):
        self._server = server if server.startswith("http") else f"http://{server}"
        self._username = username
        self._password = password

        self._session = requests.Session()
        self._login()

    @staticmethod
    def _flatten_dictlist(data: list[dict]) -> dict:
        return {k: v for d in data for k, v in d.items()}

    def _login(self):
        self._session.post(
            f"{self._server}/control/login",
            json={"name": self._username, "password": self._password}
        )

    def _get(self, path: str, *, params: dict=None) -> dict:
        try:
            return self._session.get(
                f"{self._server}/control/{path.strip('/')}",
                params=params
            ).json()
        except Exception:
            time.sleep(0.5)
            self._login()
            return self._get(path, params=params)

    def _translate_clients(self, clients: dict) -> dict:
        ips = clients.keys()
        res = self._get("clients/find", params={
            f"ip{i}": ip for i, ip in enumerate(ips)
        })
        res = self._flatten_dictlist(res)
        translation = {ip: res[ip]['name'] for ip in ips}

        return [
            {
                "ip": ip,
                "name": translation[ip],
                "count": count
            }
            for ip, count in clients.items()
        ]

    def dhcp_status(self) -> dict[str, int]:
        res = self._get("dhcp/status")
        return {
            "enabled": int(res["enabled"]),
            "active_leases": len(res["leases"]),
            "static_leases": len(res["static_leases"])
        }

    def filtering_status(self) -> dict[str, int]:
        res = self._get("filtering/status")
        return {
            "enabled": int(res["enabled"]),
            "active_lists": sum(1 for f in res["filters"] if f["enabled"]),
            "total_filters": sum(f["rules_count"] for f in res["filters"] if f["enabled"]),
            "user_rules": len(res["user_rules"])
        }

    def status(self) -> dict[str, int]:
        res = self._get("status")
        return {
            "running": int(res["running"]),
            "protection_enabled": int(res["protection_enabled"])
        }

    def dns_rewrite(self) -> dict[str, int]:
        res = self._get("rewrite/list")
        return {
            "rules": len(res)
        }

    def dns_topstats(self) -> dict[str, dict]:
        res = self._get("stats")
        top_clients = self._flatten_dictlist(res["top_clients"])
        return {
            "top_domains": self._flatten_dictlist(res["top_queried_domains"]),
            "top_clients": self._translate_clients(top_clients),
            "top_blocked_domains": self._flatten_dictlist(res["top_blocked_domains"]),
            "top_upstreams_responses": self._flatten_dictlist(res["top_upstreams_responses"]),
            "top_upstreams_avg_time": self._flatten_dictlist(res["top_upstreams_avg_time"]),
        }

    def dns_queries(self) -> dict[str, int]:
        res = self._get("stats")
        return {
            "num_queries": res["num_dns_queries"],
            "num_blocked": res["num_blocked_filtering"],
            "num_replaced": res["num_replaced_safebrowsing"] +
                            res["num_replaced_safesearch"] +
                            res["num_replaced_parental"],
            "avg_processing_time": res["avg_processing_time"]
        }
