import Link from "next/link";
import { Film, Image as ImageIcon, Video, Layers, LayoutDashboard, History, Sparkles, Settings, CreditCard, LogOut } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const navItems = [
    { name: "Overview", href: "/dashboard", icon: <LayoutDashboard className="w-5 h-5" /> },
    { name: "Image Studio", href: "/dashboard/generate-image", icon: <ImageIcon className="w-5 h-5" /> },
    { name: "Video Studio", href: "/dashboard/generate-video", icon: <Video className="w-5 h-5" /> },
    { name: "Documentary", href: "/dashboard/documentary", icon: <Layers className="w-5 h-5" /> },
    { name: "Gallery", href: "/dashboard/gallery", icon: <History className="w-5 h-5" /> },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden selection:bg-primary/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border/50 glass flex flex-col hidden md:flex">
        <div className="h-20 flex items-center px-6 border-b border-border/50">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-primary to-accent flex items-center justify-center">
              <Film className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight">ShadowReel<span className="text-primary">.ai</span></span>
          </Link>
        </div>
        
        <div className="flex-1 overflow-y-auto py-6 px-4 flex flex-col gap-2">
          <div className="px-2 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Studios</div>
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all group"
            >
              <span className="group-hover:text-primary transition-colors">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </Link>
          ))}
          
          <div className="px-2 mt-8 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Account</div>
          <Link href="/dashboard/settings" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all group">
            <Settings className="w-5 h-5 group-hover:text-primary transition-colors" />
            <span className="font-medium">Settings</span>
          </Link>
          <Link href="/dashboard/billing" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all group">
            <CreditCard className="w-5 h-5 group-hover:text-primary transition-colors" />
            <span className="font-medium">Billing</span>
          </Link>
        </div>

        {/* Credit System UI */}
        <div className="p-4 border-t border-border/50">
          <div className="bg-card p-4 rounded-xl border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Credits</span>
              <Sparkles className="w-4 h-4 text-primary" />
            </div>
            <div className="w-full bg-background rounded-full h-2 mb-2 overflow-hidden border border-border">
              <div className="bg-gradient-to-r from-primary to-accent h-2 rounded-full" style={{ width: '65%' }}></div>
            </div>
            <div className="text-xs text-muted-foreground flex justify-between">
              <span>650 / 1000</span>
              <Link href="/dashboard/billing" className="text-primary hover:underline">Upgrade</Link>
            </div>
          </div>
          <button className="flex items-center gap-3 px-3 py-2.5 w-full mt-2 rounded-lg text-muted-foreground hover:text-red-400 hover:bg-red-500/10 transition-all">
            <LogOut className="w-5 h-5" />
            <span className="font-medium text-sm">Log out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/5 via-background to-background">
        <header className="h-20 border-b border-border/50 glass flex items-center px-8 justify-between md:justify-end shrink-0">
          <div className="md:hidden flex items-center gap-2">
            <Film className="w-6 h-6 text-primary" />
            <span className="font-bold text-lg">ShadowReel</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-sm">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="font-medium text-primary">Pro Plan</span>
            </div>
            <div className="w-9 h-9 rounded-full bg-accent flex items-center justify-center font-bold text-white shadow-lg border border-white/10">
              PR
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
