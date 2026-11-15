"""
TabbyPatrol - Tab Content & Task Classifier
Differentiates between PRODUCTIVE TASKS (educational videos, reading advice, tutorials, documentation)
and WASTEFUL TASKS (scrolling shorts/reels, funny videos, odd reddit articles, memes).
Explicitly separates every tab under monitored/blocked domains into productive and wasteful tasks.
"""

import re
from urllib.parse import urlparse


def clean_browser_title(title: str) -> str:
    """Strips browser process and vendor suffixes from window titles."""
    if not title:
        return ""
    title = title.strip()
    suffixes = [
        " - Google Chrome",
        " - Microsoft​ Edge",
        " - Microsoft Edge",
        " - Mozilla Firefox",
        " - Brave",
        " - Opera",
        " - Vivaldi"
    ]
    for s in suffixes:
        if title.endswith(s):
            title = title[:-len(s)].strip()
    return title


def extract_domain(url: str, title: str = "") -> str:
    """Extracts a clean domain or service name from URL or title."""
    if url:
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            if host:
                return host
        except Exception:
            pass

    t_lower = (title or "").lower()
    known_services = {
        "youtube": "youtube.com",
        "reddit": "reddit.com",
        "wikipedia": "wikipedia.org",
        "github": "github.com",
        "stackoverflow": "stackoverflow.com",
        "instagram": "instagram.com",
        "tiktok": "tiktok.com",
        "twitch": "twitch.tv",
        "netflix": "netflix.com",
        "twitter": "x.com",
        "x.com": "x.com",
        "amazon": "amazon.com",
        "hacker news": "news.ycombinator.com"
    }
    for name, domain in known_services.items():
        if name in t_lower:
            return domain
    return ""


class TabContentRecognizer:
    def __init__(self):
        self.cache = {}

        # 1. Productive Educational YouTube keywords & creators
        self.yt_edu_terms = [
            "lecture", "course", "tutorial", "class", "mit ", "stanford", "harvard",
            "cs50", "3blue1brown", "veritasium", "kurzgesagt", "crash course", "khan academy",
            "ted-ed", "ted talk", "numberphile", "freecodecamp", "algorithm", "calculus",
            "physics", "chemistry", "biology", "neuroscience", "machine learning",
            "deep learning", "artificial intelligence", "data structures", "organic chemistry",
            "how to", "step by step", "full course", "explained", "documentary", "history of",
            "linear algebra", "differential equations", "quantum", "computer science",
            "discrete math", "astronomy", "biochemistry", "python tutorial", "advice",
            "career advice", "career", "study tips", "how i", "guide", "productivity",
            "coding", "deep dive", "programming", "engineering", "math", "science",
            "lesson", "exam prep", "interview prep", "book summary", "analysis",
            "fireship", "traversy media", "sentdex", "lex fridman", "huberman", "ali abdaal"
        ]

        # 2. Wasteful / Funny / Clickbait / Gaming YouTube keywords
        self.yt_wasteful_terms = [
            "mrbeast", "i spent", "$1 vs", "in 100 days", "survived", "challenge",
            "try not to laugh", "laugh", "prank", "vlog", "react", "reaction", "meme",
            "fails", "cringe", "tiktok compilation", "speedrun", "gameplay", "walkthrough",
            "minecraft", "gta", "roblox", "fortnite", "unboxing", "haul", "mukbang",
            "gossip", "drama", "sidemen", "pewdiepie", "logan paul", "jake paul",
            "streamer", "funny moments", "funny", "bloopers", "comedy", "sketch",
            "roast", "parody", "odd", "weirdest", "craziest", "cat fails", "dog fails",
            "compilation", "satisfying", "shorts", "#shorts"
        ]

        # 3. Productive Reddit Subreddits (Advice, Career, Education, Tech, Science)
        self.reddit_advice_subreddits = {
            # Life & Career Advice
            "advice", "needadvice", "careerguidance", "cscareerquestions", "jobs", "resumes",
            "personalfinance", "financialindependence", "frugal", "fitness", "getdisciplined",
            "productivity", "decidingtobettermyself", "selfimprovement", "education", "college",
            "gradschool", "askengineers", "engineering",
            # Tech & Programming
            "learnprogramming", "programming", "python", "datascience", "machinelearning",
            "compsci", "webdev", "reactjs", "cpp", "rust", "algorithms", "math", "science",
            "physics", "chemistry", "askscience", "explainlikeimfive", "devops", "linux",
            "sysadmin", "artificial", "statistics", "computerscience", "coding"
        }

        # 4. Reddit Advice title cues
        self.reddit_advice_keywords = [
            "advice", "how do i", "how to", "tips", "guide", "guide to", "best way to",
            "recommendations", "help with", "career", "interview", "learning", "studying",
            "troubleshooting", "question about", "best practices", "how can i", "resume",
            "suggestion", "improve", "schedule", "routine", "fix my"
        ]

        # 5. Wasteful / Odd Reddit Subreddits (Memes, odd articles, time-sinks, drama)
        self.reddit_wasteful_subreddits = {
            # Memes & Humor
            "memes", "dankmemes", "funny", "gifs", "shitposting", "wholesomememes",
            "comedyheaven", "humor", "me_irl",
            # Odd / Weird / Time-sink rabbit holes
            "mildlyinteresting", "interestingasfuck", "damnthatsinteresting", "oddlysatisfying",
            "oddlyterrifying", "tifu", "amitheasshole", "aita", "confession", "drama",
            "publicfreakout", "facepalm", "teenagers", "crazyfuckingvideos", "wallstreetbets",
            "gaming", "aww", "mildlyinfuriating", "crappydesign", "diwhy", "cursedimages"
        }

        # 6. Wasteful Reddit title cues
        self.reddit_wasteful_keywords = [
            "odd", "bizarre", "weird", "insane", "shocking", "cursed", "wtf", "lol",
            "hilarious", "funny", "fails", "craziest", "tifu", "spilling", "potato shaped",
            "peeling", "meme", "when the code", "satisfying", "distraction"
        ]

    def analyze_tab(self, raw_title: str, url: str = "", custom_blocked: list = None) -> dict:
        """
        Analyzes the active tab title and URL.
        Separates tabs on monitored/blocked domains into PRODUCTIVE TASKS or WASTEFUL TASKS.
        """
        clean_title = clean_browser_title(raw_title)
        if not clean_title and not url:
            return {
                "title": "Empty Tab",
                "url": "",
                "domain": "",
                "site": "Browser",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": "Empty Tab",
                "about": "New or blank browser tab.",
                "category": "🌐 Browser",
                "is_distraction": False,
                "bubble_text": "Observing desktop... 🐾"
            }

        cache_key = f"{clean_title}||{url}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        lower_title = clean_title.lower()
        url_lower = (url or "").lower()
        domain = extract_domain(url, clean_title)

        result = self._classify_task(clean_title, lower_title, url, url_lower, domain, custom_blocked)

        if len(self.cache) > 200:
            self.cache.clear()
        self.cache[cache_key] = result
        return result

    def _classify_task(self, clean_title, lower_title, url, url_lower, domain, custom_blocked):
        # 1. YOUTUBE CLASSIFICATION
        if "youtube" in lower_title or "youtube.com" in domain:
            return self._classify_youtube(clean_title, lower_title, url_lower)

        # 2. REDDIT CLASSIFICATION
        if "reddit" in lower_title or "reddit.com" in domain:
            return self._classify_reddit(clean_title, lower_title, url_lower)

        # 3. INSTAGRAM & REELS
        if "instagram.com" in domain or "instagram" in lower_title:
            return self._classify_instagram(clean_title, url_lower)

        # 4. TIKTOK
        if "tiktok.com" in domain or "tiktok" in lower_title:
            return self._classify_tiktok(clean_title)

        # 5. TWITCH
        if "twitch.tv" in domain or "twitch" in lower_title:
            return self._classify_twitch(clean_title, lower_title)

        # 6. NETFLIX & STREAMING
        if any(d in domain for d in ["netflix.com", "hulu.com", "disneyplus.com", "primevideo.com"]) or any(k in lower_title for k in ["netflix", "hulu"]):
            return self._classify_streaming(clean_title, domain)

        # 7. TWITTER / X
        if any(d in domain for d in ["x.com", "twitter.com"]) or "twitter" in lower_title:
            return self._classify_twitter(clean_title, lower_title)

        # 8. WIKIPEDIA & ENCYCLOPEDIAS (Always Productive)
        if "wikipedia" in lower_title or "wikipedia.org" in domain:
            return self._classify_wikipedia(clean_title)

        # 9. DEVELOPER & CODING SITES (Always Productive)
        if any(d in domain for d in ["github.com", "gitlab.com", "stackoverflow.com", "leetcode.com", "hackerrank.com", "docs.python.org", "developer.mozilla.org"]):
            return self._classify_developer(clean_title, domain)

        # 10. GENERAL SITES & CUSTOM BLOCKED RULES
        return self._classify_general(clean_title, lower_title, domain, custom_blocked)

    def _classify_youtube(self, clean_title, lower_title, url_lower):
        v_title = re.sub(r"\s*-\s*youtube$", "", clean_title, flags=re.IGNORECASE).strip()
        v_lower = v_title.lower()

        # Homepage or Search
        if v_lower in ["", "youtube", "home"] or url_lower in ["https://www.youtube.com/", "https://youtube.com/"]:
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "youtube.com",
                "site": "YouTube",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": "YouTube Homepage",
                "about": "Browsing and navigating video catalog on YouTube.",
                "category": "🎬 Video Platform",
                "is_distraction": False,
                "bubble_text": "Browsing YouTube home 🔍"
            }

        if v_lower.startswith("search") or "results?search_query=" in url_lower:
            query = v_title.replace("Search - ", "").replace("Search", "").strip() or "videos"
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "youtube.com",
                "site": "YouTube",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": f"Searching: {query}",
                "about": f"Searching YouTube video catalog for '{query}'.",
                "category": "🔍 Search",
                "is_distraction": False,
                "bubble_text": f"Searching: {query[:25]} 🔍"
            }

        # YouTube Shorts -> WASTEFUL TASK
        if "/shorts/" in url_lower or "#shorts" in v_lower:
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "youtube.com",
                "site": "YouTube Shorts",
                "task_type": "WASTEFUL",
                "task_label": "🎯 WASTEFUL TASK",
                "topic": v_title,
                "about": f"Scrolling short-form video reels on YouTube Shorts: '{v_title}'.",
                "category": "📱 Short-Form Distraction",
                "is_distraction": True,
                "bubble_text": "Wasteful task: YouTube Shorts! 🎯💥"
            }

        # Check Educational keywords
        is_edu = any(t in v_lower for t in self.yt_edu_terms)

        # Check for explicitly Wasteful content (Shorts, funny fails, clickbait, challenges, MrBeast, gaming)
        is_wasteful = False
        for t in self.yt_wasteful_terms:
            if t in v_lower:
                # Do not trigger wasteful for chemical reaction / science reaction mechanisms
                if t in ["react", "reaction"] and ("reaction mechanism" in v_lower or "chemical reaction" in v_lower or "chemistry" in v_lower or is_edu):
                    continue
                is_wasteful = True
                break

        # Priority protection for educational videos
        if is_edu and not any(k in v_lower for k in ["funny fails", "try not to laugh", "prank", "mrbeast"]):
            is_wasteful = False

        if is_wasteful:
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "youtube.com",
                "site": "YouTube",
                "task_type": "WASTEFUL",
                "task_label": "🎯 WASTEFUL TASK",
                "topic": v_title,
                "about": f"Funny video, entertainment stunt, or gaming clickbait on YouTube: '{v_title}'.",
                "category": "🎮 Entertainment / Distraction",
                "is_distraction": True,
                "bubble_text": f"Wasteful task: Funny/Entertainment Video! 🎯"
            }
        else:
            # Everything else on YouTube is PRODUCTIVE: educational lectures, tutorials, courses, science,
            # career advice, documentaries, explainers, focus music, learning videos!
            is_explicit_edu = any(t in v_lower for t in self.yt_edu_terms)
            about_desc = (
                f"Educational YouTube video / tutorial covering academic or skill topic: '{v_title}'."
                if is_explicit_edu else
                f"Watching educational/knowledge video on YouTube: '{v_title}'."
            )
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "youtube.com",
                "site": "YouTube",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": v_title,
                "about": about_desc,
                "category": "🎓 Education & Learning",
                "is_distraction": False,
                "bubble_text": f"Productive task: Educational Video ({v_title[:24]}...) 📚✨"
            }

    def _classify_reddit(self, clean_title, lower_title, url_lower):
        clean_name = re.sub(r"\s*-\s*reddit$", "", clean_title, flags=re.IGNORECASE).strip()
        combined = f"{clean_title} {url_lower}".lower()

        # Extract subreddit name
        sub_match = re.search(r"(?:reddit\.com/r/|r/)([a-zA-Z0-9_]+)", combined)
        sub_name = sub_match.group(1).lower() if sub_match else ""

        # Reddit Homepage
        if clean_name.lower() in ["", "reddit", "reddit - dive into anything"]:
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "reddit.com",
                "site": "Reddit",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": "Reddit Homepage",
                "about": "Browsing community front page on Reddit.",
                "category": "💬 Social Community",
                "is_distraction": False,
                "bubble_text": "Browsing Reddit home 🔍"
            }

        # Check for explicitly Wasteful / Odd / Meme Reddit content
        is_wasteful_sub = sub_name in self.reddit_wasteful_subreddits
        has_wasteful_kw = any(k in combined for k in self.reddit_wasteful_keywords)

        if is_wasteful_sub or has_wasteful_kw:
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "reddit.com",
                "site": "Reddit",
                "task_type": "WASTEFUL",
                "task_label": "🎯 WASTEFUL TASK",
                "topic": f"r/{sub_name or 'memes'}: {clean_name}",
                "about": f"Scrolling funny memes or reading odd time-sink Reddit articles on r/{sub_name or 'reddit'}: '{clean_name}'.",
                "category": "💬 Odd Articles & Memes",
                "is_distraction": True,
                "bubble_text": f"Wasteful task: Odd Reddit Articles / Memes! 🎯"
            }
        else:
            # Everything else on Reddit is PRODUCTIVE: reading advice, technical discussions, career tips,
            # Q&As, community learning, self-improvement, science, news!
            is_explicit_advice = (sub_name in self.reddit_advice_subreddits) or any(k in combined for k in self.reddit_advice_keywords)
            about_desc = (
                f"Reading Reddit advice and career/learning discussions on r/{sub_name or 'advice'}: '{clean_name}'."
                if is_explicit_advice else
                f"Reading knowledge discussion and community Q&A on r/{sub_name or 'reddit'}: '{clean_name}'."
            )
            return {
                "title": clean_title,
                "url": url_lower,
                "domain": "reddit.com",
                "site": "Reddit",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": f"r/{sub_name or 'reddit'}: {clean_name}",
                "about": about_desc,
                "category": "💡 Advice & Learning",
                "is_distraction": False,
                "bubble_text": f"Productive task: Reading Reddit Advice on r/{sub_name or 'reddit'}! 💡"
            }

    def _classify_instagram(self, clean_title, url_lower):
        is_reels = "/reels" in url_lower or "reels" in clean_title.lower()
        detail = "Scrolling Instagram Reels" if is_reels else "Browsing Instagram photos and stories"
        return {
            "title": clean_title,
            "url": url_lower,
            "domain": "instagram.com",
            "site": "Instagram",
            "task_type": "WASTEFUL",
            "task_label": "🎯 WASTEFUL TASK",
            "topic": "Instagram Reels & Feed",
            "about": f"{detail} - short-form social media distraction.",
            "category": "📱 Social Media / Reels",
            "is_distraction": True,
            "bubble_text": "Wasteful task: Scrolling Instagram Reels! 🎯"
        }

    def _classify_tiktok(self, clean_title):
        return {
            "title": clean_title,
            "url": "",
            "domain": "tiktok.com",
            "site": "TikTok",
            "task_type": "WASTEFUL",
            "task_label": "🎯 WASTEFUL TASK",
            "topic": "TikTok Video Stream",
            "about": "Scrolling short-form viral videos and brainrot algorithms on TikTok.",
            "category": "📱 Viral Short-Form Video",
            "is_distraction": True,
            "bubble_text": "Wasteful task: Scrolling TikTok! 🎯"
        }

    def _classify_twitch(self, clean_title, lower_title):
        is_coding = any(k in lower_title for k in ["coding", "programming", "development", "python", "software"])
        if is_coding:
            return {
                "title": clean_title,
                "url": "",
                "domain": "twitch.tv",
                "site": "Twitch",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": clean_title,
                "about": f"Watching live software development or educational coding stream on Twitch: '{clean_title}'.",
                "category": "💻 Live Coding Stream",
                "is_distraction": False,
                "bubble_text": "Productive task: Live Coding Stream! 💻"
            }
        else:
            return {
                "title": clean_title,
                "url": "",
                "domain": "twitch.tv",
                "site": "Twitch",
                "task_type": "WASTEFUL",
                "task_label": "🎯 WASTEFUL TASK",
                "topic": clean_title,
                "about": f"Watching live video gaming stream on Twitch: '{clean_title}'.",
                "category": "🎮 Live Gaming Stream",
                "is_distraction": True,
                "bubble_text": "Wasteful task: Twitch Gaming Stream! 🎯"
            }

    def _classify_streaming(self, clean_title, domain):
        return {
            "title": clean_title,
            "url": "",
            "domain": domain or "netflix.com",
            "site": "Streaming Entertainment",
            "task_type": "WASTEFUL",
            "task_label": "🎯 WASTEFUL TASK",
            "topic": clean_title,
            "about": f"Streaming movie or episodic entertainment TV series: '{clean_title}'.",
            "category": "🍿 Movies & Television",
            "is_distraction": True,
            "bubble_text": "Wasteful task: Streaming Movies/TV! 🎯"
        }

    def _classify_twitter(self, clean_title, lower_title):
        is_tech = any(k in lower_title for k in ["paper", "release", "announcement", "arxiv", "ai", "research"])
        if is_tech:
            return {
                "title": clean_title,
                "url": "",
                "domain": "x.com",
                "site": "X / Twitter",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": clean_title,
                "about": f"Reading tech research / release announcement on X/Twitter: '{clean_title}'.",
                "category": "💻 Tech Announcements",
                "is_distraction": False,
                "bubble_text": "Productive task: Tech Announcement! 💡"
            }
        else:
            return {
                "title": clean_title,
                "url": "",
                "domain": "x.com",
                "site": "X / Twitter",
                "task_type": "WASTEFUL",
                "task_label": "🎯 WASTEFUL TASK",
                "topic": clean_title,
                "about": "Scrolling social feed, timeline drama, and tweets on X/Twitter.",
                "category": "🐦 Social Media",
                "is_distraction": True,
                "bubble_text": "Wasteful task: Scrolling Twitter/X! 🎯"
            }

    def _classify_wikipedia(self, clean_title):
        article_name = re.sub(r"\s*-\s*wikipedia$", "", clean_title, flags=re.IGNORECASE).strip()
        return {
            "title": clean_title,
            "url": "",
            "domain": "wikipedia.org",
            "site": "Wikipedia",
            "task_type": "PRODUCTIVE",
            "task_label": "🟢 PRODUCTIVE TASK",
            "topic": article_name,
            "about": f"Encyclopedia research article covering: '{article_name}'.",
            "category": "📚 Encyclopedia & Reference",
            "is_distraction": False,
            "bubble_text": f"Productive task: Researching {article_name[:24]}... 📚"
        }

    def _classify_developer(self, clean_title, domain):
        return {
            "title": clean_title,
            "url": "",
            "domain": domain,
            "site": "Developer Platform",
            "task_type": "PRODUCTIVE",
            "task_label": "🟢 PRODUCTIVE TASK",
            "topic": clean_title,
            "about": f"Coding, troubleshooting technical issues, or studying documentation: '{clean_title}'.",
            "category": "💻 Software Engineering",
            "is_distraction": False,
            "bubble_text": f"Productive task: Coding & Docs 💻"
        }

    def _classify_general(self, clean_title, lower_title, domain, custom_blocked):
        # Search engine
        if any(s in lower_title for s in ["google search", "bing search", "duckduckgo"]):
            q = clean_title.split("-")[0].replace("Google", "").replace("Bing", "").strip() or "web"
            return {
                "title": clean_title,
                "url": "",
                "domain": domain or "google.com",
                "site": "Search Engine",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": f"Searching: {q}",
                "about": f"Conducting web search query for '{q}'.",
                "category": "🔍 Search Engine",
                "is_distraction": False,
                "bubble_text": f"Searching: {q[:25]} 🔍"
            }

        # Check custom blocked keywords
        is_wasteful = False
        matched_kw = ""
        if custom_blocked:
            for kw in custom_blocked:
                clean_kw = kw.strip().lower()
                if clean_kw and (clean_kw in lower_title or (domain and clean_kw in domain)):
                    is_wasteful = True
                    matched_kw = clean_kw
                    break

        if is_wasteful:
            return {
                "title": clean_title,
                "url": "",
                "domain": domain or "blocked",
                "site": domain or "Web",
                "task_type": "WASTEFUL",
                "task_label": "🎯 WASTEFUL TASK",
                "topic": clean_title,
                "about": f"Custom blocked wasteful site matching rule '{matched_kw}': '{clean_title}'.",
                "category": "🎯 Blocked Distraction",
                "is_distraction": True,
                "bubble_text": f"Wasteful task: {clean_title[:24]}! 🎯"
            }
        else:
            return {
                "title": clean_title,
                "url": "",
                "domain": domain or "web",
                "site": domain or "Web",
                "task_type": "PRODUCTIVE",
                "task_label": "🟢 PRODUCTIVE TASK",
                "topic": clean_title,
                "about": f"Reading webpage: '{clean_title}'.",
                "category": "🌐 Web Page",
                "is_distraction": False,
                "bubble_text": f"Productive task: {clean_title[:25]} 🌐"
            }
