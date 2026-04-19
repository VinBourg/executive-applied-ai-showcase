async function loadSnapshot() {
  const response = await fetch("data/showcase_snapshot.json");
  return response.json();
}

function createMetricCard(label, value, note) {
  return `
    <article class="metric-card">
      <div class="metric-label">${label}</div>
      <div class="metric-value">${value}</div>
      <div class="metric-label">${note}</div>
    </article>
  `;
}

function renderHome(data) {
  const metricHost = document.getElementById("home-metrics");
  const leadHost = document.getElementById("lead-table-body");
  const actionHost = document.getElementById("home-actions");
  metricHost.innerHTML = [
    createMetricCard("Operations Health", data.kpi.summary.operations_health_score, "KPI pipeline snapshot"),
    createMetricCard("SLA Compliance", `${data.kpi.summary.sla_compliance_rate}%`, "Latest static demo data"),
    createMetricCard("Opportunity Pool", `${data.leadAutomation.summary.opportunity_pool_k}k`, "Qualified lead universe"),
    createMetricCard("High-Priority Leads", data.leadAutomation.summary.high_priority_count, data.leadAutomation.summary.markets),
  ].join("");

  leadHost.innerHTML = data.leadAutomation.top_leads
    .map(
      (lead) => `
        <tr>
          <td>${lead.company}</td>
          <td>${lead.market}</td>
          <td>${lead.score}</td>
          <td>${lead.offer_angle}</td>
          <td>${lead.owner}</td>
        </tr>
      `
    )
    .join("");

  actionHost.innerHTML = data.kpi.actions.map((item) => `<li>${item}</li>`).join("");
}

function renderKpiDemo(data) {
  const summaryHost = document.getElementById("kpi-metrics");
  const categoryHost = document.getElementById("category-table-body");
  const alertHost = document.getElementById("alert-table-body");
  const actionHost = document.getElementById("kpi-actions");

  summaryHost.innerHTML = [
    createMetricCard("Tickets", data.kpi.summary.ticket_count, "Current sample period"),
    createMetricCard("Avg Resolution", `${data.kpi.summary.average_resolution_hours}h`, "Support ops average"),
    createMetricCard("SLA Compliance", `${data.kpi.summary.sla_compliance_rate}%`, "Across all tickets"),
    createMetricCard("Reopened Rate", `${data.kpi.summary.reopened_rate}%`, "Quality signal"),
    createMetricCard("Health Score", data.kpi.summary.operations_health_score, "Composite operating signal"),
    createMetricCard("Alerts", data.kpi.summary.alert_count, "Active issues to review"),
  ].join("");

  categoryHost.innerHTML = data.kpi.categories
    .map(
      (row) => `
        <tr>
          <td>${row.category}</td>
          <td>${row.ticket_count}</td>
          <td>${row.average_resolution_hours}h</td>
          <td>${row.sla_compliance_rate}%</td>
          <td class="${row.risk_level === "high" ? "risk-high" : "risk-low"}">${row.risk_level}</td>
        </tr>
      `
    )
    .join("");

  alertHost.innerHTML = data.kpi.alerts
    .map(
      (alert) => `
        <tr>
          <td class="${alert.severity === "high" ? "severity-high" : "severity-medium"}">${alert.severity}</td>
          <td>${alert.owner}</td>
          <td>${alert.signal}</td>
          <td>${alert.recommended_action}</td>
        </tr>
      `
    )
    .join("");

  actionHost.innerHTML = data.kpi.actions.map((item) => `<li>${item}</li>`).join("");
}

loadSnapshot().then((data) => {
  const page = document.body.dataset.page;
  if (page === "home") {
    renderHome(data);
  }
  if (page === "kpi-demo") {
    renderKpiDemo(data);
  }
});
