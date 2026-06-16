const API_BASE = "/api";

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

async function apiPost(path, body) {
  console.log("POST", path, JSON.stringify(body));
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    const msg = typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail.map((e) => e.msg || JSON.stringify(e)).join("; ")
        : res.statusText;
    throw new Error(msg);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

async function fetchHealth() {
  return apiGet("/health");
}

async function fetchProviders() {
  return apiGet("/providers");
}

async function fetchProviderModels(name) {
  return apiGet(`/providers/${name}/models`);
}

async function fetchBuildProfiles() {
  return apiGet("/build-profiles");
}

async function createPipeline(data) {
  return apiPost("/pipelines", data);
}

async function fetchPipelines(limit = 100, offset = 0) {
  return apiGet(`/pipelines?limit=${limit}&offset=${offset}`);
}

async function fetchCurrentPipeline() {
  return apiGet("/pipelines/current");
}

async function fetchPipeline(id) {
  return apiGet(`/pipelines/${id}`);
}

async function approveCheckpoint(id) {
  return apiPost(`/pipelines/${id}/approve`, {});
}

async function submitFeedback(id, feedback) {
  return apiPost(`/pipelines/${id}/feedback`, { feedback });
}

async function retryAgent(id, agent) {
  return apiPost(`/pipelines/${id}/retry`, { agent });
}

async function deletePipeline(id) {
  return apiDelete(`/pipelines/${id}`);
}

async function fetchArtifacts(id) {
  return apiGet(`/pipelines/${id}/artifacts`);
}

async function fetchArtifact(id, path) {
  return apiGet(`/pipelines/${id}/artifacts/${path}`);
}

async function downloadProject(id) {
  window.open(`${API_BASE}/pipelines/${id}/download`, "_blank");
}

window.api = {
  fetchHealth,
  fetchProviders,
  fetchProviderModels,
  fetchBuildProfiles,
  createPipeline,
  fetchPipelines,
  fetchCurrentPipeline,
  fetchPipeline,
  approveCheckpoint,
  submitFeedback,
  retryAgent,
  deletePipeline,
  fetchArtifacts,
  fetchArtifact,
  downloadProject,
};
