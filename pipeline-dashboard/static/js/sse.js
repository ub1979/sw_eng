let sseSource = null;
let sseReconnectDelay = 1000;
let sseReconnectTimer = null;
let sseListeners = {};

function on(eventType, handler) {
  if (!sseListeners[eventType]) {
    sseListeners[eventType] = [];
  }
  sseListeners[eventType].push(handler);
}

function off(eventType, handler) {
  if (!sseListeners[eventType]) return;
  sseListeners[eventType] = sseListeners[eventType].filter((h) => h !== handler);
}

function emit(eventType, data) {
  const handlers = sseListeners[eventType];
  if (!handlers) return;
  handlers.forEach((h) => {
    try {
      h(data);
    } catch (e) {
      console.error("SSE handler error:", e);
    }
  });
}

function connect(pipelineId) {
  disconnect();
  const url = `/api/pipelines/${pipelineId}/events`;
  sseSource = new EventSource(url);

  sseSource.onopen = () => {
    sseReconnectDelay = 1000;
    emit("open", {});
  };

  sseSource.onmessage = (event) => {
    let data = null;
    try {
      data = JSON.parse(event.data);
    } catch {
      data = event.data;
    }
    emit(event.type, data);
  };

  sseSource.addEventListener("sync", (event) => {
    let data = null;
    try {
      data = JSON.parse(event.data);
    } catch {
      data = event.data;
    }
    emit("sync", data);
  });

  sseSource.addEventListener("ping", (event) => {
    emit("ping", event.data);
  });

  sseSource.addEventListener("error", (event) => {
    emit("error", event);
  });

  sseSource.onerror = () => {
    emit("error", {});
    disconnect();
    scheduleReconnect(pipelineId);
  };
}

function disconnect() {
  if (sseSource) {
    sseSource.close();
    sseSource = null;
  }
  if (sseReconnectTimer) {
    clearTimeout(sseReconnectTimer);
    sseReconnectTimer = null;
  }
}

function scheduleReconnect(pipelineId) {
  sseReconnectTimer = setTimeout(() => {
    sseReconnectDelay = Math.min(sseReconnectDelay * 2, 8000);
    connect(pipelineId);
  }, sseReconnectDelay);
}

window.sse = {
  connect,
  disconnect,
  on,
  off,
};
