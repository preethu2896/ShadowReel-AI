"use client";

import { useState, useEffect, useCallback } from "react";
import {
  History, Search, Filter, Maximize, Download, Heart, Share2,
  Image as ImageIcon, RefreshCw, AlertCircle, X, CheckCircle2, Clock,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getGenerationHistory, resolveImageUrl,
  type JobStatusResponse,
} from "@/lib/api";

const TABS = ["All", "Completed", "Processing", "Failed"];

function statusIcon(status: string) {
  if (status === "completed") return <CheckCircle2 className="w-3 h-3 text-green-400" />;
  if (status === "failed") return <AlertCircle className="w-3 h-3 text-red-400" />;
  return <Clock className="w-3 h-3 text-yellow-400" />;
}

export default function Gallery() {
  const [activeTab, setActiveTab] = useState("All");
  const [search, setSearch] = useState("");
  const [items, setItems] = useState<JobStatusResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedImage, setExpandedImage] = useState<string | null>(null);
  const [liked, setLiked] = useState<Set<string>>(new Set());

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getGenerationHistory(50);
      setItems(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load gallery");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = items.filter((item) => {
    const matchTab =
      activeTab === "All" ? true :
      activeTab === "Completed" ? item.status === "completed" :
      activeTab === "Processing" ? (item.status === "processing" || item.status === "queued") :
      item.status === "failed";
    const matchSearch = !search || item.prompt?.toLowerCase().includes(search.toLowerCase());
    return matchTab && matchSearch;
  });

  const toggleLike = (id: string) =>
    setLiked((prev) => { const s = new Set(prev); if (s.has(id)) { s.delete(id); } else { s.add(id); } return s; });

  return (
    <>
      {/* Lightbox */}
      <AnimatePresence>
        {expandedImage && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" onClick={() => setExpandedImage(null)}>
            {expandedImage.endsWith('.mp4') ? (
              <video src={expandedImage} controls autoPlay loop className="max-w-full max-h-[90vh] rounded-xl shadow-2xl object-contain bg-black" />
            ) : (
              <motion.img src={expandedImage} alt="Generated" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                className="max-w-full max-h-[90vh] rounded-xl shadow-2xl object-contain" />
            )}
            <button onClick={() => setExpandedImage(null)} className="absolute top-4 right-4 text-white/70 hover:text-white"><X className="w-8 h-8" /></button>
          </div>
        )}
      </AnimatePresence>

      <div className="flex flex-col h-[calc(100vh-8rem)]">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 shrink-0">
          <div>
            <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
              <History className="w-6 h-6 text-foreground" /> Generation History
            </h1>
            <p className="text-muted-foreground text-sm">{items.length} total generations — stored locally</p>
          </div>
          <button onClick={load} className="p-2 bg-card border border-border rounded-lg text-muted-foreground hover:text-foreground transition-colors" title="Refresh">
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6 shrink-0 bg-card p-4 rounded-xl border border-border/50 glass">
          <div className="flex items-center gap-2 w-full md:w-auto flex-wrap">
            {TABS.map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${activeTab === tab ? "bg-foreground text-background" : "bg-background border border-border text-muted-foreground hover:text-foreground"}`}>
                {tab}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative w-full md:w-64">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                placeholder="Search prompts…"
                className="w-full bg-background border border-border rounded-lg pl-9 pr-3 py-1.5 text-sm focus:outline-none focus:border-primary" />
            </div>
            <button className="p-2 bg-background border border-border rounded-lg text-muted-foreground hover:text-foreground">
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 mb-4">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {/* Grid */}
        <div className="flex-1 overflow-y-auto pr-1 pb-10">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="aspect-[4/5] bg-card border border-border rounded-xl animate-pulse" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-muted-foreground">
              <ImageIcon className="w-14 h-14 opacity-15 mb-4" />
              <p className="text-base font-medium">No generations yet</p>
              <p className="text-sm mt-1 opacity-60">Start generating images to fill your gallery</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map((item, idx) => {
                const imgUrl = item.output_url ? resolveImageUrl(item.output_url) : null;
                const isLiked = liked.has(item.job_id);
                return (
                  <motion.div key={item.job_id}
                    initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.04 }}
                    className="group relative aspect-[4/5] bg-background border border-border rounded-xl overflow-hidden hover:border-primary/40 transition-colors">

                    {imgUrl ? (
                      imgUrl.endsWith('.mp4') ? (
                        <video src={imgUrl} autoPlay loop muted playsInline className="w-full h-full object-cover bg-black" />
                      ) : (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={imgUrl} alt={item.prompt ?? ""} className="w-full h-full object-cover" />
                      )
                    ) : (
                      <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground bg-card">
                        {item.status === "failed"
                          ? <AlertCircle className="w-8 h-8 text-red-400/50" />
                          : <ImageIcon className="w-8 h-8 opacity-20" />}
                        <span className="text-xs mt-2 opacity-50 capitalize">{item.status}</span>
                      </div>
                    )}

                    {/* Status badges */}
                    <div className="absolute top-3 left-3 flex flex-col gap-1.5">
                      <span className="flex items-center gap-1 w-max px-2 py-0.5 rounded text-[10px] font-bold text-white bg-black/60 backdrop-blur-md border border-white/10">
                        {statusIcon(item.status)}{item.style ?? "—"}
                      </span>
                      {imgUrl?.endsWith('.mp4') && (
                        <span className="flex items-center gap-1 w-max px-2 py-0.5 rounded text-[10px] font-bold text-accent bg-accent/20 backdrop-blur-md border border-accent/50">
                          Video
                        </span>
                      )}
                    </div>

                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4 backdrop-blur-[2px]">
                      <div className="absolute top-3 right-3 flex flex-col gap-2">
                        <button onClick={() => toggleLike(item.job_id)}
                          className={`p-2 rounded-lg text-white transition-colors backdrop-blur-md border border-white/10 ${isLiked ? "bg-red-500/70" : "bg-white/10 hover:bg-white/20"}`}>
                          <Heart className={`w-4 h-4 ${isLiked ? "fill-white" : ""}`} />
                        </button>
                        {imgUrl && (
                          <button onClick={() => { navigator.clipboard.writeText(imgUrl); }}
                            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors backdrop-blur-md border border-white/10">
                            <Share2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>

                      <p className="text-white/70 text-[10px] mb-1 uppercase tracking-wider">{item.model?.toUpperCase()} • {item.status}</p>
                      <h3 className="text-white font-semibold text-sm line-clamp-2 mb-3">{item.prompt}</h3>
                      <div className="flex gap-2">
                        {imgUrl && (
                          <>
                            <button onClick={() => setExpandedImage(imgUrl)}
                              className="flex-1 py-2 bg-white text-black text-xs font-bold rounded-lg flex items-center justify-center gap-2 hover:bg-white/90 transition-colors">
                              <Maximize className="w-3 h-3" /> View
                            </button>
                            <a href={imgUrl} download className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white backdrop-blur-md border border-white/10">
                              <Download className="w-4 h-4" />
                            </a>
                          </>
                        )}
                      </div>
                      {item.created_at && (
                        <p className="text-white/40 text-[10px] mt-2">{new Date(item.created_at).toLocaleString()}</p>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
