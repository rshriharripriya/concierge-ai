import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { AuroraBackground } from "@/components/ui/AuroraBackground";

import { Analytics } from "@vercel/analytics/react";

const inter = Inter({ subsets: ["latin"] });
const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  weight: ["400", "700", "900"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_URL || 'http://localhost:3000'),
  title: "Concierge AI - Smart tax help",
  description: "AI-powered customer-to-expert routing system inspired by Intuit VEP architecture",
  openGraph: {
    title: "Concierge AI - Smart tax help",
    description: "AI-powered customer-to-expert routing system inspired by Intuit VEP architecture",
    images: ['/preview.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: "Concierge AI - Smart tax help",
    description: "AI-powered customer-to-expert routing system inspired by Intuit VEP architecture",
    images: ['/preview.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} ${playfair.variable} text-gray-900 antialiased`}>
        <AuroraBackground>
          <div className="relative z-10 min-h-screen flex flex-col w-full">
            {children}
          </div>
        </AuroraBackground>
        <Analytics />
      </body>
    </html>
  );
}
