import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import { MESSAGES } from "@/lib/messages";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-fraunces",
  display: "swap",
});

const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-plex-sans",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://lupafarma.es"),
  title: MESSAGES.meta.title,
  description: MESSAGES.meta.description,
  keywords: ["farmacia", "facturas", "auditor", "PVL", "BOE", "Nomenclátor", "España"],
  authors: [{ name: "Luis Rodriguez Cruz" }],
  creator: "Lupafarma",
  openGraph: {
    type: "website",
    locale: "es_ES",
    url: "https://lupafarma.es",
    title: MESSAGES.meta.title,
    description: MESSAGES.meta.description,
    siteName: "Lupa",
    images: [
      {
        url: "/opengraph-image.png",
        width: 1200,
        height: 630,
        alt: "Lupa — Auditor de facturas farmacéuticas",
      },
    ],
  },
  robots: { index: true, follow: true },
  alternates: { canonical: "https://lupafarma.es" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`h-full antialiased ${fraunces.variable} ${plexSans.variable} ${plexMono.variable}`}
    >
      <body className="min-h-full bg-bg text-ink font-sans">{children}</body>
    </html>
  );
}
