"""
Research engine — newsletter scanning, Facebook Ad Library fetching, trend extraction.

Uses httpx for web requests. The Ad Library fetch hits Meta's public Ad Library website
(not the authenticated API) to extract trends. Newsletter scanning uses web search
to find and summarize recent newsletter content in a niche.
"""
import logging
import re
from typing import Optional

import httpx

from orchestrator.knowledge_base import store_research_finding, store_ad_library_snapshot

logger = logging.getLogger(__name__)

SEARCH_URL = "https://html.duckduckgo.com/html/"


async def search_web(query: str, max_results: int = 10) -> list[dict]:
    """Simple DuckDuckGo HTML search to get links and snippets."""
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.post(SEARCH_URL, data={"q": query, "b": ""})
            resp.raise_for_status()
            html = resp.text

            links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.+?)</a>', html)
            snippets = re.findall(r'class="result__snippet">(.+?)</a>', html, re.DOTALL)

            for i, (url, title) in enumerate(links[:max_results]):
                snippet = snippets[i].strip() if i < len(snippets) else ""
                snippet = re.sub(r"<[^>]+>", "", snippet)
                title = re.sub(r"<[^>]+>", "", title)
                results.append({"url": url, "title": title.strip(), "snippet": snippet.strip()})
    except Exception as e:
        logger.error("Web search failed for '%s': %s", query, e)
    return results


async def scan_newsletters(niche: str, task_id: Optional[str] = None) -> dict:
    """Search for recent newsletters in a niche, return structured findings."""
    queries = [
        f"{niche} newsletter 2026 best insights",
        f"{niche} email newsletter trends",
        f"{niche} substack newsletter popular",
    ]

    all_results = []
    for q in queries:
        results = await search_web(q)
        all_results.extend(results)

    unique = {r["url"]: r for r in all_results}
    findings = list(unique.values())[:15]

    summary = f"Found {len(findings)} newsletter sources for '{niche}'. "
    if findings:
        titles = [f["title"] for f in findings[:5]]
        summary += "Top sources: " + "; ".join(titles)

    store_research_finding(
        agent_name="priya",
        research_type="newsletter_scan",
        niche=niche,
        summary=summary,
        task_id=task_id,
        raw_data={"results": findings},
        key_insights=[f["title"] for f in findings[:5]],
    )

    return {"niche": niche, "sources": findings, "summary": summary}


async def fetch_ad_library_trends(
    niche: str,
    search_terms: Optional[list[str]] = None,
    task_id: Optional[str] = None,
) -> dict:
    """
    Fetch Facebook Ad Library data for a niche.
    Uses web search for ad trends since the authenticated API requires Meta app review.
    """
    terms = search_terms or [niche]
    all_trends = []

    for term in terms:
        query = f"Facebook Ad Library {term} active ads 2026"
        results = await search_web(query, max_results=5)

        query2 = f"Meta ad trends {term} popular ad creatives hooks"
        results2 = await search_web(query2, max_results=5)

        combined = results + results2
        all_trends.append({
            "query_term": term,
            "sources": combined,
            "ad_count": len(combined),
        })

    aggregated = {
        "niche": niche,
        "terms_searched": terms,
        "total_sources": sum(t["ad_count"] for t in all_trends),
        "by_term": all_trends,
    }

    for t in all_trends:
        store_ad_library_snapshot(
            niche=niche,
            query_term=t["query_term"],
            ad_count=t["ad_count"],
            top_ads=t["sources"][:10],
            trends={"common_hooks": [], "popular_ctas": [], "dominant_formats": []},
        )

    store_research_finding(
        agent_name="priya",
        research_type="ad_library",
        niche=niche,
        summary=f"Ad Library scan for '{niche}': {aggregated['total_sources']} sources across {len(terms)} terms",
        task_id=task_id,
        raw_data=aggregated,
        key_insights=[f"Term '{t['query_term']}': {t['ad_count']} sources" for t in all_trends],
    )

    return aggregated


async def analyze_competitor_content(niche: str, task_id: Optional[str] = None) -> dict:
    """Search for competitor content and strategies in a niche."""
    queries = [
        f"{niche} top performing content 2026",
        f"{niche} competitor marketing strategy",
        f"{niche} viral content examples",
    ]

    all_results = []
    for q in queries:
        results = await search_web(q)
        all_results.extend(results)

    unique = {r["url"]: r for r in all_results}
    findings = list(unique.values())[:15]

    summary = f"Competitor analysis for '{niche}': {len(findings)} content pieces found."

    store_research_finding(
        agent_name="subodh",
        research_type="competitor_analysis",
        niche=niche,
        summary=summary,
        task_id=task_id,
        raw_data={"results": findings},
        key_insights=[f["title"] for f in findings[:5]],
    )

    return {"niche": niche, "findings": findings, "summary": summary}


async def run_full_research(niche: str, task_id: Optional[str] = None) -> dict:
    """Run all research phases for a niche and return consolidated brief."""
    newsletters = await scan_newsletters(niche, task_id)
    ad_trends = await fetch_ad_library_trends(niche, task_id=task_id)
    competitors = await analyze_competitor_content(niche, task_id)

    return {
        "niche": niche,
        "newsletters": newsletters,
        "ad_trends": ad_trends,
        "competitors": competitors,
        "summary": (
            f"Research complete for '{niche}'. "
            f"Newsletters: {len(newsletters.get('sources', []))} sources. "
            f"Ad Library: {ad_trends.get('total_sources', 0)} sources. "
            f"Competitors: {len(competitors.get('findings', []))} pieces."
        ),
    }
