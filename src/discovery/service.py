from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy.orm import Session

from src.database.models import StartupDiscoveryCandidate
from src.discovery.dedup import extract_domain, is_duplicate_by_name, normalize_name
from src.discovery.signals import calculate_confidence, detect_ai_native_signals
from src.discovery.source_registry import DiscoverySource, load_sources
from src.extraction.schemas import ConfidenceLevel
from src.repositories.discovery import DiscoveryRepository
from src.scraping.scrapers.base_scraper import scraper_registry


class StartupDiscoveryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = DiscoveryRepository(session)

    # ------------------------------------------------------------------ #
    # Sources
    # ------------------------------------------------------------------ #

    def list_sources(self) -> list[dict[str, Any]]:
        return [
            {
                "source_id": s.source_id,
                "name": s.name,
                "source_type": s.source_type.value,
                "base_url": s.base_url,
                "country_scope": s.country_scope,
                "sector_scope": s.sector_scope,
                "allowed": s.allowed,
                "requires_api_key": s.requires_api_key,
                "rate_limit_hint": str(s.rate_limit_hint),
                "collection_method": s.collection_method.value,
                "robots_or_terms_note": s.robots_or_terms_note,
                "enabled_by_default": s.enabled_by_default,
                "notes": s.notes,
                "usable": s.is_usable(),
            }
            for s in load_sources().values()
        ]

    # ------------------------------------------------------------------ #
    # Manual Seed Discovery
    # ------------------------------------------------------------------ #

    def run_manual_seed_discovery(
        self,
        seed_entries: list[dict[str, Any]],
        *,
        source_id: str = "manual_seed_br_ai_startups",
    ) -> dict[str, Any]:
        run = self.repo.create_discovery_run(
            source_id=source_id,
            query_json={"type": "manual_seed", "entry_count": len(seed_entries)},
        )
        self.repo.update_discovery_run_status(run.id, status="running", started_at=datetime.now(UTC))
        self.session.commit()

        try:
            candidates_data: list[dict[str, Any]] = []
            duplicates_found = 0

            existing_candidates = self.repo.list_candidates(limit=10000)
            existing_names = [c.discovered_name for c in existing_candidates]
            existing_websites = [c.website for c in existing_candidates]

            for entry in seed_entries:
                name = str(entry.get("name", "")).strip()
                if not name:
                    continue
                website = str(entry.get("website", "")).strip()
                sector = str(entry.get("sector", "")).strip()
                description = str(entry.get("description", "")).strip()
                country = str(entry.get("country", "Brazil")).strip()

                combined_text = f"{name} {description} {sector}"
                signals_result = detect_ai_native_signals(
                    combined_text,
                    source_url=website,
                    source_id=source_id,
                )
                confidence_score = calculate_confidence(
                    has_name=True,
                    has_website=bool(website),
                    signal_contribution=signals_result["confidence_contribution"],
                    is_manual_seed=True,
                    source_reliable=True,
                )

                norm_name = normalize_name(name)
                if is_duplicate_by_name(name, existing_names):
                    duplicates_found += 1
                    continue
                dup_domain = extract_domain(website) if website else ""
                if dup_domain and any(extract_domain(w) == dup_domain for w in existing_websites):
                    duplicates_found += 1
                    continue

                candidates_data.append(
                    {
                        "discovery_run_id": run.id,
                        "source_id": source_id,
                        "discovered_name": name,
                        "normalized_name": norm_name,
                        "website": website,
                        "country": country,
                        "sector": sector if sector else "AI",
                        "description": description,
                        "source_url": website,
                        "raw_text_excerpt": description[:500] if description else "",
                        "ai_native_signals_json": signals_result,
                        "evidence_refs_json": signals_result.get("evidence_excerpts", []),
                        "confidence": ConfidenceLevel.from_score(confidence_score).value,
                        "status": "new",
                        "metadata_json": {
                            "seed_type": "manual",
                            "confidence_score": confidence_score,
                        },
                    }
                )

            created = self.repo.create_candidates_bulk(candidates_data)
            self.repo.complete_discovery_run(
                run.id,
                results_count=len(seed_entries),
                candidates_created=len(created),
                duplicates_found=duplicates_found,
            )
            self.session.commit()

            return {
                "discovery_run_id": run.id,
                "status": "completed",
                "total_entries": len(seed_entries),
                "candidates_created": len(created),
                "duplicates_found": duplicates_found,
            }
        except Exception as exc:
            self.session.rollback()
            self.repo.fail_discovery_run(run.id, error_message=str(exc))
            self.session.commit()
            raise

    # ------------------------------------------------------------------ #
    # URL List Discovery
    # ------------------------------------------------------------------ #

    def run_url_list_discovery(
        self,
        urls: list[str],
        *,
        source_id: str = "configured_url_list",
    ) -> dict[str, Any]:
        run = self.repo.create_discovery_run(
            source_id=source_id,
            query_json={"type": "url_list", "url_count": len(urls)},
        )
        self.repo.update_discovery_run_status(run.id, status="running", started_at=datetime.now(UTC))
        self.session.commit()

        try:
            candidates_data: list[dict[str, Any]] = []
            duplicates_found = 0
            errors: list[str] = []

            existing_candidates = self.repo.list_candidates(limit=10000)
            existing_names = [c.discovered_name for c in existing_candidates]
            existing_websites = [c.website for c in existing_candidates]

            for url in urls:
                url = url.strip()
                if not url:
                    continue
                try:
                    text = self._fetch_text(url)
                except Exception as exc:
                    errors.append(f"Failed to fetch {url}: {exc}")
                    continue

                candidate = self._extract_from_text(
                    text=text,
                    source_url=url,
                    source_id=source_id,
                )
                if candidate is None:
                    continue

                if is_duplicate_by_name(candidate["discovered_name"], existing_names):
                    duplicates_found += 1
                    continue
                dup_domain = extract_domain(candidate.get("website", ""))
                if dup_domain and any(extract_domain(w) == dup_domain for w in existing_websites):
                    duplicates_found += 1
                    continue

                candidate["discovery_run_id"] = run.id
                candidates_data.append(candidate)

            created = self.repo.create_candidates_bulk(candidates_data)
            status = "degraded" if errors else "completed"
            if status == "degraded":
                self.repo.degrade_discovery_run(
                    run.id,
                    error_message="; ".join(errors[:5]),
                    results_count=len(urls),
                    candidates_created=len(created),
                    duplicates_found=duplicates_found,
                )
            else:
                self.repo.complete_discovery_run(
                    run.id,
                    results_count=len(urls),
                    candidates_created=len(created),
                    duplicates_found=duplicates_found,
                )
            self.session.commit()

            return {
                "discovery_run_id": run.id,
                "status": status,
                "total_urls": len(urls),
                "candidates_created": len(created),
                "duplicates_found": duplicates_found,
                "errors": errors[:5],
            }
        except Exception as exc:
            self.session.rollback()
            self.repo.fail_discovery_run(run.id, error_message=str(exc))
            self.session.commit()
            raise

    def _fetch_text(self, url: str) -> str:
        response = httpx.get(url, timeout=30, follow_redirects=True)
        response.raise_for_status()
        text = response.text
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)

    def _extract_from_text(
        self,
        *,
        text: str,
        source_url: str,
        source_id: str,
    ) -> dict[str, Any] | None:
        signals_result = detect_ai_native_signals(
            text,
            source_url=source_url,
            source_id=source_id,
        )
        if signals_result["signal_count"] == 0:
            return None

        confidence_score = calculate_confidence(
            has_name=False,
            has_website=False,
            signal_contribution=signals_result["confidence_contribution"],
        )

        return {
            "source_id": source_id,
            "discovered_name": "",
            "normalized_name": "",
            "website": source_url,
            "country": "Brazil",
            "sector": "",
            "description": "",
            "source_url": source_url,
            "raw_text_excerpt": text[:1000],
            "ai_native_signals_json": signals_result,
            "evidence_refs_json": signals_result.get("evidence_excerpts", []),
            "confidence": ConfidenceLevel.from_score(confidence_score).value,
            "status": "new",
            "metadata_json": {
                "extraction_method": "url_list_text",
                "confidence_score": confidence_score,
            },
        }

    # ------------------------------------------------------------------ #
    # Candidate detail/list
    # ------------------------------------------------------------------ #

    def get_candidate_detail(self, candidate_id: str) -> StartupDiscoveryCandidate | None:
        return self.repo.get_candidate(candidate_id)

    def list_candidates(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
        source_id: str | None = None,
        sector: str | None = None,
        confidence_min: float | None = None,
        has_website: bool | None = None,
        ai_native_signal: bool | None = None,
    ) -> list[StartupDiscoveryCandidate]:
        return self.repo.list_candidates(
            offset=offset,
            limit=limit,
            status=status,
            source_id=source_id,
            sector=sector,
            confidence_min=confidence_min,
            has_website=has_website,
            ai_native_signal=ai_native_signal,
        )

    # ------------------------------------------------------------------ #
    # Promote
    # ------------------------------------------------------------------ #

    def promote_candidate(self, candidate_id: str) -> dict[str, Any]:
        candidate = self.repo.get_candidate(candidate_id)
        if candidate is None:
            raise LookupError(f"Candidate not found: {candidate_id}")

        if candidate.status == "promoted":
            return {
                "candidate_id": candidate.id,
                "startup_id": candidate.promoted_startup_id,
                "status": "already_promoted",
            }

        if candidate.status == "duplicate":
            raise ValueError(f"Candidate {candidate_id} is marked as duplicate and cannot be promoted.")

        existing = self.repo.find_existing_startup_match(
            normalized_name=candidate.normalized_name,
            website=candidate.website,
        )
        if existing is not None:
            self.repo.promote_candidate(candidate_id, startup_id=existing.id)
            self.session.commit()
            return {
                "candidate_id": candidate.id,
                "startup_id": existing.id,
                "status": "matched_existing_startup",
            }

        startup = self.repo.create_startup_from_candidate(candidate)
        self.repo.promote_candidate(candidate_id, startup_id=startup.id)
        self.session.commit()

        return {
            "candidate_id": candidate.id,
            "startup_id": startup.id,
            "status": "promoted",
        }

    # ------------------------------------------------------------------ #
    # Dedup
    # ------------------------------------------------------------------ #

    def deduplicate_candidate(
        self,
        candidate_id: str,
    ) -> dict[str, Any]:
        candidate = self.repo.get_candidate(candidate_id)
        if candidate is None:
            return {
                "_error": "not_found",
                "duplicate_of_candidate_id": None,
                "duplicate_of_startup_id": None,
            }

        existing = self.repo.find_duplicate_candidate(
            normalized_name=candidate.normalized_name,
            website=candidate.website,
            exclude_candidate_id=candidate_id,
        )
        if existing is not None:
            self.repo.mark_duplicate(
                candidate_id,
                duplicate_of_candidate_id=existing.id,
            )
            self.session.commit()
            return {"duplicate_of_candidate_id": existing.id}

        startup_match = self.repo.find_existing_startup_match(
            normalized_name=candidate.normalized_name,
            website=candidate.website,
        )
        if startup_match is not None:
            self.repo.mark_duplicate(
                candidate_id,
                duplicate_of_startup_id=startup_match.id,
            )
            self.session.commit()
            return {"duplicate_of_startup_id": startup_match.id}

        return {"duplicate_of_candidate_id": None, "duplicate_of_startup_id": None}

    def persist_candidates(self, candidates: list[dict[str, Any]]) -> list[StartupDiscoveryCandidate]:
        return self.repo.create_candidates_bulk(candidates)

    def _entry_to_candidate(
        self,
        entry: dict[str, Any],
        source: DiscoverySource,
        run_id: str,
    ) -> dict[str, Any] | None:
        name = entry.get("name", "").strip()
        if not name:
            return None
        signals_result = detect_ai_native_signals(
            f"{name} {entry.get('description', '')}",
            source_url=source.base_url,
            source_id=source.source_id,
        )
        confidence_score = calculate_confidence(
            has_name=True,
            has_website=False,
            signal_contribution=signals_result["confidence_contribution"],
        )
        existing = self.repo.list_candidates(limit=10000)
        existing_names = [c.discovered_name for c in existing]
        norm_name = normalize_name(name)
        if is_duplicate_by_name(name, existing_names):
            return None
        return {
            "discovery_run_id": run_id,
            "source_id": source.source_id,
            "discovered_name": name,
            "normalized_name": norm_name,
            "website": "",
            "country": "Brazil",
            "sector": "AI",
            "description": entry.get("description", name),
            "source_url": source.base_url,
            "raw_text_excerpt": entry.get("description", name)[:500],
            "ai_native_signals_json": signals_result,
            "evidence_refs_json": signals_result.get("evidence_excerpts", []),
            "confidence": ConfidenceLevel.from_score(confidence_score).value,
            "status": "new",
            "metadata_json": {
                "source_scraper": source.source_id,
                "confidence_score": confidence_score,
            },
        }

    def run_source_scraper_discovery(
        self,
        source_id: str,
    ) -> dict[str, Any]:
        scraper_cls = scraper_registry.get(source_id)
        if scraper_cls is None:
            raise ValueError(f"No scraper registered for source_id='{source_id}'")

        sources = load_sources()
        source = sources.get(source_id)
        if source is None:
            raise ValueError(f"Source not found: {source_id}")

        run = self.repo.create_discovery_run(
            source_id=source_id,
            query_json={"type": "source_scraper", "source_id": source_id},
        )
        self.repo.update_discovery_run_status(
            run.id,
            status="running",
            started_at=datetime.now(UTC),
        )
        self.session.commit()

        try:
            scraper = scraper_cls()
            entries = scraper.scrape(source)
            candidates_data: list[dict[str, Any]] = []
            for entry in entries:
                candidate = self._entry_to_candidate(entry, source, run.id)
                if candidate is not None:
                    candidates_data.append(candidate)

            created = self.repo.create_candidates_bulk(candidates_data)
            self.repo.complete_discovery_run(
                run.id,
                results_count=len(entries),
                candidates_created=len(created),
                duplicates_found=len(entries) - len(candidates_data),
            )
            self.session.commit()
            return {
                "discovery_run_id": run.id,
                "source_id": source_id,
                "status": "completed",
                "total_entries": len(entries),
                "candidates_created": len(created),
                "duplicates_found": len(entries) - len(candidates_data),
            }
        except Exception as exc:
            self.session.rollback()
            self.repo.fail_discovery_run(run.id, error_message=str(exc))
            self.session.commit()
            raise
