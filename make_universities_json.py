import json
import re
import sys

import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_universities_in_the_United_Kingdom"

def clean_name(name: str) -> str:
    # Remove footnote markers like [1], extra whitespace
    name = re.sub(r"\[\d+\]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def main():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # The page contains one or more "wikitable" tables; we want the university-name column.
    tables = soup.select("table.wikitable")
    if not tables:
        print("No wikitable found. Wikipedia layout may have changed.", file=sys.stderr)
        sys.exit(1)

    uni_names = set()

    for table in tables:
        # Grab rows
        rows = table.select("tr")
        if not rows:
            continue

        # Identify header row
        headers = [clean_name(th.get_text(" ", strip=True)) for th in rows[0].select("th")]
        # Look for a column called "University"
        try:
            uni_col = headers.index("University")
        except ValueError:
            continue

        # Parse data rows
        for row in rows[1:]:
            cells = row.select("td")
            if len(cells) <= uni_col:
                continue
            uni_text = clean_name(cells[uni_col].get_text(" ", strip=True))
            if uni_text:
                uni_names.add(uni_text)

    # Sort alphabetically
    uni_list = sorted(uni_names, key=lambda s: s.lower())

    # Output structure for your project:
    # keep "city" blank for now if you don't have a city dataset ready
    out = [{"name": name, "city": ""} for name in uni_list]

    with open("universities.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(out)} universities to universities.json")

if __name__ == "__main__":
    main()
