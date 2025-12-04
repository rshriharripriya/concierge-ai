const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/py';

export interface QueryResponse {
    conversation_id: string;
    intent: string;
    complexity_score: number;
    route_decision: string;
    response: string;
    confidence: number;
    expert?: any;
    sources: any[];
    reasoning: string;
}

export async function sendQuery(
    query: string,
    userId: string,
    conversationId?: string
): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE}/chat/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query,
            user_id: userId,
            conversation_id: conversationId,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
    }

    return response.json();
}

export async function getExperts() {
    const response = await fetch(`${API_BASE}/experts/available`);

    if (!response.ok) {
        throw new Error('Failed to fetch experts');
    }

    return response.json();
}

export async function getConversation(conversationId: string) {
    const response = await fetch(`${API_BASE}/chat/conversations/${conversationId}`);

    if (!response.ok) {
        throw new Error('Failed to fetch conversation');
    }

    return response.json();
}
