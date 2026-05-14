import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lupa — Auditor de facturas farmacéuticas",
  description:
    "Auditor de facturas farmacéuticas para farmacias españolas con procesamiento 100% local en el navegador.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-bg text-ink">{children}</body>
    </html>
  );
}
