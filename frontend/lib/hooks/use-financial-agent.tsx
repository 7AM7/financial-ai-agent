"use client";

import { ReactNode, useEffect } from "react";
import { useCoAgent } from "@copilotkit/react-core";

// Define the agent state interface matching backend
export type FinancialAgentState = {
  result_data: Record<string, unknown>[];
  result_columns: string[];
  result_count: number;
  sql: string;
  status: string;
  messages: Record<string, unknown>[];
}


/**
 * Financial Agent Provider Component
 *
 * Wraps the application and provides access to the financial agent state.
 * This enables real-time status updates and state synchronization between
 * the backend agent and frontend UI.
 */
export function FinancialAgentProvider({ children }: { children: ReactNode }) {
  // Connect to the financial agent
  const { state } = useCoAgent<FinancialAgentState>({
    name: "financial_assistant",
    initialState: {
      result_data: [],
      result_columns: [],
      result_count: 0,
      sql: "",
      status: "thinking...",
      messages: [],
    },
  });


  // Log state changes for debugging
  useEffect(() => {
    console.log("[DEBUG] Agent state changed:", {
      result_data_length: state.result_data?.length || 0,
      result_count: state.result_count,
      result_columns: state.result_columns,
      sql_length: state.sql?.length || 0,
      status: state.status,
      has_messages: state.messages?.length || 0,
    });

    if (state.result_data && state.result_data.length > 0) {
      console.log("[DEBUG] Result data sample:", state.result_data[0]);
    }
  }, [state]);

  return <>{children}</>;
}

/**
 * Hook to access financial agent state
 *
 * Use this hook in components to access the agent's current state.
 *
 * @example
 * ```tsx
 * const { status } = useFinancialAgent();
 * ```
 */
export function useFinancialAgent() {
  const { state } = useCoAgent<FinancialAgentState>({
    name: "financial_assistant",
  });

  return {
    status: state.status || "",
  };
}
