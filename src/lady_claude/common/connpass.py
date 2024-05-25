from datetime import datetime, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup


def get_interested_events() -> List[Dict]:
    base_url = "https://connpass.com/search"
    keywords = ["AWS", "クラスメソッド", "Meetup", "RAG", "モバイル", "デザイン"]
    area_list = ["kyoto", "osaka", "hyogo"]

    events = []

    for keyword in keywords:
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        start_date = (now + timedelta(weeks=2)).strftime("%Y%%2F%m%%2F%d")
        end_date = (now + timedelta(weeks=3)).strftime("%Y%%2F%m%%2F%d")

        url_with_query = f"{base_url}?q={keyword}"
        url_with_query = f"{url_with_query}&start_from={start_date}&start_to={end_date}"
        url_with_query = (
            f"{url_with_query}&prefectures={'&prefectures='.join(area_list)}"
        )

        response = requests.get(
            url_with_query,
            headers={"User-Agent": None},
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch connpass events with status code: {response.status_code}."
            )

        search_soup = BeautifulSoup(response.text, "html.parser")

        for event in search_soup.find_all("div", class_="event_list vevent"):
            event_year = event.find("p", class_="year").text.strip()
            event_date = event.find("p", class_="date").text.strip()
            event_time = event.find("p", class_="time").text.strip()
            event_title = event.find("p", class_="event_title").find("a").text.strip()
            event_link = event.find("p", class_="event_title").find("a")["href"]
            event_id = event_link.rstrip("/").split("/")[-1]

            response = requests.get(
                event_link,
                headers={"User-Agent": None},
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to fetch connpass events with status code: {response.status_code}."
                )

            event_soup = BeautifulSoup(response.text, "html.parser")

            description = (
                event_soup.find("div", id="editor_area")
                .get_text(separator="\n")  # type: ignore
                .strip()
            )

            events.append(
                {
                    "id": event_id,
                    "date": f"{event_year}/{event_date} {event_time}",
                    "description": description,
                    "link": event_link,
                    "title": event_title,
                },
            )

    return list({event["id"]: event for event in events}.values())
