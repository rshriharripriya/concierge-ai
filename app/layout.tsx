import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuroraBackground } from "@/components/ui/AuroraBackground";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Concierge AI - Intelligent Expert Routing",
  description: "AI-powered customer-to-expert routing system inspired by Intuit VEP architecture",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <AuroraBackground>
          <div className="relative z-10 min-h-screen flex flex-col w-full">
            {children}
          </div>
        </AuroraBackground>
      </body>
    </html>
  );
}
