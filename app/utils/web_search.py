"""
Web Search Integration for Sanctions Checking
Provides multiple methods to search the web for sanctions information
"""

import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class WebSearchService:
    """
    Web search service with multiple providers
    """

    def __init__(self):
        # API keys for different search providers
        self.serper_api_key = os.getenv("SERPER_API_KEY")  # serper.dev
        self.serpapi_key = os.getenv("SERPAPI_KEY")  # serpapi.com
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")  # tavily.com

    async def search_serper(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search using Serper.dev (Google Search API)
        Free tier: 2,500 queries/month
        Sign up: https://serper.dev
        """
        if not self.serper_api_key:
            return []

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": num_results
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Extract organic results
                results = []
                for item in data.get("organic", [])[:num_results]:
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "source": "serper"
                    })

                return results

        except Exception as e:
            print(f"Serper search error: {str(e)}")
            return []

    async def search_serpapi(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search using SerpAPI (Google Search API)
        Free tier: 100 queries/month
        Sign up: https://serpapi.com
        """
        if not self.serpapi_key:
            return []

        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "num": num_results,
            "engine": "google"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Extract organic results
                results = []
                for item in data.get("organic_results", [])[:num_results]:
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "source": "serpapi"
                    })

                return results

        except Exception as e:
            print(f"SerpAPI search error: {str(e)}")
            return []

    async def search_tavily(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search using Tavily AI (AI-powered search)
        Optimized for AI applications
        Sign up: https://tavily.com
        """
        if not self.tavily_api_key:
            return []

        url = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "max_results": num_results,
            "search_depth": "advanced",
            "include_domains": [
                "ofac.treasury.gov",
                "un.org",
                "europa.eu",
                "state.gov"
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Extract results
                results = []
                for item in data.get("results", [])[:num_results]:
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("url"),
                        "snippet": item.get("content"),
                        "source": "tavily"
                    })

                return results

        except Exception as e:
            print(f"Tavily search error: {str(e)}")
            return []

    async def search_sanctions(self, country: str, port: str = None, product: str = None) -> Dict:
        """
        Search for sanctions information using available providers
        Tries multiple providers for redundancy
        """
        # Build search query
        query_parts = [f"{country} sanctions", "OFAC", "UN"]
        if port:
            query_parts.append(f"{port} port")
        if product:
            query_parts.append(f"{product} export control")

        query = " ".join(query_parts)

        # Try each provider in order
        results = []

        # Try Serper first (best for Google search)
        if self.serper_api_key:
            results = await self.search_serper(query, num_results=5)

        # Fallback to SerpAPI
        if not results and self.serpapi_key:
            results = await self.search_serpapi(query, num_results=5)

        # Fallback to Tavily
        if not results and self.tavily_api_key:
            results = await self.search_tavily(query, num_results=5)

        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "searched_at": datetime.now().isoformat(),
            "provider": results[0]["source"] if results else "none"
        }

    async def fetch_official_sanctions_lists(self) -> Dict:
        """
        Fetch content directly from official sanctions websites
        """
        official_sources = {
            "ofac": "https://sanctionssearch.ofac.treas.gov/",
            "un": "https://www.un.org/securitycouncil/sanctions/",
            "eu": "https://www.sanctionsmap.eu/"
        }

        results = {}

        async with httpx.AsyncClient(timeout=10.0) as client:
            for name, url in official_sources.items():
                try:
                    response = await client.get(url)
                    results[name] = {
                        "status": "accessible",
                        "url": url,
                        "status_code": response.status_code
                    }
                except Exception as e:
                    results[name] = {
                        "status": "error",
                        "url": url,
                        "error": str(e)
                    }

        return results


class DuckDuckGoSearch:
    """
    Free alternative using DuckDuckGo (no API key required)
    """

    async def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search using DuckDuckGo HTML API (free, no key required)
        """
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, data=params, follow_redirects=True)
                response.raise_for_status()

                # Parse HTML (simplified - in production use BeautifulSoup)
                results = []
                # Note: This is a simplified example
                # In production, use BeautifulSoup to parse HTML properly

                return results

        except Exception as e:
            print(f"DuckDuckGo search error: {str(e)}")
            return []


# Free tier comparison
"""
SEARCH PROVIDERS COMPARISON:

1. Serper.dev (Recommended)
   - Free tier: 2,500 queries/month
   - Best Google results
   - Easy to use
   - Sign up: https://serper.dev
   - Cost: Free tier available

2. SerpAPI
   - Free tier: 100 queries/month
   - Good quality
   - Sign up: https://serpapi.com
   - Cost: Free tier, then $50/month

3. Tavily AI
   - AI-optimized search
   - Good for compliance queries
   - Sign up: https://tavily.com
   - Cost: Paid plans

4. DuckDuckGo
   - Completely free
   - No API key needed
   - Lower quality results
   - Good for fallback

RECOMMENDATION:
Start with Serper.dev (2,500 free queries/month)
"""
