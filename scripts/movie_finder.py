import requests
import time
import json
import os
import urllib.parse

target_total = 1500

subreddits = [
    "movies", "cinema", "film", "flicks", "moviedetails", "letterboxd", "moviereviews", "moviecritic"
]

keywords = [
    "predator badlands", "predator: badlands",
    "wicked: for good", "wicked for good","sinners",
    "nuremberg", "fantastic four: first steps", "fantastic 4: first steps"
]

results = []
seen_ids = set()

for subreddit in subreddits:
    for keyword in keywords:
        after = None
        query = urllib.parse.quote(f'title:"{keyword}"')

        while len(results) < target_total:
            print("Found " + str(len(results)) + " posts so far!") 
            url = (
                f"https://www.reddit.com/r/{subreddit}/search.json"
                f"?q={query}&restrict_sr=1&sort=new&limit=100"
            )
            if after:
                url += f"&after={after}"

            res = requests.get(url)
            if res.status_code != 200:
                print("- Rate limit hit, idle time -")
                time.sleep(2)
                continue

            data = res.json().get("data", {})
            children = data.get("children", [])
            after = data.get("after")

            if not children:
                break 

            for post in children:
                p = post["data"]
                post_id = p["id"]
                title = p["title"]

                if keyword.lower() not in title.lower():
                    continue

                if post_id not in seen_ids:
                    seen_ids.add(post_id)
                    results.append({
                        "id": p["id"],
                        "title": title,
                        "url": "https://reddit.com" + p["permalink"],
                        "created_utc": p["created_utc"],
                        "subreddit": subreddit,
                    })

                    if len(results) >= target_total:
                        break

            if not after:
                break

            time.sleep(1.5)

results = sorted(results, key=lambda x: x["created_utc"], reverse=True)[:500]

script_folder = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_folder, "reddit_movies_filtered.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)