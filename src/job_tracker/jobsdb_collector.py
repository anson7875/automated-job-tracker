"""Collect JobsDB listings from a filtered search URL when HTML is available."""

import json
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


USER_AGENT = "AutoJobTracker/0.1 (personal project)"


class JobPageParser(HTMLParser):
    """Extract job links and JSON-LD blocks from an HTML page."""

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.job_links: set[str] = set()
        self.jsonld_blocks: list[str] = []
        self._inside_jsonld = False
        self._jsonld_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            url = urljoin(self.base_url, attributes["href"])
            if "/job/" in url:
                self.job_links.add(url.split("?")[0])

        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._inside_jsonld = True
            self._jsonld_buffer = []

    def handle_data(self, data: str) -> None:
        if self._inside_jsonld:
            self._jsonld_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._inside_jsonld:
            self.jsonld_blocks.append("".join(self._jsonld_buffer))
            self._inside_jsonld = False


def fetch_html(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"Could not fetch {url}: {error}") from error


def parse_job_posting(blocks: list[str]) -> dict | None:
    """Return the first JSON-LD JobPosting object found in script blocks."""
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue

        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == "JobPosting":
                organization = candidate.get("hiringOrganization") or {}
                location = candidate.get("jobLocation") or {}
                address = location.get("address") or {}
                salary = candidate.get("baseSalary") or {}
                salary_value = salary.get("value") or {}
                return {
                    "title": candidate.get("title") or "Untitled job",
                    "company": organization.get("name"),
                    "url": candidate.get("url"),
                    "description": candidate.get("description") or "",
                    "location": address.get("addressLocality"),
                    "salary_min_hkd": salary_value.get("minValue"),
                    "salary_max_hkd": salary_value.get("maxValue"),
                }
    return None


def collect_jobs(search_url: str, max_jobs: int = 20) -> list[dict]:
    """Find job links on a search page and parse their details."""
    if max_jobs < 1:
        raise ValueError("max_jobs must be at least 1")

    search_html = fetch_html(search_url)
    search_parser = JobPageParser(search_url)
    search_parser.feed(search_html)
    jobs = []

    for job_url in list(search_parser.job_links)[:max_jobs]:
        detail_html = fetch_html(job_url)
        detail_parser = JobPageParser(job_url)
        detail_parser.feed(detail_html)
        job = parse_job_posting(detail_parser.jsonld_blocks)
        if job:
            job["url"] = job["url"] or job_url
            jobs.append(job)

    return jobs
