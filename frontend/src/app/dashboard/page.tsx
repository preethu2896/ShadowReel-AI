"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowRight, ImageIcon, Video, Layers, TrendingUp, Clock, Star, Activity, HardDrive, Cpu, Film, Share2 } from "lucide-react";
import Link from "next/link";
import { getGenerationHistory, JobStatusResponse, getSystemStats, SystemStatsResponse } from "@/lib/api";

export default function DashboardOverview() {
  const [recentRenders, setRecentRenders] = useState<JobStatusResponse[]>([]);
  const [stats, setStats] = useState<SystemStatsResponse | null>(null);
  
  useEffect(() => {
    // Load real render stats and system stats
    getGenerationHistory(4).then(data => setRecentRenders(data)).catch(console.error);
    getSystemStats().then(data => setStats(data)).catch(console.error);
  }, []);

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 pb-10">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className="flex items-center justify-between mb-8">
          <div>
             <h1 className="text-3xl font-bold mb-2">Filmmaker Command Center</h1>
             <p className="text-muted-foreground">ShadowReel AI Enterprise • Cinematic Production OS.</p>
          </div>
          <div className="flex items-center gap-3">
             <div className="bg-purple-500/10 border border-purple-500/30 text-purple-400 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-2">
                <Star className="w-4 h-4"/> Enterprise Plan
             </div>
             <div className="bg-card border border-border px-3 py-1.5 rounded-lg text-sm flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Team: Editors Group A
             </div>
          </div>
        </div>

        {/* Top Analytics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="p-5 rounded-2xl glass border border-border/50 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm font-medium">{stats?.hardware.vram.type ?? "GPU VRAM"} Load</span>
              <Cpu className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-glow-purple">{stats?.hardware.vram.used_gb ?? 0} GB <span className="text-sm font-normal text-muted-foreground">/ {stats?.hardware.vram.total_gb ?? 0} GB</span></div>
            <div className="mt-auto pt-4 w-full bg-background rounded-full h-1.5 overflow-hidden border border-border">
              <div className="bg-purple-400 h-full shadow-[0_0_10px_rgba(192,132,252,0.8)]" style={{ width: `${stats ? (stats.hardware.vram.used_gb / (stats.hardware.vram.total_gb || 1)) * 100 : 0}%` }}></div>
            </div>
          </div>
          
          <div className="p-5 rounded-2xl glass border border-border/50 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm font-medium">Render Queue</span>
              <Activity className="w-4 h-4 text-accent" />
            </div>
            <div className="text-2xl font-bold text-glow-blue">{stats?.queue.active_jobs ?? 0} <span className="text-sm font-normal text-muted-foreground">Active Jobs</span></div>
            <div className="mt-auto pt-4 w-full bg-background rounded-full h-1.5 overflow-hidden border border-border">
              <div className="bg-accent h-full shadow-[0_0_10px_rgba(59,130,246,0.8)] animate-pulse" style={{ width: stats?.queue.active_jobs ? '100%' : '0%' }}></div>
            </div>
          </div>
          
          <div className="p-5 rounded-2xl glass border border-border/50 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm font-medium">Storage Used</span>
              <HardDrive className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-bold">{stats?.hardware.storage.used_gb ?? 0} GB <span className="text-sm font-normal text-muted-foreground">/ {stats?.hardware.storage.total_gb ?? 0} GB</span></div>
            <div className="mt-auto pt-4 w-full bg-background rounded-full h-1.5 overflow-hidden border border-border">
              <div className="bg-primary h-full" style={{ width: `${stats ? (stats.hardware.storage.used_gb / (stats.hardware.storage.total_gb || 1)) * 100 : 0}%` }}></div>
            </div>
          </div>

          <div className="p-5 rounded-2xl glass border border-border/50 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm font-medium">Total Renders</span>
              <TrendingUp className="w-4 h-4 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-green-400">{(stats?.analytics.failed_jobs ?? 0) + (recentRenders.length > 0 ? 1 : 0)} <span className="text-sm font-normal text-muted-foreground">All Time</span></div>
            <div className="mt-auto pt-4 text-xs text-muted-foreground">Platform growing steady.</div>
          </div>
        </div>

        {/* Quick Actions Ecosystem */}
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Star className="w-5 h-5 text-yellow-400" /> Creator Ecosystem
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Link href="/dashboard/documentary">
            <div className="p-5 rounded-2xl glass border border-purple-500/30 hover:border-purple-400 transition-all hover:box-glow-purple group cursor-pointer h-full bg-purple-500/5">
              <div className="w-10 h-10 rounded-lg bg-purple-400/20 flex items-center justify-center mb-3">
                <Layers className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="font-bold mb-1">Doc Studio</h3>
              <p className="text-xs text-muted-foreground mb-3">Auto-generate cinematic docs.</p>
            </div>
          </Link>
          
          <Link href="/dashboard/generate-video">
            <div className="p-5 rounded-2xl glass border border-accent/30 hover:border-accent transition-all hover:shadow-[0_0_20px_rgba(37,99,235,0.2)] group cursor-pointer h-full bg-accent/5">
              <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center mb-3">
                <Video className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-bold mb-1">Video Engine</h3>
              <p className="text-xs text-muted-foreground mb-3">Wan2.1 & SVD dynamic scenes.</p>
            </div>
          </Link>

          <Link href="/dashboard/generate-image">
            <div className="p-5 rounded-2xl glass border border-primary/30 hover:border-primary transition-all hover:box-glow group cursor-pointer h-full bg-primary/5">
              <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center mb-3">
                <ImageIcon className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-bold mb-1">Thumbnail Maker</h3>
              <p className="text-xs text-muted-foreground mb-3">Generate high-CTR YouTube thumbnails.</p>
            </div>
          </Link>
          
          <Link href="/dashboard/documentary">
            <div className="p-5 rounded-2xl glass border border-green-500/30 hover:border-green-400 transition-all hover:shadow-[0_0_20px_rgba(74,222,128,0.2)] group cursor-pointer h-full bg-green-500/5">
              <div className="w-10 h-10 rounded-lg bg-green-400/20 flex items-center justify-center mb-3">
                <Share2 className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="font-bold mb-1">Viral Shorts</h3>
              <p className="text-xs text-muted-foreground mb-3">Convert docs to 9:16 vertical reels.</p>
            </div>
          </Link>
        </div>

        {/* Dashboard Activity Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-muted-foreground" /> Project Activity Feed
            </h2>
            <div className="bg-card border border-border rounded-xl overflow-hidden glass">
              <div className="divide-y divide-border/50">
                {recentRenders.length === 0 ? (
                   <div className="p-6 text-center text-muted-foreground">No recent activity</div>
                ) : recentRenders.map((render) => (
                  <div key={render.job_id} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        render.job_type === 'video' ? 'bg-accent/10 text-accent' : 
                        render.job_type === 'image' ? 'bg-primary/10 text-primary' : 'bg-purple-400/10 text-purple-400'
                      }`}>
                        {render.job_type === 'video' ? <Film className="w-5 h-5" /> : 
                         render.job_type === 'image' ? <ImageIcon className="w-5 h-5" /> : <Layers className="w-5 h-5" />}
                      </div>
                      <div>
                        <h4 className="font-medium text-sm line-clamp-1">{render.prompt || "Documentary Master Render"}</h4>
                        <span className="text-xs text-muted-foreground uppercase">{render.job_type} • {render.model || 'Pipeline'}</span>
                      </div>
                    </div>
                    <div className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                      render.status === 'completed' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 
                      render.status === 'failed' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                      'bg-orange-500/10 text-orange-500 border-orange-500/20 animate-pulse'
                    }`}>
                      {render.status}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-muted-foreground" /> Retention Analytics
            </h2>
            <div className="bg-card border border-border rounded-xl p-6 glass h-full">
               <div className="flex flex-col h-full">
                  <p className="text-sm text-muted-foreground mb-4">Latest Project: The Fall of Rome</p>
                  
                  <div className="space-y-5 flex-1">
                     <div>
                        <div className="flex justify-between text-xs mb-1">
                           <span className="text-white font-bold">Hook Strength</span>
                           <span className="text-green-400">92%</span>
                        </div>
                        <div className="w-full bg-background rounded-full h-1 overflow-hidden">
                           <div className="bg-green-400 h-full shadow-[0_0_8px_rgba(74,222,128,0.8)]" style={{ width: '92%' }}></div>
                        </div>
                     </div>
                     <div>
                        <div className="flex justify-between text-xs mb-1">
                           <span className="text-white font-bold">Pacing Intensity</span>
                           <span className="text-yellow-400">78%</span>
                        </div>
                        <div className="w-full bg-background rounded-full h-1 overflow-hidden">
                           <div className="bg-yellow-400 h-full shadow-[0_0_8px_rgba(250,204,21,0.8)]" style={{ width: '78%' }}></div>
                        </div>
                     </div>
                     <div>
                        <div className="flex justify-between text-xs mb-1">
                           <span className="text-white font-bold">Visual Variation</span>
                           <span className="text-accent">85%</span>
                        </div>
                        <div className="w-full bg-background rounded-full h-1 overflow-hidden">
                           <div className="bg-accent h-full shadow-[0_0_8px_rgba(59,130,246,0.8)]" style={{ width: '85%' }}></div>
                        </div>
                     </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-border/50">
                     <p className="text-xs text-muted-foreground flex items-center gap-2"><ArrowRight className="w-3 h-3"/> Editor Agent: Increase tension buildup around chapter 2.</p>
                     <p className="text-xs text-muted-foreground flex items-center gap-2 mt-2"><ArrowRight className="w-3 h-3"/> Cinematographer Agent: Drone shot suggested for intro.</p>
                  </div>
               </div>
            </div>
          </div>
        </div>
        
        {/* Enterprise Multi-Agent System & Neural Map */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
           <div className="bg-card border border-border rounded-xl glass p-6 relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/5 to-blue-500/5 group-hover:opacity-100 opacity-50 transition-opacity"></div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2 relative z-10">
                 <Cpu className="w-5 h-5 text-purple-400" /> Collaborative AI Film Crew
              </h2>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-3 relative z-10">
                 {['Director', 'Cinematographer', 'Editor', 'Sound', 'Color'].map(agent => (
                    <div key={agent} className="bg-background/80 backdrop-blur-sm border border-border p-3 rounded-lg text-center flex flex-col items-center shadow-[0_0_15px_rgba(168,85,247,0.1)] hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] transition-all">
                       <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center mb-2 border border-purple-500/30">
                          <Activity className="w-4 h-4 text-purple-400" />
                       </div>
                       <span className="text-xs font-bold">{agent}</span>
                       <span className="text-[9px] text-green-400 mt-1 uppercase tracking-widest">Active</span>
                    </div>
                 ))}
              </div>
           </div>

           <div className="bg-card border border-border rounded-xl glass p-6 relative overflow-hidden group">
              <div className="absolute inset-0 bg-blue-500/5 group-hover:bg-blue-500/10 transition-colors"></div>
              
              {/* Reactive Particle Canvas Mock */}
              <div className="absolute inset-0 opacity-20 pointer-events-none">
                 <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-500 rounded-full blur-[80px] animate-pulse"></div>
                 <div className="absolute bottom-1/4 right-1/4 w-40 h-40 bg-purple-500 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>
              </div>

              <h2 className="text-xl font-bold mb-4 flex items-center gap-2 relative z-10">
                 <Activity className="w-5 h-5 text-blue-400" /> AI Consciousness Topology
              </h2>
              <div className="h-40 flex items-center justify-between px-4 relative z-10">
                 {/* Evolving Workflow Path */}
                 <div className="absolute left-8 right-8 top-1/2 h-0.5 bg-border -translate-y-1/2"></div>
                 <div className="absolute left-8 right-8 top-1/2 h-0.5 bg-gradient-to-r from-green-400 via-blue-500 to-transparent shadow-[0_0_15px_rgba(59,130,246,0.8)] -translate-y-1/2 animate-pulse" style={{ width: '75%' }}></div>
                 
                 {[
                    {name: "Foundation DB", status: "done", icon: "🧠"}, 
                    {name: "World Engine", status: "done", icon: "🌍"}, 
                    {name: "Auto-Director", status: "active", icon: "🎬"}, 
                    {name: "Self-Learning", status: "active", icon: "🔄"},
                    {name: "Mastering", status: "wait", icon: "🎛️"}
                 ].map((node, i) => (
                    <div key={i} className="relative z-10 flex flex-col items-center gap-3">
                       <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center bg-background/90 backdrop-blur-md transition-all duration-1000 ${
                          node.status === 'done' ? 'border-green-400 shadow-[0_0_15px_rgba(74,222,128,0.4)] text-green-400' :
                          node.status === 'active' ? 'border-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.9)] scale-110 text-blue-400' :
                          'border-border/50 text-muted-foreground'
                       }`}>
                          {node.icon}
                       </div>
                       <span className={`text-[9px] uppercase tracking-widest font-bold text-center w-16 ${
                          node.status === 'active' ? 'text-blue-400' : 'text-muted-foreground'
                       }`}>{node.name}</span>
                    </div>
                 ))}
              </div>
              <div className="mt-4 pt-3 border-t border-border/30 relative z-10 flex justify-between items-center text-xs text-muted-foreground">
                 <span>Self-Improvement: <strong className="text-green-400">Active</strong></span>
                 <span>Retention Predictor: <strong className="text-blue-400">Analyzing</strong></span>
              </div>
           </div>
        </div>

        {/* Creator Analytics Dashboard */}
        <div className="bg-card border border-border rounded-xl glass p-6 mb-4 overflow-hidden relative group">
           <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent"></div>
           <h2 className="text-xl font-bold mb-4 flex items-center gap-2 relative z-10">
              <Activity className="w-5 h-5 text-green-400" /> Creator Production Analytics
           </h2>
           <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
              <div className="bg-background/80 backdrop-blur border border-border p-4 rounded-xl shadow-lg">
                 <div className="text-sm text-muted-foreground mb-1">Render Reliability</div>
                 <div className="text-2xl font-black text-green-400 flex items-end gap-1">{stats?.analytics.reliability_percent ?? 100}<span className="text-sm font-normal">%</span></div>
                 <div className="text-xs text-muted-foreground mt-2 border-t border-border/50 pt-2 flex justify-between">
                    <span>Failed Jobs:</span> <span className="font-bold">{stats?.analytics.failed_jobs ?? 0}</span>
                 </div>
              </div>
              
              <div className="bg-background/80 backdrop-blur border border-border p-4 rounded-xl shadow-lg">
                 <div className="text-sm text-muted-foreground mb-1">Avg Export Time</div>
                 <div className="text-2xl font-black text-blue-400 flex items-end gap-1">{stats?.analytics.avg_export_time_minutes ?? 0}<span className="text-sm font-normal">m</span></div>
                 <div className="text-xs text-muted-foreground mt-2 border-t border-border/50 pt-2 flex justify-between">
                    <span>VRAM Efficiency:</span> <span className="font-bold text-green-400">High</span>
                 </div>
              </div>

              <div className="bg-background/80 backdrop-blur border border-border p-4 rounded-xl shadow-lg">
                 <div className="text-sm text-muted-foreground mb-1">Predicted Retention</div>
                 <div className="text-2xl font-black text-purple-400 flex items-end gap-1">76<span className="text-sm font-normal">%</span></div>
                 <div className="text-xs text-muted-foreground mt-2 border-t border-border/50 pt-2 flex justify-between">
                    <span>Pacing Score:</span> <span className="font-bold">A-</span>
                 </div>
              </div>
              
              <div className="bg-background/80 backdrop-blur border border-border p-4 rounded-xl shadow-lg">
                 <div className="text-sm text-muted-foreground mb-1">Creator Templates</div>
                 <div className="text-2xl font-black text-orange-400 flex items-end gap-1">12</div>
                 <div className="text-xs text-muted-foreground mt-2 border-t border-border/50 pt-2 flex justify-between">
                    <span>Reusable Workflows</span>
                 </div>
              </div>
           </div>
        </div>
      </motion.div>
    </div>
  );
}
