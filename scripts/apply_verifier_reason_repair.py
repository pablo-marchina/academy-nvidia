from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/verify_runtime_output.ps1"


def main() -> None:
    text = PATH.read_text(encoding="utf-8-sig")
    old = '''        $status = ([string]$result.status).ToLowerInvariant()
        $errorText = [string](Get-OptionalProperty -Object $result -Name "error")
        $forbidden = Test-ForbiddenRuntimeError -Text $errorText
        $statusAccepted = $acceptedStatuses -contains $status
        $runtimeClean = [string]::IsNullOrWhiteSpace($errorText) -and $null -eq $forbidden
        if ($status -eq "degraded") {
            $reason = [string](Get-OptionalProperty -Object $result -Name "degraded_reason")
'''
    new = '''        $status = ([string]$result.status).ToLowerInvariant()
        $errorText = [string](Get-OptionalProperty -Object $result -Name "error")
        $reason = [string](Get-OptionalProperty -Object $result -Name "degraded_reason")
        $forbidden = Test-ForbiddenRuntimeError -Text $errorText
        $statusAccepted = $acceptedStatuses -contains $status
        $runtimeClean = [string]::IsNullOrWhiteSpace($errorText) -and $null -eq $forbidden
        if ($status -eq "degraded") {
'''

    if new in text:
        print("[already] verifier degraded reason initialized for every result")
        return
    if old not in text:
        raise RuntimeError("Could not locate pipeline result block in verify_runtime_output.ps1")

    PATH.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("[fixed] verifier degraded reason initialized for every result")


if __name__ == "__main__":
    main()
