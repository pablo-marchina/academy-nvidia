from __future__ import annotations

import re
from dataclasses import dataclass


PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior|system|developer)\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?(system prompt|developer message|hidden instructions)", re.IGNORECASE),
    re.compile(r"exfiltrate|leak|dump\s+(api[_-]?key|secret|token|password)", re.IGNORECASE),
    re.compile(r"call\s+tool|execute\s+(shell|powershell|bash)|run\s+command", re.IGNORECASE),
    re.compile(r"rank\s+.*because\s+.*paid\s+partnership|manipulate\s+recommendation", re.IGNORECASE),
)

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[A-Za-z0-9_\-]{12,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
)


@dataclass(frozen=True)
class SecurityFinding:
    finding_type: str
    matched: str
    action: str


def detect_prompt_injection(text: str) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append(
                SecurityFinding(
                    finding_type="prompt_injection",
                    matched=match.group(0),
                    action="quarantine_external_instruction",
                )
            )
    return findings


def detect_secret_leakage(text: str) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                SecurityFinding(
                    finding_type="secret_leakage",
                    matched=match.group(0),
                    action="block_and_redact",
                )
            )
    return findings


def sanitize_untrusted_rag_context(text: str) -> tuple[str, list[SecurityFinding]]:
    findings = detect_prompt_injection(text) + detect_secret_leakage(text)
    sanitized = text
    for finding in findings:
        sanitized = sanitized.replace(finding.matched, "[BLOCKED_UNTRUSTED_CONTENT]")
    return sanitized, findings


def assert_tool_request_allowed(tool_name: str, allowed_tools: set[str]) -> bool:
    normalized = tool_name.strip().casefold()
    return normalized in {tool.casefold() for tool in allowed_tools}
