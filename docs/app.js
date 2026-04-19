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

function renderLeadAutomationDemo(data) {
  const summaryHost = document.getElementById("lead-metrics");
  const rankingHost = document.getElementById("lead-ranking-body");
  const highHost = document.getElementById("lead-sequence-high");
  const mediumHost = document.getElementById("lead-sequence-medium");
  const lowHost = document.getElementById("lead-sequence-low");

  summaryHost.innerHTML = [
    createMetricCard("Markets", data.leadAutomation.summary.markets, "Target commercial zones"),
    createMetricCard("Opportunity Pool", `${data.leadAutomation.summary.opportunity_pool_k}k`, "Estimated pipeline value"),
    createMetricCard("High-Priority Leads", data.leadAutomation.summary.high_priority_count, "Immediate outreach candidates"),
    createMetricCard("Workflow Nodes", data.leadAutomation.summary.workflow_nodes, "n8n-style orchestration steps"),
  ].join("");

  rankingHost.innerHTML = data.leadAutomation.ranked_leads
    .map(
      (lead) => `
        <tr>
          <td>${lead.company}</td>
          <td>${lead.market}</td>
          <td>${lead.score}</td>
          <td>${lead.priority}</td>
          <td>${lead.offer_angle}</td>
          <td>${lead.owner}</td>
          <td>${lead.next_step}</td>
        </tr>
      `
    )
    .join("");

  highHost.innerHTML = data.leadAutomation.sequence.high.map((item) => `<li>${item}</li>`).join("");
  mediumHost.innerHTML = data.leadAutomation.sequence.medium.map((item) => `<li>${item}</li>`).join("");
  lowHost.innerHTML = data.leadAutomation.sequence.low.map((item) => `<li>${item}</li>`).join("");
}

function renderSqlCopilotDemo(data) {
  const summaryHost = document.getElementById("sql-metrics");
  const routeHost = document.getElementById("sql-route-body");
  const queueHost = document.getElementById("sql-queue-body");
  const agendaHost = document.getElementById("sql-agenda");

  summaryHost.innerHTML = [
    createMetricCard("Revenue Under Watch", `${data.sqlCopilot.summary.revenue_under_watch_k}k`, "Accounts needing review"),
    createMetricCard("Segment To Protect", data.sqlCopilot.summary.segment_to_protect, `${data.sqlCopilot.summary.segment_revenue_k}k revenue`),
    createMetricCard("Avg Open Tickets", data.sqlCopilot.summary.segment_avg_open_tickets, "In the most exposed segment"),
    createMetricCard("Expansion Pipeline", `${data.sqlCopilot.summary.expansion_pipeline_k}k`, "Priority growth portfolio"),
  ].join("");

  routeHost.innerHTML = data.sqlCopilot.routes
    .map(
      (route) => `
        <tr>
          <td>${route.intent}</td>
          <td>${route.decision_owner}</td>
          <td>${route.priority}</td>
          <td>${route.row_count}</td>
          <td>${route.top_signal}</td>
          <td>${route.next_step}</td>
        </tr>
      `
    )
    .join("");

  queueHost.innerHTML = data.sqlCopilot.action_queue
    .map(
      (item) => `
        <tr>
          <td>${item.entity_name}</td>
          <td>${item.market}</td>
          <td>${item.workstream}</td>
          <td>${item.priority}</td>
          <td>${item.decision_owner}</td>
          <td>${item.business_case}</td>
        </tr>
      `
    )
    .join("");

  agendaHost.innerHTML = data.sqlCopilot.agenda.map((item) => `<li>${item}</li>`).join("");
}

loadSnapshot().then((data) => {
  const page = document.body.dataset.page;
  if (page === "home") {
    renderHome(data);
  }
  if (page === "kpi-demo") {
    renderKpiDemo(data);
  }
  if (page === "lead-demo") {
    renderLeadAutomationDemo(data);
  }
  if (page === "sql-demo") {
    renderSqlCopilotDemo(data);
  }
});
