import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  LangGraphHttpAgent,
  ExperimentalEmptyAdapter
} from "@copilotkit/runtime";


const serviceAdapter = new ExperimentalEmptyAdapter();

export const POST = async (req: NextRequest) => {
  const baseUrl = process.env.REMOTE_ACTION_URL || "http://localhost:8000/copilotkit";
  const runtime = new CopilotRuntime({
    agents: {
      'financial_assistant': new LangGraphHttpAgent({
        url: `${baseUrl}/agents/financial_assistant`,
      })
    }
  })

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};