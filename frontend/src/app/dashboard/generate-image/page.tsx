"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import {
  Wand2, Settings2, Image as ImageIcon, Sparkles, Download,
  Maximize, RotateCcw, X, AlertCircle, CheckCircle2,
  Zap, ChevronDown, Terminal, Loader2, Cpu, Database,
} from "lucide-react";
import {
  generateImage, subscribeToJob, getGenerationHistory, resolveImageUrl,
  aspectRatioDimensions, healthCheck,
  type JobStatusResponse, type GenerateImageParams,
} from "@/lib/api";

// ─── Types ────────────────────────────────────────────────────
interface LogEntry { time: string; message: string; type: "info" | "success" | "error" | "progress"; }
interface ActiveJob { jobId: string; progress: number; status: string; logs: LogEntry[]; }

// ─── Constants ────────────────────────────────────────────────
const STYLES = ["Cinematic Realism", "Dark Documentary", "War Archives", "Neo Noir", "Analog Film", "Horror Atmosphere", "Sci-Fi Future", "Historical Reconstruction", "Drone Shot", "Apocalypse", "YouTube Thumbnail (Dark Mystery)", "YouTube Thumbnail (Conspiracy)", "YouTube Thumbnail (Face Zoom)"];
const RATIOS = ["16:9","9:16","1:1","21:9","4:3"];
const MODELS = [{ value: "flux", label: "FLUX.1-dev", badge: "BEST" }, { value: "sdxl", label: "SDXL 1.0", badge: "FAST" }];
const SAMPLERS = ["euler","euler_ancestral","dpm_2","dpm_2_ancestral","ddim","lcm"];
const SCHEDULERS = ["normal","karras","exponential","simple"];

function now() { return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); }

// ─── Sub-components ───────────────────────────────────────────

function StatusBadge({ comfyui }: { comfyui: string | null }) {
  const ok = comfyui === "connected";
  return (
    <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full border ${ok ? "border-green-500/30 bg-green-500/10 text-green-400" : "border-red-500/30 bg-red-500/10 text-red-400"}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${ok ? "bg-green-400 animate-pulse" : "bg-red-400"}`} />
      ComfyUI {ok ? "Online" : "Offline"}
    </div>
  );
}

function LogsModal({ logs, onClose }: { logs: LogEntry[]; onClose: () => void }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-[#0d0d0f] border border-border rounded-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div className="flex items-center gap-2"><Terminal className="w-4 h-4 text-primary" /><span className="font-bold">Generation Logs</span></div>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground"><X className="w-5 h-5" /></button>
        </div>
        <div className="h-80 overflow-y-auto p-4 font-mono text-xs space-y-1">
          {logs.length === 0 && <p className="text-muted-foreground">No logs yet…</p>}
          {logs.map((l, i) => (
            <div key={i} className={`flex gap-3 ${l.type === "error" ? "text-red-400" : l.type === "success" ? "text-green-400" : l.type === "progress" ? "text-blue-400" : "text-muted-foreground"}`}>
              <span className="opacity-50 shrink-0">{l.time}</span>
              <span>{l.message}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </motion.div>
    </div>
  );
}

function GeneratedCard({ job, onExpand }: { job: JobStatusResponse; onExpand: (url: string) => void }) {
  const imgUrl = job.output_url ? resolveImageUrl(job.output_url) : null;
  return (
    <motion.div
      layout initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
      className="group relative aspect-video bg-background border border-border rounded-xl overflow-hidden"
    >
      {imgUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={imgUrl} alt={job.prompt ?? ""} className="w-full h-full object-cover" />
      ) : (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted-foreground">
          {job.status === "failed" ? (
            <><AlertCircle className="w-7 h-7 text-red-500" /><span className="text-xs text-red-400 text-center px-3">{job.error_message ?? "Failed"}</span></>
          ) : (
            <><ImageIcon className="w-8 h-8 opacity-20" /><span className="text-xs opacity-40">{job.status}</span></>
          )}
        </div>
      )}
      {imgUrl && (
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-3 backdrop-blur-sm">
          <div className="flex justify-end gap-2">
            <button onClick={() => onExpand(imgUrl)} className="p-1.5 bg-white/10 hover:bg-white/20 rounded-md text-white"><Maximize className="w-4 h-4" /></button>
            <a href={imgUrl} download className="p-1.5 bg-white/10 hover:bg-white/20 rounded-md text-white"><Download className="w-4 h-4" /></a>
          </div>
          <div className="text-xs text-white/80 line-clamp-2">{job.prompt}</div>
        </div>
      )}
    </motion.div>
  );
}

function ActiveJobCard({ job }: { job: ActiveJob }) {
  return (
    <div className="aspect-video bg-background border border-primary/30 rounded-xl overflow-hidden relative">
      <div className="absolute inset-0 bg-gradient-to-r from-background via-primary/5 to-background animate-pulse" />
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 p-4">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <div className="w-full max-w-[80%]">
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span className="capitalize">{job.status}</span>
            <span>{job.progress}%</span>
          </div>
          <div className="h-1.5 bg-border rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
              initial={{ width: 0 }} animate={{ width: `${job.progress}%` }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            />
          </div>
        </div>
        <span className="text-xs text-muted-foreground animate-pulse">AI is rendering your scene…</span>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────
export default function GenerateImage() {
  // Form state
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("Cinematic Realism");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [model, setModel] = useState<"flux" | "sdxl">("flux");
  const [steps, setSteps] = useState(20);
  const [cfg, setCfg] = useState(7.0);
  const [sampler, setSampler] = useState("euler");
  const [scheduler, setScheduler] = useState("normal");
  const [seed, setSeed] = useState(-1);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeJob, setActiveJob] = useState<ActiveJob | null>(null);
  const [history, setHistory] = useState<JobStatusResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [comfyuiStatus, setComfyuiStatus] = useState<string | null>(null);

  // UI state
  const [showLogs, setShowLogs] = useState(false);
  const [expandedImage, setExpandedImage] = useState<string | null>(null);

  const wsCleanupRef = useRef<(() => void) | null>(null);

  // ── Load history + health check on mount ──
  useEffect(() => {
    getGenerationHistory(12).then(setHistory).catch(console.error);
    healthCheck().then((r) => setComfyuiStatus(r.comfyui)).catch(() => setComfyuiStatus("unreachable"));
  }, []);

  // ── Cleanup WS on unmount ──
  useEffect(() => () => { wsCleanupRef.current?.(); }, []);

  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;
    setError(null);
    setIsGenerating(true);

    const dims = aspectRatioDimensions(aspectRatio);
    const params: GenerateImageParams = {
      prompt: prompt.trim(),
      negative_prompt: negativePrompt.trim() || undefined,
      style: selectedStyle,
      model,
      steps,
      cfg_scale: cfg,
      sampler: sampler as GenerateImageParams["sampler"],
      scheduler: scheduler as GenerateImageParams["scheduler"],
      seed: seed === -1 ? -1 : seed,
      width: dims.width,
      height: dims.height,
    };

    try {
      const { job_id } = await generateImage(params);
      const job: ActiveJob = { jobId: job_id, progress: 0, status: "queued", logs: [{ time: now(), message: `Job queued → ${job_id}`, type: "info" }] };
      setActiveJob(job);

      wsCleanupRef.current = subscribeToJob(job_id, {
        onProgress: (ev) => {
          const pct = ev.progress ?? 0;
          const step = "step" in ev ? ev.step : undefined;
          const msg = step != null ? `Step ${step} — ${pct}%` : `Progress: ${pct}%`;
          setActiveJob((prev) => prev ? { ...prev, progress: pct, status: "processing", logs: [...prev.logs, { time: now(), message: msg, type: "progress" }] } : prev);
        },
        onCompleted: (ev) => {
          setActiveJob(null);
          setIsGenerating(false);
          const completed: JobStatusResponse = {
            job_id,
            job_type: "image",
            status: "completed",
            progress: 100,
            prompt: params.prompt,
            style: params.style,
            model: params.model,
            output_url: ev.output_url,
            completed_at: new Date().toISOString(),
          };
          setHistory((prev) => [completed, ...prev]);
          wsCleanupRef.current = null;
        },
        onError: (ev) => {
          setError(ev.message);
          setActiveJob((prev) => prev ? { ...prev, status: "failed", logs: [...prev.logs, { time: now(), message: `Error: ${ev.message}`, type: "error" }] } : prev);
          setIsGenerating(false);
          wsCleanupRef.current = null;
        },
        onClose: () => {
          if (isGenerating) setIsGenerating(false);
        },
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to queue generation";
      setError(msg);
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    wsCleanupRef.current?.();
    wsCleanupRef.current = null;
    setIsGenerating(false);
    setActiveJob(null);
    setError(null);
  };

  return (
    <>
      {/* Logs Modal */}
      <AnimatePresence>
        {showLogs && activeJob && <LogsModal logs={activeJob.logs} onClose={() => setShowLogs(false)} />}
      </AnimatePresence>

      {/* Expanded image lightbox */}
      <AnimatePresence>
        {expandedImage && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" onClick={() => setExpandedImage(null)}>
            <motion.img
              src={expandedImage} alt="Generated"
              initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
              className="max-w-full max-h-[90vh] rounded-xl shadow-2xl object-contain"
            />
            <button onClick={() => setExpandedImage(null)} className="absolute top-4 right-4 text-white/70 hover:text-white"><X className="w-8 h-8" /></button>
          </div>
        )}
      </AnimatePresence>

      <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)]">

        {/* ── Settings Panel ── */}
        <div className="w-full lg:w-80 shrink-0 bg-card border border-border/50 rounded-2xl p-5 overflow-y-auto hidden md:block glass">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <Settings2 className="w-5 h-5 text-primary" />
              <h2 className="font-bold text-lg">Settings</h2>
            </div>
            <StatusBadge comfyui={comfyuiStatus} />
          </div>

          <div className="space-y-6">
            {/* Model */}
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 block">AI Model</label>
              <div className="flex flex-col gap-2">
                {MODELS.map((m) => (
                  <button key={m.value} onClick={() => setModel(m.value as "flux" | "sdxl")}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-lg border text-sm font-medium transition-all ${model === m.value ? "bg-primary/15 border-primary/50 text-primary" : "bg-background border-border text-muted-foreground hover:border-primary/30"}`}>
                    <div className="flex items-center gap-2"><Cpu className="w-4 h-4" />{m.label}</div>
                    <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${model === m.value ? "bg-primary text-white" : "bg-muted text-muted-foreground"}`}>{m.badge}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Style */}
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 block">Style Preset</label>
              <div className="flex flex-wrap gap-1.5">
                {STYLES.map((s) => (
                  <button key={s} onClick={() => setSelectedStyle(s)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${selectedStyle === s ? "bg-primary text-white" : "bg-background border border-border text-muted-foreground hover:border-primary/50"}`}>
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Aspect Ratio */}
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 block">Aspect Ratio</label>
              <div className="grid grid-cols-3 gap-1.5">
                {RATIOS.map((r) => (
                  <button key={r} onClick={() => setAspectRatio(r)}
                    className={`py-2 rounded-lg text-xs font-medium transition-all flex flex-col items-center gap-1 ${aspectRatio === r ? "bg-primary/20 text-primary border border-primary/50" : "bg-background border border-border text-muted-foreground hover:border-primary/30"}`}>
                    <div className={`border-2 ${aspectRatio === r ? "border-primary" : "border-muted-foreground"} rounded-sm ${r === "16:9" ? "w-6 h-3.5" : r === "9:16" ? "w-3.5 h-6" : r === "1:1" ? "w-5 h-5" : r === "21:9" ? "w-7 h-3" : "w-5 h-4"}`} />
                    {r}
                  </button>
                ))}
              </div>
            </div>

            {/* Steps & CFG */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Steps <span className="text-foreground font-semibold">{steps}</span></label>
                <input type="range" min={1} max={100} value={steps} onChange={(e) => setSteps(+e.target.value)} className="w-full accent-primary" />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">CFG <span className="text-foreground font-semibold">{cfg.toFixed(1)}</span></label>
                <input type="range" min={1} max={20} step={0.5} value={cfg} onChange={(e) => setCfg(+e.target.value)} className="w-full accent-primary" />
              </div>
            </div>

            {/* Advanced toggle */}
            <button onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center justify-between w-full text-xs font-semibold text-muted-foreground uppercase tracking-wider hover:text-foreground transition-colors">
              Advanced Control <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? "rotate-180" : ""}`} />
            </button>

            <AnimatePresence>
              {showAdvanced && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="space-y-3 overflow-hidden">
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Sampler</label>
                    <select value={sampler} onChange={(e) => setSampler(e.target.value)} className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary">
                      {SAMPLERS.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Scheduler</label>
                    <select value={scheduler} onChange={(e) => setScheduler(e.target.value)} className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary">
                      {SCHEDULERS.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Seed (-1 = random)</label>
                    <input type="number" min={-1} value={seed} onChange={(e) => setSeed(+e.target.value)}
                      className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* ── Main Studio Area ── */}
        <div className="flex-1 flex flex-col min-h-0">

          {/* Prompt Area */}
          <div className="bg-card border border-border/50 p-4 rounded-2xl glass mb-4 shrink-0">
            <div className="relative mb-3">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the cinematic scene… (e.g. A neon-lit cyberpunk alleyway, rain-soaked streets, volumetric lighting, 8K)"
                className="w-full h-24 bg-background/50 border border-border rounded-xl p-4 text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary resize-none text-sm"
              />
              <button className="absolute bottom-3 right-3 text-primary/70 hover:text-primary bg-primary/10 p-1.5 rounded-lg transition-colors" title="Enhance prompt">
                <Sparkles className="w-4 h-4" />
              </button>
            </div>

            <div className="relative mb-4">
              <input type="text" value={negativePrompt} onChange={(e) => setNegativePrompt(e.target.value)}
                placeholder="Negative prompt (what to avoid)…"
                className="w-full bg-background/50 border border-border rounded-lg px-4 py-2 text-sm text-foreground focus:outline-none focus:border-red-500/50" />
            </div>

            {/* Error banner */}
            <AnimatePresence>
              {error && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
                  className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-2 mb-3">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="flex-1">{error}</span>
                  <button onClick={() => setError(null)}><X className="w-4 h-4" /></button>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                <button onClick={handleReset} className="p-2 bg-background border border-border rounded-lg text-muted-foreground hover:text-foreground transition-colors" title="Clear / Cancel">
                  <RotateCcw className="w-5 h-5" />
                </button>
                {activeJob && (
                  <button onClick={() => setShowLogs(true)} className="flex items-center gap-1.5 px-3 py-2 bg-background border border-border rounded-lg text-xs text-muted-foreground hover:text-foreground transition-colors">
                    <Terminal className="w-4 h-4" /> Logs
                  </button>
                )}
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className={`px-8 py-2.5 rounded-xl font-bold flex items-center gap-2 transition-all ${isGenerating || !prompt.trim() ? "bg-muted text-muted-foreground cursor-not-allowed" : "bg-primary text-white hover:bg-primary/90"}`}>
                {isGenerating ? (
                  <><Loader2 className="w-4 h-4 animate-spin" />Generating…</>
                ) : (
                  <><Wand2 className="w-5 h-5" />Generate</>
                )}
              </button>
            </div>

            {/* Progress bar */}
            <AnimatePresence>
              {activeJob && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mt-3 overflow-hidden">
                  <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                    <div className="flex items-center gap-1.5">
                      <Zap className="w-3 h-3 text-primary animate-pulse" />
                      <span className="capitalize">{activeJob.status}</span>
                    </div>
                    <span className="font-mono">{activeJob.progress}%</span>
                  </div>
                  <div className="h-1.5 bg-border rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
                      initial={{ width: 0 }} animate={{ width: `${activeJob.progress}%` }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Gallery */}
          <div className="flex-1 bg-card border border-border/50 rounded-2xl glass p-5 overflow-y-auto">
            <div className="flex items-center justify-between mb-4 shrink-0">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-primary" /> Generated Images
              </h3>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <div className="flex items-center gap-1"><Database className="w-3 h-3" />{history.length} images</div>
                {history.some((j) => j.status === "completed") && (
                  <div className="flex items-center gap-1 text-green-400"><CheckCircle2 className="w-3 h-3" />Saved locally</div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {/* Active generation card */}
              {activeJob && <ActiveJobCard job={activeJob} />}

              {/* History */}
              {history.map((job) => (
                <GeneratedCard key={job.job_id} job={job} onExpand={setExpandedImage} />
              ))}

              {/* Empty state */}
              {!activeJob && history.length === 0 && (
                <div className="col-span-full flex flex-col items-center justify-center py-20 text-muted-foreground">
                  <ImageIcon className="w-12 h-12 opacity-20 mb-3" />
                  <p className="text-sm">Your generated images will appear here</p>
                  <p className="text-xs mt-1 opacity-60">Enter a prompt and click Generate to begin</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
