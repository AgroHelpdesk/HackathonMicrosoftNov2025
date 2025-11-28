// API Response Types
export interface StartSessionResponse {
    session_id: string;
}

export interface SendMessageResponse {
    ok: boolean;
    reply: string;
    flow_state?: string;
    needs_clarification?: boolean;
    work_order_id?: string;
    execution_summary?: {
        total_time_ms: number;
        agents_executed: number;
        decisions_made: number;
        success: boolean;
        work_order?: {
            id: string;
            specialist: string;
            priority: string;
        };
        runbook_execution?: {
            name: string;
            success: boolean;
            steps_completed: number;
        };
    };
}

export interface MessageHistoryResponse {
    messages: Array<{
        role: string;
        content: string;
        timestamp: string;
    }>;
}
