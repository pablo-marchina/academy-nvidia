import type { StartupInput } from "./api/client";

export const sampleStartupInput: StartupInput = {
  startup_name: "Nexus AI Labs",
  description: "Fictional AI-native startup for local demo purposes only.",
  source_url: "https://example.com/nexus-ai-labs",
  metadata: {
    description: "Fictional startup sample. No real company data.",
    generated_at: "2026-06-11T00:00:00Z",
    schema_version: "1.0",
  },
  profile: {
    sector: "HealthTech",
    description:
      "AI-native healthcare platform using deep learning for real-time medical image analysis in production across multiple hospital networks.",
    product_summary:
      "Real-time AI-powered medical imaging diagnostics deployed in hospitals.",
    ai_signals: [
      "deep learning",
      "computer vision",
      "neural networks",
      "real-time inference",
    ],
    tech_stack: ["PyTorch", "TensorRT", "Docker", "Kubernetes"],
    customers: ["Fictional Hospital A", "Clinic Network B"],
    funding: ["Seed $2M led by Fictional VC"],
  },
  evidence: [
    {
      claim: "Deep learning medical imaging platform in production",
      confidence: "high",
    },
    {
      claim: "Production deployment in major hospital networks",
      confidence: "high",
    },
    {
      claim: "PyTorch and GPU inference pipeline deployed",
      confidence: "high",
    },
    {
      claim: "Computer vision models for real-time diagnostics",
      confidence: "medium",
    },
    {
      claim: "Seed funding of $2M for AI infrastructure",
      confidence: "medium",
    },
  ],
};
