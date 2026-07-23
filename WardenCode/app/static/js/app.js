(function () {
  const providerSelect = document.getElementById("provider");
  const modelRow = document.getElementById("model-row");
  const keyRow = document.getElementById("key-row");
  const modelInput = document.getElementById("model");
  const apiKeyInput = document.getElementById("api-key");
  const delayInput = document.getElementById("delay");
  const runBtn = document.getElementById("run-btn");
  const configError = document.getElementById("config-error");

  const configPanel = document.getElementById("config-panel");
  const runPanel = document.getElementById("run-panel");
  const progressFill = document.getElementById("progress-fill");
  const progressLabel = document.getElementById("progress-label");
  const resultFeed = document.getElementById("result-feed");
  const statPass = document.getElementById("stat-pass");
  const statFail = document.getElementById("stat-fail");
  const statReview = document.getElementById("stat-review");
  const reportBtn = document.getElementById("report-btn");
  const newRunBtn = document.getElementById("new-run-btn");

  let pollTimer = null;
  let renderedCount = 0;
  let currentRunId = null;

  function updateProviderFields() {
    const isMock = providerSelect.value === "mock";
    modelRow.hidden = isMock;
    keyRow.hidden = isMock;
  }
  providerSelect.addEventListener("change", updateProviderFields);
  updateProviderFields();

  function selectedCategories() {
    return Array.from(document.querySelectorAll('input[name="category"]:checked')).map(
      (el) => el.value
    );
  }

  function resetRunUI() {
    renderedCount = 0;
    resultFeed.innerHTML = "";
    progressFill.style.width = "0%";
    progressLabel.textContent = "0 / 0";
    statPass.textContent = "0";
    statFail.textContent = "0";
    statReview.textContent = "0";
    reportBtn.hidden = true;
    newRunBtn.hidden = true;
  }

  function renderResult(r) {
    const li = document.createElement("li");
    li.className = "result-item";
    li.dataset.passed = String(r.passed);
    li.dataset.confidence = r.confidence;

    const badge = document.createElement("span");
    badge.className = "result-badge";
    badge.textContent = r.passed ? "PASS" : "FAIL";

    const owasp = document.createElement("span");
    owasp.className = "result-owasp";
    owasp.textContent = r.owasp_id;

    const name = document.createElement("span");
    name.className = "result-name";
    name.textContent = r.name.replace(/_/g, " ");

    const note = document.createElement("span");
    note.className = "result-note";
    note.textContent = r.confidence === "low" ? "read raw response before trusting this" : "";

    li.append(badge, owasp, name, note);
    resultFeed.appendChild(li);
    resultFeed.scrollTop = resultFeed.scrollHeight;
  }

  function updateStats(results) {
    let pass = 0, fail = 0, review = 0;
    for (const r of results) {
      if (r.passed) pass++; else fail++;
      if (r.confidence === "low") review++;
    }
    statPass.textContent = pass;
    statFail.textContent = fail;
    statReview.textContent = review;
  }

  async function poll() {
    if (!currentRunId) return;
    let res;
    try {
      res = await fetch(`/api/status/${currentRunId}`);
    } catch (e) {
      configError.textContent = "Lost connection to the local Warden server.";
      return;
    }
    if (!res.ok) return;
    const state = await res.json();

    progressLabel.textContent = `${state.completed} / ${state.total}`;
    progressFill.style.width = state.total
      ? `${(state.completed / state.total) * 100}%`
      : "0%";

    for (; renderedCount < state.results.length; renderedCount++) {
      renderResult(state.results[renderedCount]);
    }
    updateStats(state.results);

    if (state.status === "complete") {
      clearInterval(pollTimer);
      reportBtn.hidden = false;
      newRunBtn.hidden = false;
      runBtn.disabled = false;
    } else if (state.status === "error") {
      clearInterval(pollTimer);
      configError.textContent = `Run failed: ${state.error}`;
      newRunBtn.hidden = false;
      runBtn.disabled = false;
    }
  }

  async function startRun() {
    configError.textContent = "";
    const provider = providerSelect.value;

    if (provider !== "mock" && !apiKeyInput.value.trim()) {
      configError.textContent = "An API key is required for this provider.";
      return;
    }
    const categories = selectedCategories();
    if (categories.length === 0) {
      configError.textContent = "Select at least one category to run.";
      return;
    }

    runBtn.disabled = true;
    resetRunUI();
    runPanel.hidden = false;
    runPanel.scrollIntoView({ behavior: "smooth", block: "start" });

    const body = {
      provider,
      model: modelInput.value.trim() || undefined,
      api_key: apiKeyInput.value.trim() || undefined,
      delay: parseFloat(delayInput.value) || 0,
      categories,
    };

    await launch(body);
  }

  async function launch(body) {
    let res;
    try {
      res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (e) {
      configError.textContent = "Could not reach the local Warden server.";
      runBtn.disabled = false;
      return;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      configError.textContent = err.error || "Could not start the run.";
      runBtn.disabled = false;
      return;
    }
    const data = await res.json();
    currentRunId = data.run_id;
    pollTimer = setInterval(poll, 600);
    poll();
  }

  runBtn.addEventListener("click", startRun);

  reportBtn.addEventListener("click", () => {
    if (currentRunId) window.location.href = `/api/report/${currentRunId}`;
  });

  newRunBtn.addEventListener("click", () => {
    currentRunId = null;
    runPanel.hidden = true;
    configPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  });
})();
