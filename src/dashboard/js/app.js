/**
 * AI-Driven CI/CD Pipeline Optimization - Frontend Dashboard Logic
 * Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
 */

const API_BASE = window.location.origin;

// State management
let overviewChartInstance = null;
let modelChartInstance = null;
let expChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initPredictorForm();
    initPipelineRunner();
    loadAllDashboardData();

    // Auto-refresh every 20 seconds
    setInterval(loadAllDashboardData, 20000);
});

function initTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

            tab.classList.add("active");
            const target = document.getElementById(tab.dataset.tab);
            if (target) target.classList.add("active");

            // Re-render charts on tab switch if needed
            if (tab.dataset.tab === "models") renderModelCharts();
            if (tab.dataset.tab === "experiments") loadExperimentBenchmarks();
        });
    });
}

async function loadAllDashboardData() {
    await checkHealth();
    await loadKPIs();
    await loadBuildHistory();
    await loadASTOverview();
    await loadExperimentBenchmarks();
}

async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        const badge = document.getElementById("health-badge");
        if (data.status === "healthy") {
            badge.className = "badge badge-success";
            badge.innerText = "● System Healthy (Models & DB Active)";
        } else {
            badge.className = "badge badge-warning";
            badge.innerText = "● System Degraded";
        }
    } catch (e) {
        const badge = document.getElementById("health-badge");
        badge.className = "badge badge-danger";
        badge.innerText = "● Backend Disconnected";
    }
}

async function loadKPIs() {
    try {
        const res = await fetch(`${API_BASE}/api/overview`);
        const kpis = await res.json();

        document.getElementById("kpi-total-builds").innerText = kpis.total_builds || 0;
        document.getElementById("kpi-success-rate").innerText = `${kpis.success_rate_pct || 0}%`;
        document.getElementById("kpi-runtime-savings").innerText = `${kpis.runtime_reduction_pct || 0}%`;
        document.getElementById("kpi-test-reduction").innerText = `${kpis.test_reduction_pct || 0}%`;
        document.getElementById("kpi-avg-runtime").innerText = `${kpis.optimized_avg_runtime_sec || kpis.baseline_avg_runtime_sec || 0}s`;
        document.getElementById("kpi-avg-cpu").innerText = `${kpis.optimized_avg_cpu || kpis.baseline_avg_cpu || 0}%`;
    } catch (e) {
        console.error("Error loading KPIs:", e);
    }
}

async function loadBuildHistory() {
    try {
        const res = await fetch(`${API_BASE}/api/telemetry/history?limit=15`);
        const history = await res.json();
        const tbody = document.getElementById("history-table-body");
        tbody.innerHTML = "";

        if (!history || history.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No pipeline execution records yet. Run a pipeline from the Runner tab.</td></tr>`;
            return;
        }

        history.forEach(b => {
            const tr = document.createElement("tr");
            const statusBadge = b.status === "SUCCESS"
                ? `<span class="badge badge-success">SUCCESS</span>`
                : `<span class="badge badge-danger">FAILED</span>`;

            const stratBadge = b.execution_strategy === "FULL_TEST_SUITE"
                ? `<span class="badge badge-danger">FULL SUITE</span>`
                : `<span class="badge badge-success">TARGETED</span>`;

            const modeBadge = b.execution_mode === "BASELINE"
                ? `<span class="badge badge-primary">BASELINE</span>`
                : `<span class="badge badge-warning">AI OPT</span>`;

            const riskText = b.failure_probability !== null && b.failure_probability !== undefined
                ? `${(b.failure_probability * 100).toFixed(1)}%`
                : "N/A";

            tr.innerHTML = `
                <td><strong>${b.build_id}</strong></td>
                <td>${modeBadge}</td>
                <td>${stratBadge}</td>
                <td>${statusBadge}</td>
                <td>${riskText}</td>
                <td>${b.actual_runtime.toFixed(2)}s</td>
                <td>${b.tests_passed} / ${b.test_count}</td>
                <td style="font-size: 0.75rem; color: var(--text-secondary);">${b.timestamp.split("T")[1].split(".")[0]}</td>
            `;
            tbody.appendChild(tr);
        });

        renderOverviewChart(history);
    } catch (e) {
        console.error("Error loading build history:", e);
    }
}

function renderOverviewChart(history) {
    if (!history || history.length === 0) return;
    const ctx = document.getElementById("overviewRuntimeChart");
    if (!ctx) return;

    const reversed = [...history].reverse();
    const labels = reversed.map(b => b.build_id.split("-")[1].slice(-4));
    const runtimes = reversed.map(b => b.actual_runtime);
    const predictedRuntimes = reversed.map(b => b.predicted_runtime || b.actual_runtime);

    if (overviewChartInstance) overviewChartInstance.destroy();

    overviewChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Actual Pipeline Runtime (s)",
                    data: runtimes,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59, 130, 246, 0.15)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                },
                {
                    label: "AI Predicted Runtime (s)",
                    data: predictedRuntimes,
                    borderColor: "#10b981",
                    borderDash: [5, 5],
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: "#94a3b8" } }
            },
            scales: {
                x: { grid: { color: "#334155" }, ticks: { color: "#94a3b8" } },
                y: { grid: { color: "#334155" }, ticks: { color: "#94a3b8" }, title: { display: true, text: "Seconds", color: "#94a3b8" } }
            }
        }
    });
}

function initPredictorForm() {
    const form = document.getElementById("prediction-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const features = {
            files_changed: parseInt(document.getElementById("p-files").value),
            lines_added: parseInt(document.getElementById("p-added").value),
            lines_deleted: parseInt(document.getElementById("p-deleted").value),
            test_count: parseInt(document.getElementById("p-tests").value),
            prev_runtime: parseFloat(document.getElementById("p-prev-runtime").value),
            prev_failure: parseInt(document.getElementById("p-prev-fail").value),
            cpu_usage: parseFloat(document.getElementById("p-cpu").value),
            memory_usage: parseFloat(document.getElementById("p-mem").value),
        };

        const changedFile = document.getElementById("p-file-name").value;

        try {
            // Call Decision Engine
            const res = await fetch(`${API_BASE}/api/decision`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    changed_files: [changedFile],
                    features: features,
                }),
            });
            const data = await res.json();

            // Render prediction card
            const resultBox = document.getElementById("prediction-result-box");
            resultBox.style.display = "block";

            document.getElementById("res-prob").innerText = `${(data.failure_probability * 100).toFixed(1)}%`;
            document.getElementById("res-conf").innerText = `${(data.model_confidence * 100).toFixed(1)}%`;
            document.getElementById("res-pred-time").innerText = `${data.predicted_runtime.toFixed(1)}s`;
            document.getElementById("res-strategy").innerText = data.execution_strategy;
            document.getElementById("res-strategy").className = data.execution_strategy === "FULL_TEST_SUITE" ? "badge badge-danger" : "badge badge-success";
            document.getElementById("res-explanation").innerText = data.decision_explanation;

            const testList = document.getElementById("res-tests-list");
            testList.innerHTML = "";
            data.selected_tests.forEach(t => {
                const li = document.createElement("li");
                li.innerText = t;
                testList.appendChild(li);
            });
        } catch (err) {
            alert(`Inference failed: ${err.message}`);
        }
    });
}

async function loadASTOverview() {
    try {
        const res = await fetch(`${API_BASE}/api/analyze/ast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ app_dir: "sample_app", tests_dir: "sample_tests" }),
        });
        const astData = await res.json();
        const treeBox = document.getElementById("ast-tree-box");
        if (!treeBox) return;

        let html = "<h4>AST Direct & Transitive Dependency Graph</h4><ul>";
        for (const [mod, tests] of Object.entries(astData.module_to_tests)) {
            html += `<li><strong>sample_app/${mod}.py</strong> ➔ <span>${tests.length} tests mapped: [${tests.join(", ")}]</span></li>`;
        }
        html += "</ul>";
        treeBox.innerHTML = html;
    } catch (e) {
        console.error("Error loading AST:", e);
    }
}

function initPipelineRunner() {
    const runBtn = document.getElementById("run-pipeline-btn");
    if (!runBtn) return;

    runBtn.addEventListener("click", async () => {
        const mode = document.getElementById("runner-mode").value;
        const changedFile = document.getElementById("runner-file").value;
        const consoleBox = document.getElementById("runner-console");

        runBtn.disabled = true;
        runBtn.innerText = "⏳ Executing Pipeline...";
        consoleBox.innerText = `[*] Launching ${mode} pipeline...\n[*] Target Changed File: ${changedFile}\n[*] Awaiting test suite execution and telemetry capture...\n`;

        try {
            const payload = {
                execution_mode: mode,
                changed_files: [changedFile],
                branch: "main",
            };

            const res = await fetch(`${API_BASE}/api/pipeline/execute`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await res.json();

            consoleBox.innerText += `\n[+] Pipeline Completed: ${data.build_id}\n`;
            consoleBox.innerText += `    Execution Strategy : ${data.execution_strategy}\n`;
            consoleBox.innerText += `    Pipeline Outcome   : ${data.status}\n`;
            consoleBox.innerText += `    Actual Duration    : ${data.actual_runtime} seconds\n`;
            consoleBox.innerText += `    Executed Tests     : ${data.test_count} (${data.tests_passed} passed, ${data.tests_failed} failed)\n`;
            consoleBox.innerText += `    CPU Utilization    : ${data.cpu_usage}%\n`;
            consoleBox.innerText += `    Memory Allocation  : ${data.memory_usage} MB\n`;
            if (data.decision_explanation) {
                consoleBox.innerText += `    Decision Audit     : ${data.decision_explanation}\n`;
            }

            await loadKPIs();
            await loadBuildHistory();
        } catch (err) {
            consoleBox.innerText += `\n[!] Error during execution: ${err.message}`;
        } finally {
            runBtn.disabled = false;
            runBtn.innerText = "🚀 Run Pipeline";
        }
    });
}

async function renderModelCharts() {
    try {
        const res = await fetch(`${API_BASE}/api/models/metrics`);
        const metrics = await res.json();

        // Classification chart
        const ctxClf = document.getElementById("modelClfChart");
        if (ctxClf) {
            const clfLabels = Object.keys(metrics.classification_benchmarks);
            const recalls = clfLabels.map(k => metrics.classification_benchmarks[k].recall);
            const f1s = clfLabels.map(k => metrics.classification_benchmarks[k].f1_score);
            const rocs = clfLabels.map(k => metrics.classification_benchmarks[k].roc_auc);

            if (modelChartInstance) modelChartInstance.destroy();

            modelChartInstance = new Chart(ctxClf, {
                type: "bar",
                data: {
                    labels: clfLabels,
                    datasets: [
                        { label: "Recall (Failure Detection)", data: recalls, backgroundColor: "#ef4444" },
                        { label: "F1-Score", data: f1s, backgroundColor: "#3b82f6" },
                        { label: "ROC-AUC", data: rocs, backgroundColor: "#10b981" }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: "#94a3b8" } } },
                    scales: {
                        x: { ticks: { color: "#94a3b8" } },
                        y: { min: 0, max: 1.0, ticks: { color: "#94a3b8" } }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Error rendering model charts:", e);
    }
}

async function loadExperimentBenchmarks() {
    try {
        const res = await fetch(`${API_BASE}/api/experiments/comparison`);
        const experiments = await res.json();
        const tbody = document.getElementById("experiments-table-body");
        if (!tbody) return;
        tbody.innerHTML = "";

        if (!experiments || experiments.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No empirical experiments recorded yet. Run run_experiments.py to populate.</td></tr>`;
            return;
        }

        experiments.forEach(exp => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${exp.scenario_name}</strong></td>
                <td>${exp.baseline_runtime.toFixed(2)}s</td>
                <td>${exp.optimized_runtime.toFixed(2)}s</td>
                <td style="color: #34d399; font-weight: 700;">${exp.runtime_savings_pct.toFixed(1)}%</td>
                <td>${exp.baseline_tests_count} ➔ ${exp.optimized_tests_count}</td>
                <td style="color: #34d399; font-weight: 700;">${exp.test_reduction_pct.toFixed(1)}%</td>
                <td>${exp.baseline_defect_detected === exp.optimized_defect_detected ? '<span class="badge badge-success">100% Retained</span>' : '<span class="badge badge-danger">Mismatch</span>'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error loading experiments:", e);
    }
}
