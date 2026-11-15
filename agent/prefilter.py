"""
High-Speed Rule-Based Pre-Filter for TabbyPatrol
Evaluates obvious tabs in < 1ms without calling an LLM:
- Obvious distractions (Reels, Shorts, TikTok, Netflix, Brainrot) -> instant "distraction"
- Search & Homepages (YouTube home, search queries, channel pages) -> instant "browsing"
- Trusted productive platforms (GitHub, LeetCode, ArXiv, Python docs) -> instant "approve"
- Ambiguous tabs return None -> routed directly to LangChain DeepAgent!
"""

import re
from typing import Dict, Any, Optional


class FastRulePreFilter:
    def __init__(self):
        # Intrinsically productive domains
        self.productive_domains = [
            "github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com",
            "stackexchange.com", "superuser.com", "leetcode.com", "hackerrank.com",
            "codeforces.com", "kaggle.com", "w3schools.com", "developer.mozilla.org",
            "geeksforgeeks.org", "dev.to", "pypi.org", "crates.io", "replit.com",
            "codepen.io", "arxiv.org", "scholar.google.com", "jstor.org",
            "sciencedirect.com", "ieee.org", "nature.com", "researchgate.net",
            "overleaf.com", "coursera.org", "edx.org", "ocw.mit.edu", "khanacademy.org",
            "gradescope.com", "piazza.com", "canvas", "blackboard", "notion.so",
            "figma.com", "trello.com", "linear.app", "docs.google.com", "sheets.google.com",
            "devpost.com", "mlh.io", "docs.python.org", "react.dev", "nodejs.org",
            "rust-lang.org", "fastapi.tiangolo.com"
        ]

        # Pure distraction domains
        self.distraction_domains = [
            "instagram.com", "tiktok.com", "9gag.com", "buzzfeed.com", "roblox.com",
            "crazygames.com", "coolmathgames.com", "netflix.com", "hulu.com",
            "disneyplus.com", "primevideo.com", "pinterest.com", "twitch.tv"
        ]

        # Hard distraction subreddits (Step 3 specification)
        # reddit.com/r/(memes|dankmemes|wallstreetbets|funny|shitposting|PoliticalHumor|gaming)
        self.reddit_distraction_subs = [
            "memes", "dankmemes", "wallstreetbets", "funny", "shitposting",
            "politicalhumor", "gaming"
        ]

        # YouTube entertainment clickbait patterns (Step 3 specification)
        # MrBeast, "I Spent", "$1 vs", "Survive", "Challenge", "Try Not to Laugh", "Skibidi", "Reaction"
        self.yt_entertainment_patterns = [
            "mrbeast", "mr beast", "i spent", "$1 vs", "survive", "survived",
            "challenge", "try not to laugh", "skibidi", "reaction video", "reacting to",
            "my reaction", "live reaction"
        ]

        # Well-known entertainment creators
        self.distraction_creators = [
            "mrbeast", "mr beast", "beast react", "beast reacts", "beast philanthropy",
            "sidemen", "ishowspeed", "kai cenat", "pewdiepie", "markiplier",
            "jacksepticeye", "ludwig", "xqc", "penguinz0", "moistcr1tikal",
            "logan paul", "jake paul", "dude perfect", "ssundee", "unspeakable",
            "prestonplayz"
        ]

        # Clear distraction phrases
        self.distraction_phrases = [
            "try not to laugh", "cat fails", "funny compilation", "funny moments",
            "100 days challenge", "$1 vs $", "i spent 7 days", "solitary confinement",
            "brainrot", "gta 6 official gameplay", "tiktok cringe", "r/memes",
            "r/dankmemes", "r/shitposting", "extreme hide and seek", "last to leave",
            "trapped in", "giving away", "survived 100 days", "survive 100 days",
            "survived 24 hours", "survive 24 hours", "stream highlights", "let's play",
            "speedrun", "asmr eating", "mukbang", "dating show", "celebrity drama",
            "skibidi toilet", "skibidi", "private jet", "hotel room"
        ]

        # Challenge and viral title regex patterns
        self.distraction_regexes = [
            re.compile(r"\b(i\s+spent|spent)\s+(\d+|\$[\d,]+)\b", re.IGNORECASE),
            re.compile(r"\bsurvive[d]?\s+\d+\s+(days|hours)\b", re.IGNORECASE),
            re.compile(r"\$[\d,]+\s+vs\s+\$[\d,]+", re.IGNORECASE),
            re.compile(r"\b1\s+vs\s+100\b", re.IGNORECASE),
            re.compile(r"\blast\s+to\s+leave\b", re.IGNORECASE),
            re.compile(r"\bfight[s]?\s+for\s+\$[\d,]+", re.IGNORECASE),
            re.compile(r"\bwin[s]?\s+\$[\d,]+", re.IGNORECASE),
            re.compile(r"\bgiving\s+away\s+(\$[\d,]+|\d+)", re.IGNORECASE),
            re.compile(r"\btrapped\s+in\b", re.IGNORECASE),
            re.compile(r"\bsolitary\s+confinement\b", re.IGNORECASE),
            re.compile(r"\bworld'?s\s+most\s+dangerous\b", re.IGNORECASE),
            re.compile(r"\b(cat|dog)\s+fails?\b", re.IGNORECASE),
            re.compile(r"\btiktok\s+compilation\b", re.IGNORECASE),
            re.compile(r"\bcringe\s+compilation\b", re.IGNORECASE),
            re.compile(r"\b(skibidi|brainrot)\b", re.IGNORECASE),
        ]

        # Unambiguous educational lecture phrases & creators (Approved before browsing!)
        self.lecture_phrases = [
            "full course", "full programming course", "crash course",
            "cs50", "mit opencourseware", "linear algebra, spring", "mit 18.06",
            "mit 6.006", "mit 6.", "mit ", "r/learnprogramming", "r/learnpython",
            "3blue1brown", "statquest", "freecodecamp", "traversy media", "fireship",
            "khan academy", "coursera", "edx", "karpathy", "andrew ng",
            "programming tutorial", "tutorial for beginners", "lecture 1", "lecture 0",
            "lecture 2", "algorithms", "data structures", "calculus", "organic chemistry"
        ]

        self.lecture_regexes = [
            re.compile(r"\bmit\s+(opencourseware|6\.\d+|18\.\d+|\d+\.\d+)\b", re.IGNORECASE),
            re.compile(r"\blecture\s+\d+\b", re.IGNORECASE),
            re.compile(r"\b(cs50|algorithms|calculus|linear\s+algebra|organic\s+chemistry)\b", re.IGNORECASE),
        ]

    def evaluate(self, title: str, url: str = "") -> Optional[Dict[str, Any]]:
        """
        Fast evaluation of tab title and URL:
        RULE ORDER (Step 2 & 3 specification):
        1. Hard distraction rules first
        2. Productive approvals second
        3. Browsing ONLY for true homepage / search / channel pages (exact path match, never /r/ or /watch)
        4. Ambiguous tabs return None -> routed to LangChain DeepAgent with 6s timeout!
        """
        lower_title = title.strip().lower()
        lower_url = url.strip().lower()
        clean_url = lower_url.split("#")[0].split("?")[0] if lower_url else ""
        raw_url = lower_url.split("#")[0]
        combined = f"{lower_title} {lower_url}"

        # -------------------------------------------------------------
        # 1. HARD DISTRACTION RULES FIRST (INSTANT POP)
        # -------------------------------------------------------------
        # 1a. Reddit hard distraction subreddits:
        # reddit.com/r/(memes|dankmemes|wallstreetbets|funny|shitposting|PoliticalHumor|gaming)
        sub_match = re.search(r"reddit\.com/r/([a-zA-Z0-9_]+)", raw_url)
        matched_sub = None
        if sub_match:
            cand = sub_match.group(1).lower()
            if cand in self.reddit_distraction_subs:
                matched_sub = cand
        if not matched_sub:
            for sub in self.reddit_distraction_subs:
                if (
                    f"r/{sub}" in lower_title or
                    lower_title == sub or
                    lower_title == f"r/{sub}" or
                    lower_title.startswith(f"{sub} ") or
                    lower_title.startswith(f"r/{sub} ") or
                    f": r/{sub}" in lower_title or
                    f"- r/{sub}" in lower_title or
                    f"{sub} - reddit" in lower_title or
                    f"r/{sub}" in raw_url
                ):
                    matched_sub = sub
                    break

        if matched_sub:
            return {
                "verdict": "distraction",
                "relevance_to_goal": 0.05,
                "reason": f"Distraction subreddit 'r/{matched_sub}' detected. Pop it! 🎯💥",
                "confidence": 0.98,
                "source": "prefilter",
                "topic": "Reddit Distraction"
            }

        # 1b. YouTube watch pages whose title matches entertainment patterns:
        # MrBeast, "I Spent", "$1 vs", "Survive", "Challenge", "Try Not to Laugh", "Skibidi", "Reaction"
        is_yt_watch = (
            "youtube.com/watch" in raw_url or
            "youtu.be/" in raw_url or
            "/watch?v=" in raw_url
        )
        is_yt_context = is_yt_watch or lower_title.endswith(" - youtube") or "youtube" in lower_title
        if is_yt_context:
            for ep in self.yt_entertainment_patterns:
                if ep in lower_title or ep in raw_url:
                    return {
                        "verdict": "distraction",
                        "relevance_to_goal": 0.05,
                        "reason": f"Entertainment video pattern '{ep}' detected on YouTube. Pop it! 🎯💥",
                        "confidence": 0.98,
                        "source": "prefilter",
                        "topic": "YouTube Entertainment"
                    }

        # 1c. Instagram, Shorts, TikTok, and other pure distractions
        if "instagram.com/reels" in raw_url or "reels • instagram" in lower_title or "instagram" in combined:
            return {
                "verdict": "distraction",
                "relevance_to_goal": 0.0,
                "reason": "Instagram & Reels detected. Short-form distraction - pop it! 🎯💥",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "Instagram & Reels"
            }

        if "/shorts" in raw_url or "#shorts" in raw_url or " - shorts" in lower_title:
            return {
                "verdict": "distraction",
                "relevance_to_goal": 0.0,
                "reason": "YouTube Shorts detected. Short-form distraction - pop it! 🎯💥",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "YouTube Shorts"
            }

        for dd in self.distraction_domains:
            if dd in raw_url or dd.replace(".com", "") in lower_title:
                return {
                    "verdict": "distraction",
                    "relevance_to_goal": 0.0,
                    "reason": f"Distraction entertainment domain '{dd}' detected. Pop it! 🎯💥",
                    "confidence": 1.0,
                    "source": "prefilter",
                    "topic": dd.replace(".com", "").capitalize()
                }

        for dp in self.distraction_phrases:
            if dp in lower_title or dp in raw_url:
                return {
                    "verdict": "distraction",
                    "relevance_to_goal": 0.05,
                    "reason": f"Entertainment clickbait '{dp}' detected. Pop it! 🎯💥",
                    "confidence": 0.98,
                    "source": "prefilter",
                    "topic": "Entertainment & Memes"
                }

        for dc in self.distraction_creators:
            if dc in lower_title or dc in raw_url:
                return {
                    "verdict": "distraction",
                    "relevance_to_goal": 0.05,
                    "reason": f"Entertainment creator '{dc}' detected off-goal. Pop it! 🎯💥",
                    "confidence": 0.98,
                    "source": "prefilter",
                    "topic": "Entertainment Creator"
                }

        for rx in self.distraction_regexes:
            if rx.search(lower_title) or rx.search(raw_url):
                return {
                    "verdict": "distraction",
                    "relevance_to_goal": 0.05,
                    "reason": "Viral entertainment challenge / stunt pattern detected off-goal. Pop it! 🎯💥",
                    "confidence": 0.98,
                    "source": "prefilter",
                    "topic": "Viral Entertainment Challenge"
                }

        # -------------------------------------------------------------
        # 2. PRODUCTIVE PLATFORMS & EDUCATIONAL LECTURES
        # -------------------------------------------------------------
        # YouTube Creator Channel browsing (exact channel paths: /@, /channel/, /c/)
        is_youtube = ("youtube.com" in raw_url or "youtu.be" in raw_url or "youtube" in lower_title)
        if is_youtube and ("/watch" not in raw_url and "watch?v=" not in raw_url) and ("/@" in raw_url or "/channel/" in raw_url or "/c/" in raw_url):
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "YouTube creator channel detected. Allowed to browse videos! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "YouTube Channel"
            }

        for pd in self.productive_domains:
            if pd in raw_url or pd.replace(".com", "") in lower_title:
                return {
                    "verdict": "approve",
                    "relevance_to_goal": 0.95,
                    "reason": f"Verified productive platform '{pd}'. Approved - let it pass! 📚✨",
                    "confidence": 1.0,
                    "source": "prefilter",
                    "topic": "Academic & Engineering Tools"
                }

        for lp in self.lecture_phrases:
            if lp in lower_title or lp in raw_url:
                return {
                    "verdict": "approve",
                    "relevance_to_goal": 0.95,
                    "reason": f"Structured course/lecture detected ('{lp}'). Approved! 📚✨",
                    "confidence": 0.98,
                    "source": "prefilter",
                    "topic": "Educational Lecture"
                }

        for rx in self.lecture_regexes:
            if rx.search(lower_title) or rx.search(raw_url):
                return {
                    "verdict": "approve",
                    "relevance_to_goal": 0.95,
                    "reason": "Academic course or lecture series detected. Approved! 📚✨",
                    "confidence": 0.98,
                    "source": "prefilter",
                    "topic": "Educational Lecture"
                }

        # -------------------------------------------------------------
        # 3. BROWSING ONLY FOR TRUE HOMEPAGE / SEARCH / CHANNEL (EXACT PATH MATCH)
        # -------------------------------------------------------------
        pure_home_titles = [
            "youtube", "youtube - google chrome", "youtube - microsoft edge", "youtube - brave",
            "reddit", "reddit - dive into anything", "reddit - the heart of the internet",
            "reddit: the front page of the internet", "x", "twitter", "home / x", "home / twitter",
            "google", "google search", "new tab", "about:blank", "bing", "duckduckgo"
        ]
        if lower_title in pure_home_titles or re.match(r"^\(\d+\)\s*youtube(\s*-\s*(google chrome|microsoft edge|brave))?$", lower_title):
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": f"Homepage '{title}' detected. Allowed to scroll and browse! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "Homepage Browsing"
            }

        if lower_title.startswith("search - ") or lower_title == "search" or "search results" in lower_title:
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "Search interface detected. Allowed to scroll and search! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "Search Interface"
            }

        # Search engine queries
        if any(se in raw_url for se in ["google.com/search", "bing.com/search", "duckduckgo.com"]):
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "Search query detected. Allowed to scroll and search! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "Web Search"
            }

        # YouTube: ONLY homepage, search query, or channel (EXACT PATH, NEVER /watch)
        clean_url_no_slash = clean_url.rstrip("/")
        if clean_url_no_slash in ["https://www.youtube.com", "https://youtube.com", "http://www.youtube.com", "http://youtube.com"]:
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "YouTube homepage detected. Allowed to scroll recommendations! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "YouTube Homepage"
            }
        if "results?search_query" in raw_url:
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "YouTube search query detected. Allowed to scroll and search! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "YouTube Search"
            }

        # Reddit: ONLY homepage (EXACT PATH, NEVER /r/)
        if clean_url_no_slash in ["https://www.reddit.com", "https://reddit.com", "http://www.reddit.com", "http://reddit.com"]:
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "Reddit homepage detected. Allowed to browse! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "Reddit Homepage"
            }
        if "reddit.com/search" in raw_url:
            return {
                "verdict": "browsing",
                "relevance_to_goal": 0.5,
                "reason": "Reddit search query detected. Allowed to scroll and search! 🔍",
                "confidence": 1.0,
                "source": "prefilter",
                "topic": "Reddit Search"
            }

        # Ambiguous tab (other reddit.com/r/ and other youtube.com/watch) -> routed to DeepAgent!
        return None
