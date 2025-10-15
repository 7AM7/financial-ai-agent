import { AssistantMessageProps } from "@copilotkit/react-ui";
import { Markdown } from "@copilotkit/react-ui";
import { Loader } from "lucide-react";
import { useFinancialAgent } from "../lib/hooks/use-financial-agent";
import { useState, useEffect } from "react";

export const CustomAssistantMessage = (props: AssistantMessageProps) => {
  const { message, isLoading } = props;
  const { status } = useFinancialAgent();
  const [displayedStatus, setDisplayedStatus] = useState<string | null>(null);

  let messageContent: string = "";
  if (typeof message === "string") {
    messageContent = message;
  } else if (typeof message === "object" && message !== null) {
    messageContent = (message as { content?: string }).content || "";
  }

  useEffect(() => {
    if (isLoading) {
      if (status && status.trim() !== "" && !status.includes("✅")) {
        setDisplayedStatus(status);
      } else if (!messageContent || messageContent.trim() === "") {
        setDisplayedStatus("Thinking...");
      } else {
        setDisplayedStatus(null);
      }
    } else {
      const timer = setTimeout(() => {
        setDisplayedStatus(null);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [isLoading, status, messageContent]);

  const statusMessage = displayedStatus;

  return (
    <div className="pb-4">
      {(messageContent || isLoading) && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="text-sm text-gray-700 dark:text-gray-300 markdown-content">
            <Markdown content={messageContent} />
            {statusMessage && (
              <div className="flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400 mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                <Loader className="h-3 w-3 animate-spin" />
                <span>{statusMessage}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
