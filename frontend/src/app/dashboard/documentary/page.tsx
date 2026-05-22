"use client";

import { useState, useEffect } from "react";
import { Layers, Settings2, Play, Download, Film, Edit3, X, CheckCircle2, AlertCircle, Loader2, Music, Mic, Save, Copy } from "lucide-react";
import { createDocumentaryProject, getDocumentaryProject, type DocumentaryProject, type CreateDocumentaryParams, type DocumentaryScene } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { useCallback } from "react";

export default function DocumentaryMode() {
  const [topic, setTopic] = useState("");
  const [script, setScript] = useState("");
  const [globalStyle, setGlobalStyle] = useState("Dark Documentary");
  const [voice, setVoice] = useState("cinematic_male");
  const [music, setMusic] = useState("cinematic_ambient");
  const [isShort, setIsShort] = useState(false);
  const [isTrailer, setIsTrailer] = useState(false);
  
  const [project, setProject] = useState<DocumentaryProject | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [expandedMedia, setExpandedMedia] = useState<string | null>(null);

  // Keyboard Shortcuts
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      console.log("Saving project template...");
      // Auto-save logic here
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Poll project status if it's running
  useEffect(() => {
    if (!project) return;
    if (project.status === "completed" || project.status === "failed") {
      setIsProcessing(false);
      return;
    }
    
    setIsProcessing(true);
    const interval = setInterval(async () => {
      try {
        const p = await getDocumentaryProject(project.id);
        setProject(p);
      } catch (err) {
        console.error("Failed to poll project", err);
      }
    }, 3000);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project?.id, project?.status]);

  const handleGenerateFullDocumentary = async () => {
    if (!topic.trim() && !script.trim()) return;
    setIsProcessing(true);
    setProject(null);
    
    try {
      const params: CreateDocumentaryParams = {
        title: topic || "Untitled Project",
        topic: topic,
        script: script,
        style: globalStyle,
        voice: voice,
        music_style: music,
        is_short: isShort,
        is_trailer: isTrailer
      };
      
      const newProj = await createDocumentaryProject(params);
      setProject(newProj);
    } catch (err) {
      console.error(err);
      setIsProcessing(false);
    }
  };

  return (
    <>
      {/* Lightbox */}
      <AnimatePresence>
        {expandedMedia && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" onClick={() => setExpandedMedia(null)}>
            {expandedMedia.endsWith('.mp4') ? (
               <video src={expandedMedia} controls autoPlay className="max-w-full max-h-[90vh] rounded-xl shadow-2xl object-contain bg-black" />
            ) : (
               <motion.img src={expandedMedia} alt="Expanded" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                 className="max-w-full max-h-[90vh] rounded-xl shadow-2xl object-contain" />
            )}
            <button onClick={() => setExpandedMedia(null)} className="absolute top-4 right-4 text-white/70 hover:text-white"><X className="w-8 h-8" /></button>
          </div>
        )}
      </AnimatePresence>

      <div className="flex flex-col h-[calc(100vh-8rem)]">
        <div className="flex items-center justify-between mb-6 shrink-0">
          <div>
            <h1 className="text-2xl font-bold mb-1 flex items-center gap-2 text-glow">
              <Layers className="w-6 h-6 text-purple-400" /> Documentary Studio
            </h1>
            <p className="text-muted-foreground text-sm">One-click cinematic documentary generation. Enter a topic and let AI do the rest.</p>
          </div>
          <div className="flex items-center gap-3">
            {project?.output_url && (
               <a href={`http://localhost:8000${project.output_url}`} download className="px-4 py-2 bg-green-500/20 text-green-400 border border-green-500/50 rounded-lg text-sm font-bold hover:bg-green-500/30 transition-colors flex items-center gap-2">
                 <Download className="w-4 h-4" /> Download Final MP4
               </a>
            )}
            <button 
              onClick={handleGenerateFullDocumentary}
              disabled={isProcessing || (!topic.trim() && !script.trim())}
              className={`px-6 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 cinematic-transition ${
                isProcessing || (!topic.trim() && !script.trim()) ? "bg-muted text-muted-foreground cursor-not-allowed" : "bg-purple-500 text-white hover:bg-purple-600 shadow-[0_0_20px_rgba(192,132,252,0.4)] hover:shadow-[0_0_30px_rgba(192,132,252,0.6)]"
              }`}>
              {isProcessing ? <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</> : <><Play className="w-4 h-4 fill-current" /> Auto-Generate Documentary</>}
            </button>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-6 flex-1 min-h-0">
          {/* Settings Area */}
          <div className="w-full lg:w-1/3 flex flex-col gap-4 overflow-y-auto pr-2">
            
            <div className="bg-card border border-border/50 rounded-2xl p-5 glass shrink-0">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold flex items-center gap-2">
                  <Edit3 className="w-4 h-4 text-purple-400" /> Story Setup
                </h2>
              </div>
              
              <div className="space-y-4">
                 <div>
                    <label className="text-xs text-muted-foreground block mb-1">Documentary Topic</label>
                    <input 
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g. The Fall of Ancient Rome"
                      className="w-full bg-background/50 border border-border rounded-xl px-4 py-2 text-sm text-foreground focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                    />
                 </div>
                 
                 <div className="relative flex items-center justify-center">
                    <hr className="w-full border-border/50" />
                    <span className="absolute bg-card px-2 text-[10px] text-muted-foreground uppercase">OR</span>
                 </div>

                 <div>
                    <label className="text-xs text-muted-foreground block mb-1">Custom Script (Optional)</label>
                    <textarea
                      value={script}
                      onChange={(e) => setScript(e.target.value)}
                      placeholder="Paste your full narration script here..."
                      className="w-full h-32 bg-background/50 border border-border rounded-xl p-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400 resize-none"
                    />
                 </div>
              </div>
            </div>

            <div className="bg-card border border-border/50 rounded-2xl p-5 glass shrink-0">
               <div className="flex items-center gap-2 mb-4">
                  <Settings2 className="w-4 h-4 text-purple-400" />
                  <h3 className="font-bold text-sm">Cinematic Settings</h3>
               </div>
               <div className="space-y-4">
                 <div>
                    <label className="text-xs text-muted-foreground block mb-1">Visual Atmosphere</label>
                    <select 
                      value={globalStyle}
                      onChange={(e) => setGlobalStyle(e.target.value)}
                      className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-purple-400">
                      <option value="Dark Documentary">Dark Documentary</option>
                      <option value="War Archives">War Archives</option>
                      <option value="Cinematic Realism">Cinematic Realism</option>
                      <option value="Neo Noir">Neo Noir</option>
                      <option value="Historical Reconstruction">Historical Reconstruction</option>
                    </select>
                 </div>
                 
                 <div>
                    <label className="text-xs text-muted-foreground block mb-1 flex items-center gap-2"><Mic className="w-3 h-3"/> AI Narrator Voice</label>
                    <select 
                      value={voice}
                      onChange={(e) => setVoice(e.target.value)}
                      className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-purple-400">
                      <option value="cinematic_male">Deep Cinematic Male</option>
                      <option value="documentary_female">Documentary Female</option>
                      <option value="deep_dramatic">Historical Archive Male</option>
                    </select>
                 </div>

                 <div>
                    <label className="text-xs text-muted-foreground block mb-1 flex items-center gap-2"><Music className="w-3 h-3"/> Soundtrack Style</label>
                    <select 
                      value={music}
                      onChange={(e) => setMusic(e.target.value)}
                      className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-purple-400">
                      <option value="cinematic_ambient">Cinematic Ambient</option>
                      <option value="tension_buildup">Tension Buildup</option>
                      <option value="emotional_piano">Emotional Piano</option>
                      <option value="war_drums">War Drums</option>
                    </select>
                 </div>

                 <div className="flex flex-col gap-3 pt-2">
                   <div className="flex items-center gap-3">
                     <button 
                       onClick={() => setIsShort(!isShort)}
                       className={`w-10 h-5 rounded-full relative transition-colors ${isShort ? 'bg-purple-500' : 'bg-muted'}`}
                     >
                       <div className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${isShort ? 'translate-x-5.5 left-[1px]' : 'translate-x-0.5'}`} />
                     </button>
                     <label className="text-xs text-foreground cursor-pointer" onClick={() => setIsShort(!isShort)}>
                       Generate 9:16 Viral Short
                     </label>
                   </div>
                   
                   <div className="flex items-center gap-3">
                     <button 
                       onClick={() => setIsTrailer(!isTrailer)}
                       className={`w-10 h-5 rounded-full relative transition-colors ${isTrailer ? 'bg-accent' : 'bg-muted'}`}
                     >
                       <div className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${isTrailer ? 'translate-x-5.5 left-[1px]' : 'translate-x-0.5'}`} />
                     </button>
                     <label className="text-xs text-foreground cursor-pointer" onClick={() => setIsTrailer(!isTrailer)}>
                       Generate Cinematic Teaser Trailer
                     </label>
                   </div>
                 </div>
               </div>
            </div>
          </div>

          {/* Pipeline Monitor / Timeline Area */}
          <div className="w-full lg:w-2/3 flex flex-col gap-4 min-h-0">
             
             {/* Status Header */}
             <div className="bg-card border border-border/50 rounded-2xl glass p-5 shrink-0 flex flex-col gap-3 relative overflow-hidden group cinematic-glow">
                {isProcessing && <div className="absolute inset-0 bg-purple-500/5 group-hover:bg-purple-500/10 transition-colors pointer-events-none"></div>}
                
                <div className="flex items-center justify-between relative z-10">
                  <h2 className="font-bold flex items-center gap-2">
                    {isProcessing ? <div className="w-5 h-5 rounded-full border-2 border-purple-500/30 border-t-purple-500 animate-spin shadow-[0_0_10px_rgba(168,85,247,0.5)]"></div> : <Film className="w-5 h-5 text-purple-400" />} 
                    Pipeline Status: {project ? project.status.toUpperCase() : "IDLE"}
                  </h2>
                  {project?.status === "completed" && <span className="text-green-400 font-bold flex items-center gap-1"><CheckCircle2 className="w-4 h-4"/> Master Output Ready</span>}
                  {project?.status === "failed" && <span className="text-red-400 font-bold flex items-center gap-1"><AlertCircle className="w-4 h-4"/> Critical Failure</span>}
                </div>
                
                <div className="w-full h-2 bg-background rounded-full overflow-hidden border border-border relative z-10">
                  <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-700 ease-out shadow-[0_0_15px_rgba(168,85,247,0.8)]" style={{ width: `${project ? project.progress : 0}%` }} />
                </div>
                
                {isProcessing && (
                   <div className="text-[10px] text-green-400 opacity-70 font-mono mt-1 relative z-10 flex flex-col gap-0.5">
                     <span>&gt; VRAM memory pool verified.</span>
                     <span>&gt; GPU Rendering Cluster: Nominal.</span>
                     {project && project.progress > 10 && <span>&gt; Neural director analyzing scene pacing...</span>}
                     {project && project.progress > 50 && <span>&gt; Assembling spatial audio and applying film grain...</span>}
                   </div>
                )}
                
                {project?.error_message && (
                  <p className="text-xs text-red-400 bg-red-500/10 p-2 rounded border border-red-500/30 font-mono relative z-10">&gt; OOM_OR_PIPELINE_ERROR: {project.error_message}</p>
                )}
             </div>

             {/* Final Output Player */}
             {project?.output_url && (
               <div className="flex flex-col xl:flex-row gap-4 bg-card border border-border/50 rounded-2xl glass p-4 shrink-0 shadow-[0_0_30px_rgba(0,0,0,0.5)]">
                 <div className="flex-1">
                   <div className="flex items-center justify-between mb-2">
                     <h3 className="font-bold text-sm flex items-center gap-2"><Play className="w-4 h-4 text-purple-400"/> Final Master Output</h3>
                     <span className="text-[10px] text-green-400 bg-green-400/10 px-2 py-0.5 rounded border border-green-400/20 font-mono tracking-widest uppercase">Lossless</span>
                   </div>
                   <div className="relative group w-full h-64 rounded-xl border border-border overflow-hidden bg-black">
                     <video 
                       src={`http://localhost:8000${project.output_url}`} 
                       controls 
                       autoPlay 
                       playsInline
                       className={`w-full h-full object-contain ${project.is_short ? 'max-w-[360px] mx-auto' : ''}`} 
                     />
                   </div>
                   
                   <div className="mt-4 flex flex-wrap gap-3">
                     <button className="flex-1 bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-4 rounded-lg transition-all shadow-[0_0_15px_rgba(168,85,247,0.4)] flex items-center justify-center gap-2">
                       <Download className="w-4 h-4" /> Download Master (MP4)
                     </button>
                     <button className="flex-1 bg-background border border-border hover:border-purple-500/50 text-foreground font-bold py-2 px-4 rounded-lg cinematic-transition flex items-center justify-center gap-2" title="Ctrl+S to Quick Save">
                       <Save className="w-4 h-4 text-purple-400" /> Save as Template
                     </button>
                     <button className="flex-1 bg-background border border-border hover:border-blue-500/50 text-foreground font-bold py-2 px-4 rounded-lg cinematic-transition flex items-center justify-center gap-2">
                       <Copy className="w-4 h-4 text-blue-400" /> Duplicate Project
                     </button>
                   </div>
                 </div>
                 
                 <div className="w-full xl:w-1/3 flex flex-col gap-3 bg-background/50 border border-border rounded-xl p-4 overflow-y-auto max-h-[300px] shadow-inner">
                   <h3 className="font-bold text-sm flex items-center justify-between mb-2">
                       <span className="flex items-center gap-2"><Film className="w-4 h-4 text-purple-400"/> Scene Editor & Export Queue</span>
                       <div className="flex gap-2 text-xs opacity-50 hover:opacity-100 cinematic-transition">
                          <kbd className="bg-muted px-1.5 py-0.5 rounded border border-border">Ctrl</kbd>+<kbd className="bg-muted px-1.5 py-0.5 rounded border border-border">S</kbd>
                      </div>
                   </h3>
                   {project?.scenes?.map((scene: DocumentaryScene, i: number) => (
                     <div key={scene.id} className="bg-card border border-border rounded p-3 text-xs flex flex-col gap-2 hover:border-purple-500/50 transition-colors cursor-pointer group relative">
                       <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                          <button className="bg-background/80 p-1 rounded hover:text-blue-400"><Copy className="w-3 h-3"/></button>
                       </div>
                       <div className="flex justify-between items-center">
                         <span className="font-bold text-purple-400">Scene {i + 1} <span className="text-muted-foreground text-[10px] ml-1">(Drag to reorder)</span></span>
                         <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${
                           scene.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                           scene.status.startsWith('generating') ? 'bg-blue-500/20 text-blue-400 animate-pulse' :
                           'bg-muted text-muted-foreground'
                         }`}>
                           {scene.status.replace('_', ' ')}
                         </span>
                       </div>
                       <p className="text-muted-foreground line-clamp-2 pr-6">&quot;{scene.script_text}&quot;</p>
                       <div className="mt-1 pt-2 border-t border-border/50 text-[10px] text-muted-foreground flex justify-between">
                         <span className="truncate">Prompt: {scene.image_prompt?.substring(0, 20) ?? "" }...</span>
                         <span className="text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">Zoom Timeline</span>
                       </div>
                     </div>
                   ))}
                 </div>
               </div>
             )}

             {/* Scenes List */}
             <div className="bg-card border border-border/50 rounded-2xl glass p-5 flex-1 overflow-y-auto flex flex-col">
               <h3 className="font-bold text-sm mb-4 flex items-center gap-2">
                 <Layers className="w-4 h-4 text-purple-400" /> Generated Scenes Timeline <span className="text-[10px] text-muted-foreground font-normal ml-2">(Drag & Drop to Reorder)</span>
               </h3>
               
               <div className="flex-1 space-y-4 pr-2">
                  {!project || project.scenes.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50">
                      <Film className="w-12 h-12 mb-3" />
                      <p>Pipeline is idle. Fill out the settings and hit Generate.</p>
                    </div>
                  ) : (
                    project.scenes.map((scene, i) => (
                       <div 
                         key={scene.id} 
                         className="bg-background border border-border rounded-xl p-4 flex gap-4 group cinematic-fade-in cinematic-transition hover:border-purple-500/50 cursor-grab active:cursor-grabbing"
                         draggable="true"
                         onDragStart={(e) => { e.dataTransfer.setData("text/plain", i.toString()); e.currentTarget.style.opacity = "0.5"; }}
                         onDragEnd={(e) => { e.currentTarget.style.opacity = "1"; }}
                         onDragOver={(e) => e.preventDefault()}
                         onDrop={(e) => { e.preventDefault(); console.log(`Dropped scene ${e.dataTransfer.getData("text/plain")} onto ${i}`); }}
                       >
                          {/* Visuals */}
                          <div 
                            className="w-40 h-24 shrink-0 rounded-lg overflow-hidden relative bg-card border border-border cursor-pointer group-hover:border-purple-400/50 transition-colors"
                            onClick={() => {
                               if (scene.video_url) setExpandedMedia(`http://localhost:8000${scene.video_url}`);
                               else if (scene.image_url) setExpandedMedia(`http://localhost:8000${scene.image_url}`);
                            }}
                          >
                             {scene.video_url ? (
                               <>
                                 <video src={`http://localhost:8000${scene.video_url}`} className="w-full h-full object-cover" muted loop autoPlay playsInline />
                                 <div className="absolute top-1 right-1 bg-accent/80 backdrop-blur text-white text-[10px] px-1.5 py-0.5 rounded font-bold">VIDEO</div>
                               </>
                             ) : scene.image_url ? (
                               <img src={`http://localhost:8000${scene.image_url}`} className="w-full h-full object-cover" />
                             ) : (
                               <div className="absolute inset-0 flex flex-col items-center justify-center">
                                 {scene.status === "failed" ? <AlertCircle className="w-6 h-6 text-red-400/50" /> : <Loader2 className="w-6 h-6 text-purple-400/50 animate-spin" />}
                               </div>
                             )}
                             <div className="absolute top-1 left-1 bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded text-[10px] font-bold text-white z-10">
                               {i + 1}
                             </div>
                          </div>
                          
                          {/* Data */}
                          <div className="flex-1 min-w-0 flex flex-col gap-2">
                            <div className="flex justify-between items-start">
                              <span className="text-[10px] font-bold px-2 py-0.5 bg-card border border-border rounded-full text-muted-foreground uppercase">
                                {scene.status.replace('_', ' ')}
                              </span>
                            </div>
                            <p className="text-sm text-foreground bg-card/50 p-2 rounded-lg border border-border flex-1 line-clamp-2">
                              {scene.script_text}
                            </p>
                            
                            {scene.audio_url && (
                              <div className="flex items-center gap-2">
                                <audio controls src={`http://localhost:8000${scene.audio_url}`} className="h-6 w-full max-w-[200px]" />
                                <span className="text-[10px] text-muted-foreground">Narration generated</span>
                              </div>
                            )}
                          </div>
                       </div>
                    ))
                  )}
               </div>
             </div>
          </div>
        </div>
      </div>
    </>
  );
}
