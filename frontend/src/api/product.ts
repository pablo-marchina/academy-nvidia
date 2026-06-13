import { requestJson } from "./client";
import type {
  ProductReadinessRead,
  ProductCapabilityRead,
  ProductSetupChecklistRead,
  StartupListItem,
  StartupRead,
  StartupCreatePayload,
  StartupUpdatePayload,
  AnalysisRunRead,
  ActionBriefRead,
  ReviewDecisionRead,
  OpportunityListResponse,
  ClaimListResponse,
  EvidenceCoverageRead,
  ActivationRecommendationRead,
  ActivationDossierRead,
  ActivationDossierMarkdownRead,
  ProductQualitySummaryRead,
} from "./types";

export function getProductReadiness(): Promise<ProductReadinessRead> {
  return requestJson<ProductReadinessRead>("/product/readiness");
}

export function getProductCapabilities(): Promise<ProductCapabilityRead[]> {
  return requestJson<ProductCapabilityRead[]>("/product/capabilities");
}

export function getProductSetupChecklist(): Promise<ProductSetupChecklistRead> {
  return requestJson<ProductSetupChecklistRead>("/product/setup-checklist");
}

export function listStartups(
  offset = 0,
  limit = 100,
): Promise<StartupListItem[]> {
  return requestJson<StartupListItem[]>(
    `/startups?offset=${offset}&limit=${limit}`,
  );
}

export function createStartup(
  payload: StartupCreatePayload,
): Promise<StartupRead> {
  return requestJson<StartupRead>("/startups", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getStartup(id: string): Promise<StartupRead> {
  return requestJson<StartupRead>(`/startups/${id}`);
}

export function updateStartup(
  id: string,
  payload: StartupUpdatePayload,
): Promise<StartupRead> {
  return requestJson<StartupRead>(`/startups/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function createAnalysisRun(
  startupId: string,
  useRag = false,
): Promise<AnalysisRunRead> {
  return requestJson<AnalysisRunRead>(
    `/startups/${startupId}/analysis-runs`,
    {
      method: "POST",
      body: JSON.stringify({ use_rag: useRag }),
    },
  );
}

export function getAnalysisRun(id: string): Promise<AnalysisRunRead> {
  return requestJson<AnalysisRunRead>(`/analysis-runs/${id}`);
}

export function getAnalysisRunBrief(
  id: string,
): Promise<ActionBriefRead> {
  return requestJson<ActionBriefRead>(`/analysis-runs/${id}/brief`);
}

export function listOpportunities(
  offset = 0,
  limit = 50,
): Promise<OpportunityListResponse> {
  return requestJson<OpportunityListResponse>(
    `/opportunities?offset=${offset}&limit=${limit}`,
  );
}

export function getAnalysisRunClaims(
  id: string,
): Promise<ClaimListResponse> {
  return requestJson<ClaimListResponse>(
    `/analysis-runs/${id}/claims?limit=500`,
  );
}

export function getEvidenceCoverage(
  id: string,
): Promise<EvidenceCoverageRead> {
  return requestJson<EvidenceCoverageRead>(
    `/analysis-runs/${id}/evidence-coverage`,
  );
}

export function getActivationRecommendations(
  id: string,
): Promise<{ items: ActivationRecommendationRead[]; total: number }> {
  return requestJson<{ items: ActivationRecommendationRead[]; total: number }>(
    `/analysis-runs/${id}/activation-recommendations`,
  );
}

export function generateActivationRecommendations(
  id: string,
): Promise<{ recommendations: ActivationRecommendationRead[]; total: number }> {
  return requestJson<{
    recommendations: ActivationRecommendationRead[];
    total: number;
  }>(`/analysis-runs/${id}/activation-recommendations/generate`, {
    method: "POST",
  });
}

export function getDossier(id: string): Promise<ActivationDossierRead> {
  return requestJson<ActivationDossierRead>(
    `/analysis-runs/${id}/dossier`,
  );
}

export function getDossierMarkdown(
  id: string,
): Promise<ActivationDossierMarkdownRead> {
  return requestJson<ActivationDossierMarkdownRead>(
    `/analysis-runs/${id}/dossier/markdown`,
  );
}

export function generateDossier(
  id: string,
  force = false,
): Promise<{ dossier: ActivationDossierRead; version: number; is_new: boolean }> {
  const query = force ? "?force=true" : "";
  return requestJson<{
    dossier: ActivationDossierRead;
    version: number;
    is_new: boolean;
  }>(`/analysis-runs/${id}/dossier${query}`, {
    method: "POST",
  });
}

export function getQualitySummary(
  id: string,
): Promise<ProductQualitySummaryRead> {
  return requestJson<ProductQualitySummaryRead>(
    `/analysis-runs/${id}/quality-summary`,
  );
}

export function createReview(
  analysisRunId: string,
  decision: string,
  reviewer: string,
  notes = "",
): Promise<ReviewDecisionRead> {
  return requestJson<ReviewDecisionRead>(
    `/analysis-runs/${analysisRunId}/review`,
    {
      method: "POST",
      body: JSON.stringify({ decision, reviewer, notes }),
    },
  );
}

export function listReviews(
  analysisRunId: string,
): Promise<ReviewDecisionRead[]> {
  return requestJson<ReviewDecisionRead[]>(
    `/analysis-runs/${analysisRunId}/reviews`,
  );
}

export function updateClaimReview(
  analysisRunId: string,
  claimId: string,
  reviewStatus: string,
  reviewerNotes = "",
): Promise<void> {
  return requestJson<void>(
    `/analysis-runs/${analysisRunId}/claims/${claimId}/review`,
    {
      method: "PATCH",
      body: JSON.stringify({
        review_status: reviewStatus,
        reviewer_notes: reviewerNotes,
      }),
    },
  );
}
