"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";
import { FinancialDashboard } from "../components/FinancialDashboard";
import { Header } from "../components/Header";
import { Footer } from "../components/Footer";
import { CustomAssistantMessage } from "../components/AssistantMessage";
import { prompt } from "../lib/prompt";
import { useCopilotReadable } from "@copilotkit/react-core";
import { FinancialAgentProvider } from "../lib/hooks/use-financial-agent";

export default function Home() {
  useCopilotReadable({
    description: "Current time",
    value: new Date().toLocaleTimeString(),
  });

  return (
    <FinancialAgentProvider>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <main className="w-full max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex-grow">
          <FinancialDashboard />
        </main>
        <Footer />
        <CopilotSidebar
          instructions={prompt}
          clickOutsideToClose={false}
          AssistantMessage={CustomAssistantMessage}
          labels={{
            title: "Financial AI Assistant",
            initial: "Hello! I can help you analyze your financial data. Ask me about revenue, expenses, profit margins, or trends.",
            placeholder: "Ask about revenue, expenses, profit, or trends...",
          }}
        />
      </div>
    </FinancialAgentProvider>
  );
}
