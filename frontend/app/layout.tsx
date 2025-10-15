import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Financial Data Dashboard | AI-Powered Analytics",
  description: "AI-powered financial data dashboard with natural language queries for QuickBooks and Rootfi data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <CopilotKit 
          runtimeUrl="/api/copilotkit"
          showDevConsole={false}
          agent="financial_assistant"
          // threadId="92aa28d1-d15a-10be-aec1-1ba6c3e11327"
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
