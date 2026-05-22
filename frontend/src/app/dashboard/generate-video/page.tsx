"use client";

import { useState, useRef, useEffect } from "react";
import { Wand2, Settings2, Video, Upload, Sparkles, Move, Clock, MonitorPlay, Layers, Volume2, Type, GripVertical, Scissors, ChevronRight, SaveAll, Database } from "lucide-react";
import { generateVideo, subscribeToJob, type VideoModelChoice } from "@/lib/api";

export default function GenerateVideo() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState<"text" | "image">("text");
  const [isGenerating, setIsGenerating] = useState(false);
  const [motionPreset, setMotionPreset] = useState("Pan Right");
  const [duration, setDuration] = useState("5s");
  const [model, setModel] = useState<VideoModelChoice>("wan21");
  const [progress, setProgress] = useState(0);
  const [outputUrl, setOutputUrl] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [batchQueue, setBatchQueue] = useState<any[]>([]);

  const wsCleanup = useRef<(() => void) | null>(null);

  const motions = ["None", "Pan Left", "Pan Right", "Zoom In", "Zoom Out", "Tilt Up", "Tilt Down", "Tracking"];
  const durations = ["3s", "5s", "10s", "15s"];

  useEffect(() => {
    return () => {
      if (wsCleanup.current) wsCleanup.current();
    };
  }, []);

  const handleGenerate = async () => {
    if (!prompt && mode === "text") return;
    setIsGenerating(true);
    setProgress(0);
    setOutputUrl(null);
    setErrorMsg(null);

    try {
      const { job_id } = await generateVideo({
        prompt,
        motion_preset: motionPreset,
        duration,
        model,
      });

      const cleanup = subscribeToJob(job_id, {
        onProgress: (ev) => {
          setProgress(ev.progress ?? 0);
        },
        onCompleted: (ev) => {
          setIsGenerating(false);
          setProgress(100);
          setOutputUrl(ev.output_url);
        },
        onError: (ev) => {
          setIsGenerating(false);
          setErrorMsg(ev.message);
        }
      });

      wsCleanup.current = cleanup;
    } catch (err: any) {
      setIsGenerating(false);
      setErrorMsg(err.message || "Failed to start generation");
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)]">
      {/* Settings Panel */}
      <div className="w-full lg:w-80 shrink-0 bg-card border border-border/50 rounded-2xl p-6 overflow-y-auto hidden md:block glass">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Settings2 className="w-5 h-5 text-accent" />
            <h2 className="font-bold text-lg">Video Settings</h2>
          </div>
          <span className="text-[10px] text-muted-foreground uppercase tracking-widest bg-background px-2 py-0.5 rounded border border-border">Auto-Saved</span>
        </div>

        <div className="space-y-6">
          {/* Mode Selector */}
          <div>
            <div className="flex p-1 bg-background border border-border rounded-lg mb-6">
              <button
                onClick={() => setMode("text")}
                className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${
                  mode === "text" ? 'bg-accent text-white shadow-sm' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Text to Video
              </button>
              <button
                onClick={() => setMode("image")}
                className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${
                  mode === "image" ? 'bg-accent text-white shadow-sm' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Image to Video
              </button>
            </div>
          </div>

          {/* Model Selection */}
          <div>
             <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
               <Layers className="w-4 h-4" /> AI Model
             </label>
             <select 
               value={model}
               onChange={(e) => setModel(e.target.value as VideoModelChoice)}
               className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground focus:outline-none focus:border-accent"
             >
               <option value="wan21">Wan2.1 (Cinematic)</option>
               <option value="cogvideo">CogVideoX (Action)</option>
               <option value="svd">Stable Video Diffusion (Fallback)</option>
             </select>
          </div>

          {/* Camera Motion */}
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
              <Move className="w-4 h-4" /> Camera Motion
            </label>
            <div className="grid grid-cols-2 gap-2">
              {motions.map(motion => (
                <button
                  key={motion}
                  onClick={() => setMotionPreset(motion)}
                  className={`py-2 px-3 rounded-lg text-xs font-medium transition-all ${
                    motionPreset === motion ? 'bg-accent/20 text-accent border border-accent/50' : 'bg-background border border-border text-muted-foreground hover:border-accent/30'
                  }`}
                >
                  {motion}
                </button>
              ))}
            </div>
          </div>

          {/* Duration Selector */}
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4" /> Duration
            </label>
            <div className="flex gap-2">
              {durations.map(d => (
                <button
                  key={d}
                  onClick={() => setDuration(d)}
                  className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                    duration === d ? 'bg-accent text-white box-shadow-[0_0_15px_rgba(37,99,235,0.3)] border-accent' : 'bg-background border border-border text-muted-foreground hover:border-accent/50'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Studio Area */}
      <div className="flex-1 flex flex-col min-h-0 gap-6">
        {/* Input Area */}
        <div className="bg-card border border-border/50 p-4 rounded-2xl glass shrink-0">
          {mode === "image" && (
            <div className="mb-4 w-full h-32 border-2 border-dashed border-border rounded-xl flex flex-col items-center justify-center hover:border-accent/50 transition-colors cursor-pointer bg-background/50">
              <Upload className="w-6 h-6 mb-2 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">Upload Initial Frame</span>
              <span className="text-xs text-muted-foreground">JPG, PNG, WebP up to 10MB</span>
            </div>
          )}
          
          <div className="relative mb-4">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the motion and scene details... (e.g., The camera slowly pans across a futuristic neon city as flying cars zoom past, rain falling heavily)"
              className="w-full h-24 bg-background/50 border border-border rounded-xl p-4 text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent resize-none text-sm"
            />
            <button className="absolute bottom-3 right-3 text-accent/70 hover:text-accent bg-accent/10 p-1.5 rounded-lg transition-colors">
              <Sparkles className="w-4 h-4" />
            </button>
          </div>

          <div className="flex justify-end gap-3">
            <button
              onClick={() => {
                if (prompt) {
                  setBatchQueue([...batchQueue, { prompt, motionPreset, duration, model }]);
                  setPrompt("");
                }
              }}
              disabled={!prompt && mode === "text"}
              className={`px-6 py-2.5 rounded-xl font-bold flex items-center gap-2 transition-all ${
                (!prompt && mode === "text") ? 'bg-muted text-muted-foreground cursor-not-allowed' : 'bg-background border border-border hover:border-accent text-foreground shadow-sm hover:shadow-[0_0_15px_rgba(37,99,235,0.2)]'
              }`}
            >
              <Database className="w-5 h-5" /> Add to Batch Queue {batchQueue.length > 0 && `(${batchQueue.length})`}
            </button>
            <button
              onClick={handleGenerate}
              disabled={isGenerating || (!prompt && mode === "text" && batchQueue.length === 0)}
              className={`px-8 py-2.5 rounded-xl font-bold flex items-center gap-2 transition-all ${
                isGenerating || (!prompt && mode === "text" && batchQueue.length === 0) ? 'bg-muted text-muted-foreground cursor-not-allowed' : 'bg-accent text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:bg-accent/90'
              }`}
            >
              {isGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Rendering... {progress}%
                </>
              ) : (
                <>
                  {batchQueue.length > 0 ? <SaveAll className="w-5 h-5" /> : <Wand2 className="w-5 h-5" />} 
                  {batchQueue.length > 0 ? `Render Batch (${batchQueue.length})` : "Generate Video"}
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preview Player / Timeline */}
        <div className="flex-1 bg-card border border-border/50 rounded-2xl glass p-6 flex flex-col min-h-0">
          <div className="flex items-center justify-between mb-4 shrink-0">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <MonitorPlay className="w-5 h-5 text-accent" /> Output Player
            </h3>
          </div>
          
          <div className="flex-1 border border-border rounded-xl bg-background overflow-hidden relative group mb-6 min-h-[200px]">
            {isGenerating ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-background/50 backdrop-blur-sm z-10">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-accent/20 border-t-accent rounded-full animate-spin" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Video className="w-6 h-6 text-accent animate-pulse" />
                  </div>
                </div>
                <div className="text-center">
                  <p className="font-medium mb-1">Synthesizing Frames... {progress}%</p>
                  <p className="text-xs text-muted-foreground">This may take a few minutes</p>
                </div>
                {/* Progress Bar */}
                <div className="w-48 h-1.5 bg-card rounded-full overflow-hidden mt-2">
                  <div className="h-full bg-accent transition-all duration-300" style={{ width: `${progress}%` }} />
                </div>
              </div>
            ) : errorMsg ? (
               <div className="absolute inset-0 flex items-center justify-center text-red-400 bg-red-500/5">
                 <p>{errorMsg}</p>
               </div>
            ) : outputUrl ? (
               <video src={`http://localhost:8000${outputUrl}`} controls autoPlay loop className="w-full h-full object-contain bg-black" />
            ) : (
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-accent/5 to-background flex items-center justify-center">
                <div className="text-center text-muted-foreground opacity-50">
                  <Video className="w-16 h-16 mx-auto mb-4" />
                  <p>Your generated video will appear here</p>
                </div>
              </div>
            )}
          </div>

          {/* Timeline Editor */}
          <div className="shrink-0 h-48 bg-background border border-border rounded-xl flex flex-col overflow-hidden">
             <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card">
               <span className="text-xs font-bold flex items-center gap-2 uppercase tracking-wider">
                 <Scissors className="w-4 h-4 text-accent" /> Timeline Editor
               </span>
               <div className="text-xs text-muted-foreground">00:00:00 / 00:00:15</div>
             </div>
             <div className="flex-1 p-4 overflow-x-auto overflow-y-hidden flex flex-col gap-2 relative">
               {/* Video Track */}
               <div className="flex items-center gap-2 mb-2 w-max">
                 <div className="w-24 shrink-0 flex items-center gap-2 text-xs font-medium text-muted-foreground">
                   <Video className="w-4 h-4" /> Video 1
                 </div>
                 <div className="h-12 w-[300px] bg-accent/20 border border-accent rounded-md flex items-center px-2 cursor-grab relative group">
                   <GripVertical className="w-4 h-4 text-accent/50 mr-2" />
                   <div className="flex-1 truncate text-xs font-medium text-accent">Scene 1 (Generated)</div>
                   <div className="absolute right-0 top-0 bottom-0 w-2 bg-accent/40 cursor-ew-resize hover:bg-accent transition-colors" />
                   <div className="absolute left-0 top-0 bottom-0 w-2 bg-accent/40 cursor-ew-resize hover:bg-accent transition-colors" />
                 </div>
                 <ChevronRight className="w-4 h-4 text-border" />
                 <div className="h-12 w-[150px] bg-card border border-dashed border-border rounded-md flex items-center justify-center cursor-pointer hover:border-accent/50 transition-colors">
                   <span className="text-xs text-muted-foreground">Add Clip</span>
                 </div>
               </div>

               {/* Audio Track */}
               <div className="flex items-center gap-2 mb-2 w-max">
                 <div className="w-24 shrink-0 flex items-center gap-2 text-xs font-medium text-muted-foreground">
                   <Volume2 className="w-4 h-4" /> Audio
                 </div>
                 <div className="h-8 w-[450px] bg-purple-500/10 border border-purple-500/30 rounded-md flex items-center px-2">
                   <span className="text-[10px] text-purple-400">Cinematic Drone Ambient.mp3</span>
                 </div>
               </div>

               {/* Subtitle Track */}
               <div className="flex items-center gap-2 w-max">
                 <div className="w-24 shrink-0 flex items-center gap-2 text-xs font-medium text-muted-foreground">
                   <Type className="w-4 h-4" /> Subtitles
                 </div>
                 <div className="h-6 w-[200px] bg-orange-500/10 border border-orange-500/30 rounded-md flex items-center px-2 ml-[50px]">
                   <span className="text-[10px] text-orange-400">"The neon city awaits..."</span>
                 </div>
               </div>

               {/* Playhead */}
               <div className="absolute top-0 bottom-0 left-[150px] w-px bg-red-500 z-10 shadow-[0_0_10px_rgba(239,68,68,0.5)]">
                 <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rounded-sm" />
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
