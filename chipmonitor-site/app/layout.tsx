import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChipMonitor — AI News to TSMC",
  description: "Weekly AI news, seven core beliefs, original source posts and semiconductor relationship exposure.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
