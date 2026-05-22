"use client";

import { motion } from "framer-motion";
import { Play, Sparkles, Film, Video, Layers, Wand2, Zap, LayoutDashboard, Settings } from "lucide-react";
import Link from "next/link";

export default function Home() {


  const features = [
    {
      icon: <Sparkles className="w-6 h-6 text-primary" />,
      title: "AI Image Generation",
      description: "Generate hyper-realistic cinematic stills with advanced prompt adherence and style presets.",
    },
    {
      icon: <Video className="w-6 h-6 text-accent" />,
      title: "AI Video Generation",
      description: "Transform text or images into fluid, dramatic video sequences with precise camera control.",
    },
    {
      icon: <Layers className="w-6 h-6 text-purple-400" />,
      title: "Documentary Mode",
      description: "Multi-scene storyboard generation with auto-scene splitting and cinematic pacing.",
    },
  ];

  return (
    <div className="min-h-screen bg-background overflow-hidden selection:bg-primary/30">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-accent/5 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[100px] mix-blend-screen" />
      </div>

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border/50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-primary to-accent flex items-center justify-center">
              <Film className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight">ShadowReel<span className="text-primary">.ai</span></span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <Link href="#features" className="hover:text-foreground transition-colors">Features</Link>
            <Link href="#workflow" className="hover:text-foreground transition-colors">Workflow</Link>
            <Link href="#pricing" className="hover:text-foreground transition-colors">Pricing</Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Log in</Link>
            <Link href="/dashboard" className="text-sm font-medium bg-foreground text-background px-4 py-2 rounded-md hover:bg-foreground/90 transition-all flex items-center gap-2">
              <Wand2 className="w-4 h-4" /> Start Creating
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-48 pb-32 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/20 bg-primary/10 text-primary text-xs font-medium mb-8">
              <Sparkles className="w-3 h-3" />
              <span>Wan2.1 & Flux Pro Integration Live</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-tight">
              Generate cinematic worlds <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-purple-400 to-accent">
                with AI precision
              </span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
              The ultimate AI SaaS platform for cinematic image and video generation. 
              Built for directors, creators, and storytellers who demand production-grade quality.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/dashboard" className="w-full sm:w-auto px-8 py-4 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-all box-glow flex items-center justify-center gap-2">
                <Play className="w-5 h-5 fill-current" />
                Launch Studio
              </Link>
              <Link href="#demo" className="w-full sm:w-auto px-8 py-4 glass text-foreground rounded-lg font-medium hover:bg-white/5 transition-all border border-border flex items-center justify-center gap-2">
                Watch Showreel
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="relative z-10 py-32 px-6 bg-card/50 border-y border-border/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Production-grade toolset</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">Everything you need to conceptualize, generate, and finalize cinematic content.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                className="p-8 rounded-2xl glass border border-border/50 hover:border-primary/50 transition-all duration-300 relative group overflow-hidden"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
              >
                <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10">
                  <div className="w-12 h-12 rounded-xl bg-background flex items-center justify-center mb-6 border border-border">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 py-12 px-6 bg-background">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Film className="w-5 h-5 text-primary" />
            <span className="font-bold tracking-tight">ShadowReel<span className="text-primary">.ai</span></span>
          </div>
          <p className="text-sm text-muted-foreground">© 2026 ShadowReel AI. Built for the cinematic future.</p>
          <div className="flex gap-4">
            <Link href="#" className="text-muted-foreground hover:text-foreground"><Zap className="w-5 h-5" /></Link>
            <Link href="#" className="text-muted-foreground hover:text-foreground"><LayoutDashboard className="w-5 h-5" /></Link>
            <Link href="#" className="text-muted-foreground hover:text-foreground"><Settings className="w-5 h-5" /></Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
