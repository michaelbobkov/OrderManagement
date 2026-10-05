"""Generate Grafana dashboard JSON (kept as code so panels stay consistent)."""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "monitoring/grafana/dashboards"
DS = {"type": "prometheus", "uid": "prometheus"}


def panel(pid, title, exprs, x, y, unit="short", kind="timeseries", w=12, h=8):
    return {
        "id": pid, "title": title, "type": kind, "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "fieldConfig": {"defaults": {"unit": unit}, "overrides": []},
        "targets": [{"refId": chr(65 + i), "expr": e, "legendFormat": legend,
                     "datasource": DS} for i, (e, legend) in enumerate(exprs)],
    }


def dash(uid, title, panels):
    return {"uid": uid, "title": title, "schemaVersion": 39, "version": 1,
            "refresh": "10s", "time": {"from": "now-30m", "to": "now"},
            "tags": ["order-platform"], "panels": panels}


java_req = 'http_server_requests_seconds_count'
golden = dash("golden-signals", "Golden Signals", [
    panel(1, "Traffic - requests/s", [
        (f'sum(rate({java_req}[1m]))', "order-service"),
        ('sum(rate(http_requests_total[1m]))', "notification-service")], 0, 0, "reqps"),
    panel(2, "Errors - 5xx ratio", [
        (f'sum(rate({java_req}{{status=~"5.."}}[5m])) / sum(rate({java_req}[5m]))',
         "order-service"),
        ('sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m]))',
         "notification-service")], 12, 0, "percentunit"),
    panel(3, "Latency - p95", [
        ('histogram_quantile(0.95, sum by (le) '
         '(rate(http_server_requests_seconds_bucket[5m])))', "order-service"),
        ('histogram_quantile(0.95, sum by (le) '
         '(rate(http_request_duration_seconds_bucket[5m])))', "notification-service")],
        0, 8, "s"),
    panel(4, "Saturation - CPU %", [
        ('100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100',
         "{{instance}}")], 12, 8, "percent"),
    panel(5, "Service up", [('up', "{{job}}")], 0, 16, "short", "stat", 24, 4),
])
business = dash("business-kpis", "Business KPIs", [
    panel(1, "Orders created / min", [
        ('sum(rate(orders_created_total[5m])) * 60', "orders/min")], 0, 0, "short"),
    panel(2, "Average order value", [
        ('rate(order_value_sum[5m]) / rate(order_value_count[5m])', "avg value")],
        12, 0, "currencyUSD"),
    panel(3, "Revenue / min", [
        ('sum(rate(order_value_sum[5m])) * 60', "revenue/min")], 0, 8, "currencyUSD"),
    panel(4, "Notifications processed / min", [
        ('sum by (type) (rate(notifications_processed_total[5m])) * 60', "{{type}}")],
        12, 8, "short"),
    panel(5, "Total orders", [('sum(orders_created_total)', "total")], 0, 16, "short",
          "stat", 24, 4),
])
for d in (golden, business):
    (OUT / f"{d['uid']}.json").write_text(json.dumps(d, indent=2) + "\n")
