// Chat Message Types
export interface ChatMessage {
    id: string;
    content: string;
    sender: string;
    timestamp: Date;
    isBot: boolean;
    agentType?: string;
    isError?: boolean;
}

export type ChatStatus = 'active' | 'closed';

export interface ChatSession {
    sessionId: string;
    createdAt: Date;
    status: ChatStatus;
}
