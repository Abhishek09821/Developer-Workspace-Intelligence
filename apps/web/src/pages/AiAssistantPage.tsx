import { Bot } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function AiAssistantPage() {
  return (
    <div>
      <PageHeader
        title="AI Assistant"
        description="Ask questions about your codebase in natural language."
      />
      <EmptyState
        icon={<Bot className="w-12 h-12" />}
        title="AI Assistant not configured"
        description="Set an AI provider (OpenAI, Anthropic, or Amazon Bedrock) in Settings to enable the codebase assistant."
      />
    </div>
  )
}
