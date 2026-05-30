window.app = function () {
  const {
    fetchHealth,
    fetchProviders,
    fetchProviderModels,
    fetchBuildProfiles,
    createPipeline,
    fetchCurrentPipeline,
    fetchPipeline,
    fetchPipelines,
    approveCheckpoint,
    submitFeedback,
    retryAgent,
    deletePipeline,
    fetchArtifacts,
    fetchArtifact,
    downloadProject,
  } = window.api;

  const sse = window.sse;

  return {
    view: "welcome",
    tutorialStep: 1,
    selectedProvider: "ollama",
    selectedModel: "",
    fastModel: "",
    providerModels: [],
    providerError: "",
    projectDescription: "",
    buildPresets: {},
    selectedPreset: "standard",
    showBuildOptions: false,
    profile: {
      rigor: "standard",
      code_review: true,
      qa: true,
      e2e_tests: true,
      load_test: false,
      dast: false,
      security_scan: true,
      accessibility: true,
      devops: true,
      docs: true,
    },
    pipeline: {},
    agents: [],
    logs: [],
    expandedAgent: null,
    logIdCounter: 0,
    logAutoScroll: true,
    showCheckpointModal: false,
    checkpointArtifact: null,
    checkpointFeedback: "",
    showFeedbackArea: false,
    history: [],
    showHistory: false,
    artifacts: [],
    selectedArtifact: null,
    artifactPreview: null,
    elapsedTimer: null,
    elapsedSeconds: 0,
    focusableSelector:
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    lastFocusedElement: null,

    async initApp() {
      try {
        await fetchHealth();
      } catch (e) {
        console.warn("Backend not ready:", e);
      }

      const hasSeen = localStorage.getItem("hasSeenTutorial");
      const current = await fetchCurrentPipeline();
      if (current && current.pipeline) {
        this.pipeline = current.pipeline;
        this.agents = current.agents || [];
        this.view = this.resolveView(current.pipeline.status);
        this.startSse(current.pipeline.id);
        this.startElapsedTimer();
        if (current.pipeline.status === "checkpoint" && current.pipeline.checkpoint_artifact_path) {
          this.openCheckpointModal(current.pipeline.checkpoint_artifact_path);
        }
      } else if (!hasSeen) {
        this.view = "welcome";
      } else {
        this.view = "dashboard";
      }

      this.$watch("selectedProvider", async (val) => {
        await this.loadModels(val);
      });
      await this.loadModels(this.selectedProvider);
      await this.loadBuildProfiles();
    },

    async loadBuildProfiles() {
      try {
        const res = await fetchBuildProfiles();
        this.buildPresets = res.presets || {};
        this.applyPreset(this.selectedPreset);
      } catch (e) {
        console.warn("Failed to load build profiles:", e);
      }
    },

    applyPreset(name) {
      this.selectedPreset = name;
      const preset = this.buildPresets[name];
      if (preset) {
        this.profile = { ...this.profile, ...preset };
      }
    },

    presetLabel(name) {
      const map = {
        mvp: "MVP (fastest)",
        small: "Small project",
        standard: "Standard",
        production: "Production (most thorough)",
      };
      return map[name] || name;
    },

    startTutorial() {
      this.tutorialStep = 1;
      this.view = "tutorial";
    },

    skipTutorial() {
      localStorage.setItem("hasSeenTutorial", "true");
      this.view = "dashboard";
    },

    finishTutorial() {
      localStorage.setItem("hasSeenTutorial", "true");
      this.view = "dashboard";
    },

    tutorialTitle() {
      const titles = [
        "",
        "What is this?",
        "Pick Your AI Model",
        "Choose Build Type",
        "Describe Your Idea",
        "Watch It Build",
      ];
      return titles[this.tutorialStep];
    },

    async checkProviderHealth() {
      this.providerError = "";
      try {
        const providers = await fetchProviders();
        const p = providers.find((x) => x.name === this.selectedProvider);
        if (!p || !p.available) {
          this.providerError =
            (p && p.error) ||
            `${this.selectedProvider} is unavailable. Start the service and try again.`;
          this.providerModels = [];
          this.selectedModel = "";
        }
      } catch (e) {
        this.providerError = e.message;
      }
    },

    async loadModels(provider) {
      this.providerError = "";
      this.providerModels = [];
      try {
        const providers = await fetchProviders();
        const p = providers.find((x) => x.name === provider);
        if (!p || !p.available) {
          this.providerError =
            (p && p.error) ||
            `${provider} is unavailable. Start the service and try again.`;
          this.selectedModel = "";
          return;
        }
        const models = await fetchProviderModels(provider);
        this.providerModels = models;
        if (models.length > 0) {
          this.selectedModel = models[0];
        } else {
          this.selectedModel = "";
        }
      } catch (e) {
        this.providerError = e.message;
        this.selectedModel = "";
      }
    },

    canStartPipeline() {
      return (
        this.selectedProvider &&
        this.selectedModel &&
        this.projectDescription.trim().length > 0 &&
        (!this.pipeline.status ||
          !["running", "checkpoint"].includes(this.pipeline.status))
      );
    },

    async startPipeline() {
      try {
        const res = await createPipeline({
          project_name:
            this.projectDescription.split("\n")[0].slice(0, 100) || "Untitled",
          description: this.projectDescription,
          provider: this.selectedProvider,
          model: this.selectedModel,
          fast_model: this.fastModel || null,
          build_profile: { ...this.profile, rigor: this.selectedPreset },
        });
        this.pipeline = res.pipeline;
        this.logs = [];
        this.logIdCounter = 0;
        this.view = "pipeline";
        const current = await fetchCurrentPipeline();
        this.agents = current.agents || [];
        this.startSse(res.pipeline.id);
        this.startElapsedTimer();
      } catch (e) {
        alert("Failed to start pipeline: " + e.message);
      }
    },

    startSse(pipelineId) {
      sse.disconnect();
      sse.on("sync", (data) => {
        if (data.pipeline) {
          this.pipeline = data.pipeline;
          this.view = this.resolveView(data.pipeline.status);
        }
        if (data.agents) {
          this.agents = data.agents;
        }
      });
      sse.on("agent_start", (data) => {
        if (data.agent) {
          const a = this.agents.find((x) => x.agent_name === data.agent);
          if (a) {
            a.status = "running";
            a.started_at = new Date().toISOString();
          }
        }
      });
      sse.on("log", (data) => {
        if (data.line) {
          this.pushLog(data.line);
        }
      });
      sse.on("checkpoint", (data) => {
        if (data.pipeline) {
          this.pipeline = data.pipeline;
        }
        this.openCheckpointModal(data.artifact_path);
      });
      sse.on("complete", (data) => {
        if (data.status) {
          this.pipeline = data;
        } else if (data.pipeline) {
          this.pipeline = data.pipeline;
        }
        this.view = "completion";
        this.stopElapsedTimer();
      });
      sse.on("error", (err) => {
        console.warn("SSE error:", err);
        if (err.detail) {
          this.pushLog(`[error] ${err.detail}`);
        }
      });
      sse.on("ping", () => {});
      sse.connect(pipelineId);
    },

    pushLog(line) {
      const ts = new Date().toLocaleTimeString();
      this.logs.push({ id: ++this.logIdCounter, ts, msg: line });
      if (this.logs.length > 500) {
        this.logs.shift();
      }
      this.$nextTick(() => {
        if (this.logAutoScroll) {
          this.scrollLogToBottom();
        }
      });
    },

    scrollLogToBottom() {
      const panel = this.$refs.logPanel;
      if (panel) {
        panel.scrollTop = panel.scrollHeight;
      }
    },

    onLogScroll() {
      const panel = this.$refs.logPanel;
      if (!panel) return;
      const nearBottom =
        panel.scrollHeight - panel.scrollTop - panel.clientHeight < 20;
      this.logAutoScroll = nearBottom;
    },

    resolveView(status) {
      if (!status) return "dashboard";
      if (["running", "checkpoint"].includes(status)) return "pipeline";
      if (status === "completed") return "completion";
      if (status === "failed") return "pipeline";
      return "dashboard";
    },

    startElapsedTimer() {
      this.stopElapsedTimer();
      const created = this.pipeline.created_at
        ? new Date(this.pipeline.created_at)
        : new Date();
      const update = () => {
        const now = new Date();
        this.elapsedSeconds = Math.floor((now - created) / 1000);
      };
      update();
      this.elapsedTimer = setInterval(update, 1000);
    },

    stopElapsedTimer() {
      if (this.elapsedTimer) {
        clearInterval(this.elapsedTimer);
        this.elapsedTimer = null;
      }
    },

    formatElapsed(sec) {
      if (!sec && sec !== 0) return "0s";
      const h = Math.floor(sec / 3600);
      const m = Math.floor((sec % 3600) / 60);
      const s = sec % 60;
      if (h > 0) return `${h}h ${m}m ${s}s`;
      if (m > 0) return `${m}m ${s}s`;
      return `${s}s`;
    },

    statusBadgeClass(status) {
      const map = {
        idle: "ds-badge--info",
        running: "ds-badge--info",
        checkpoint: "ds-badge--warning",
        completed: "ds-badge--success",
        failed: "ds-badge--error",
      };
      return map[status] || "ds-badge--info";
    },

    agentCardClass(agent) {
      const classes = ["ds-card--interactive"];
      if (agent.status === "running") classes.push("ds-agent-card--running");
      if (agent.status === "completed") classes.push("ds-card--success");
      if (agent.status === "failed") classes.push("ds-card--error");
      if (agent.status === "pending" && this.pipeline.current_agent === agent.agent_name) {
        classes.push("ds-card--active");
      }
      return classes.join(" ");
    },

    agentBadgeClass(status) {
      const map = {
        pending: "ds-badge--info",
        running: "ds-badge--info",
        completed: "ds-badge--success",
        failed: "ds-badge--error",
      };
      return map[status] || "ds-badge--info";
    },

    agentIcon(agent) {
      const map = {
        pending: "",
        running: "▶️",
        completed: "✅",
        failed: "❌",
      };
      return map[agent.status] || "";
    },

    formatAgentName(name) {
      const map = {
        req_engineer: "Requirements",
        sw_architect: "Architect",
        proj_manager: "Planner",
        sw_developer: "Developer",
        code_reviewer: "Reviewer",
        qa_engineer: "QA",
        devops_engineer: "DevOps",
        tech_writer: "Writer",
      };
      return map[name] || name;
    },

    formatDuration(ms) {
      if (!ms) return "";
      const sec = Math.floor(ms / 1000);
      if (sec < 60) return `${sec}s`;
      const min = Math.floor(sec / 60);
      const rem = sec % 60;
      return `${min}m ${rem}s`;
    },

    pipelineDurationMs(pipeline) {
      if (!pipeline || !pipeline.created_at) return null;
      const created = new Date(pipeline.created_at);
      const end = pipeline.completed_at
        ? new Date(pipeline.completed_at)
        : new Date();
      return end - created;
    },

    toggleAgent(name) {
      this.expandedAgent = this.expandedAgent === name ? null : name;
    },

    agentDetails(name) {
      const map = {
        req_engineer: "Gathers and clarifies project requirements, writes requirements.md.",
        sw_architect: "Designs the tech stack, security plan, and architecture.",
        proj_manager: "Breaks work into epics, stories, and tasks. Writes project-plan.md.",
        sw_developer: "Implements the code according to the plan.",
        code_reviewer: "Reviews code for correctness, security, and style.",
        qa_engineer: "Runs tests and writes bug-report.md.",
        devops_engineer: "Creates deployment configuration and DEPLOYMENT.md.",
        tech_writer: "Writes final documentation and README.md.",
      };
      return map[name] || "";
    },

    copyLogs() {
      const text = this.logs.map((l) => `${l.ts} ${l.msg}`).join("\n");
      navigator.clipboard.writeText(text).catch(console.error);
    },

    async openCheckpointModal(artifactPath) {
      this.checkpointArtifact = null;
      this.showFeedbackArea = false;
      this.checkpointFeedback = "";
      if (artifactPath && this.pipeline.id) {
        try {
          const art = await fetchArtifact(this.pipeline.id, artifactPath);
          this.checkpointArtifact = art;
        } catch (e) {
          console.warn("Failed to load artifact:", e);
          this.checkpointArtifact = {
            path: artifactPath,
            content: "Unable to load artifact preview.",
            content_type: "text/plain",
          };
        }
      }
      this.showCheckpointModal = true;
      this.lastFocusedElement = document.activeElement;
      this.$nextTick(() => {
        this.trapFocus(this.$refs.checkpointModal);
      });
    },

    closeCheckpointModal() {
      this.showCheckpointModal = false;
      if (this.lastFocusedElement) {
        this.lastFocusedElement.focus();
      }
    },

    async approveCheckpointAndClose() {
      try {
        await approveCheckpoint(this.pipeline.id);
        this.closeCheckpointModal();
      } catch (e) {
        alert("Failed to approve: " + e.message);
      }
    },

    showFeedback() {
      this.showFeedbackArea = true;
      this.$nextTick(() => {
        const el = this.$refs.feedbackTextarea;
        if (el) el.focus();
      });
    },

    async submitFeedbackAndClose() {
      if (!this.checkpointFeedback.trim()) {
        this.closeCheckpointModal();
        return;
      }
      try {
        await submitFeedback(this.pipeline.id, this.checkpointFeedback.trim());
        this.closeCheckpointModal();
      } catch (e) {
        alert("Failed to submit feedback: " + e.message);
      }
    },

    async retryFailedAgent(agentName) {
      try {
        await retryAgent(this.pipeline.id, agentName);
      } catch (e) {
        alert("Failed to retry agent: " + e.message);
      }
    },

    trapFocus(modalEl) {
      if (!modalEl) return;
      const focusable = Array.from(
        modalEl.querySelectorAll(this.focusableSelector)
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      first.focus();

      modalEl._trapHandler = (e) => {
        if (e.key !== "Tab") return;
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      };
      modalEl.addEventListener("keydown", modalEl._trapHandler);
    },

    untrapFocus(modalEl) {
      if (modalEl && modalEl._trapHandler) {
        modalEl.removeEventListener("keydown", modalEl._trapHandler);
        delete modalEl._trapHandler;
      }
    },

    onCheckpointKeydown(e) {
      if (e.key === "Escape") {
        if (!this.showFeedbackArea) {
          this.closeCheckpointModal();
        }
      }
    },

    async loadHistory() {
      try {
        const res = await fetchPipelines(100, 0);
        this.history = res.pipelines || [];
      } catch (e) {
        console.warn("Failed to load history:", e);
      }
    },

    async toggleHistory() {
      this.showHistory = !this.showHistory;
      if (this.showHistory) {
        await this.loadHistory();
      }
    },

    async resumePipeline(id) {
      try {
        await approveCheckpoint(id);
        const run = await fetchPipeline(id);
        if (run && run.pipeline) {
          this.pipeline = run.pipeline;
          this.agents = run.agents || [];
          this.view = this.resolveView(run.pipeline.status);
          this.startSse(id);
          this.startElapsedTimer();
        }
        this.showHistory = false;
      } catch (e) {
        alert("Failed to resume pipeline: " + e.message);
      }
    },

    async viewHistoryPipeline(id) {
      try {
        const run = await fetchPipeline(id);
        if (run && run.pipeline) {
          this.pipeline = run.pipeline;
          this.agents = run.agents || [];
          this.view = this.resolveView(run.pipeline.status);
          this.startSse(id);
          this.startElapsedTimer();
        }
        this.showHistory = false;
      } catch (e) {
        alert("Failed to load pipeline: " + e.message);
      }
    },

    async confirmDeletePipeline(id, name) {
      const ok = confirm(
        `Delete '${name}' and all its files? This cannot be undone.`
      );
      if (!ok) return;
      try {
        await deletePipeline(id);
        await this.loadHistory();
        if (this.pipeline.id === id) {
          this.pipeline = {};
          this.agents = [];
          this.logs = [];
          this.view = "dashboard";
          this.stopElapsedTimer();
        }
      } catch (e) {
        alert("Failed to delete pipeline: " + e.message);
      }
    },

    historyStatusBadgeClass(status) {
      return this.statusBadgeClass(status);
    },

    async loadArtifacts() {
      if (!this.pipeline.id) return;
      try {
        const res = await fetchArtifacts(this.pipeline.id);
        this.artifacts = res.artifacts || [];
      } catch (e) {
        console.warn("Failed to load artifacts:", e);
      }
    },

    async selectArtifact(path) {
      if (!this.pipeline.id) return;
      try {
        const art = await fetchArtifact(this.pipeline.id, path);
        this.selectedArtifact = art;
        this.renderArtifactPreview(art);
      } catch (e) {
        console.warn("Failed to load artifact:", e);
      }
    },

    renderArtifactPreview(art) {
      if (!art) {
        this.artifactPreview = null;
        return;
      }
      if (art.content_type === "text/markdown") {
        if (window.marked) {
          this.artifactPreview = {
            type: "markdown",
            html: window.marked.parse(art.content),
          };
        } else {
          this.artifactPreview = { type: "text", content: art.content };
        }
      } else if (art.language) {
        this.artifactPreview = {
          type: "code",
          language: art.language,
          content: art.content,
        };
        this.$nextTick(() => {
          if (window.hljs) {
            window.hljs.highlightAll();
          }
        });
      } else {
        this.artifactPreview = { type: "text", content: art.content };
      }
    },

    artifactIcon(path) {
      const ext = path.split(".").pop().toLowerCase();
      const map = {
        md: "📄",
        py: "🐍",
        js: "📜",
        ts: "📘",
        json: "📋",
        html: "🌐",
        css: "🎨",
        yml: "⚙️",
        yaml: "⚙️",
        sh: "🐚",
        dockerfile: "🐳",
        png: "🖼️",
        jpg: "🖼️",
        jpeg: "🖼️",
        gif: "🖼️",
        svg: "🖼️",
      };
      return map[ext] || "📄";
    },

    downloadArtifact(path) {
      if (!this.pipeline.id) return;
      const a = document.createElement("a");
      a.href = `/api/pipelines/${this.pipeline.id}/artifacts/${path}`;
      a.download = path.split("/").pop();
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },

    downloadAll() {
      if (!this.pipeline.id) return;
      downloadProject(this.pipeline.id);
    },

    backToDashboard() {
      this.view = "dashboard";
      this.pipeline = {};
      this.agents = [];
      this.logs = [];
      this.stopElapsedTimer();
    },
  };
};
