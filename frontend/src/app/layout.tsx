import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ShadowReel AI | Cinematic Video Generation",
  description: "Generate cinematic worlds, AI videos, and documentary scenes with ShadowReel AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-background text-foreground min-h-screen selection:bg-primary/30 selection:text-primary`}>
        {children}
      </body>
    </html>
  );
}
