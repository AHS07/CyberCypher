/**
 * Copy shared types to dashboard lib
 * This is a symlink alternative for the monorepo
 */

export type TestStatus = "pending" | "analyzing" | "complete" | "failed";
export type Verdict = "PASS" | "FAIL" | "NEEDS_REVIEW";
export type Provider = "claude" | "gemini" | "ollama";
export type EventType = "success" | "failure" | "failover";

export interface CouncilOpinion {
    agent: string;
    provider: Provider;
    timestamp: string;
    analysis: string;
    detected_issues: string[];
    false_positives: string[];
    risk_score: number;
    confidence: number;
}

export interface ShadowTest {
    id: number;
    test_id: string;
    merchant_id: string;
    diff_report: Record<string, any>;
    legacy_response: Record<string, any>;
    headless_response: Record<string, any>;
    council_opinions: CouncilOpinion[];
    active_provider?: string;
    providers_attempted?: string[];
    is_mitigated: boolean;
    risk_score?: number;
    final_verdict?: Verdict;
    mitigation_recommendation?: string;
    status: TestStatus;
    error_message?: string;
    created_at: string;
    updated_at: string;
}

export interface ProviderHealth {
    provider: Provider;
    is_healthy: boolean;
    last_success?: string;
    last_failure?: string;
    consecutive_failures: number;
    avg_response_time_ms?: number;
}
