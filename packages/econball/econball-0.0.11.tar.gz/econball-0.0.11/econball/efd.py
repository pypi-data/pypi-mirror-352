"""A puller for EFD data."""

# pylint: disable=global-statement,line-too-long,too-many-locals,too-many-branches,too-many-statements
import io
import logging
import re
import urllib.parse
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
from requests_cache.session import CachedSession

_EFD_DATA = None


def _fetch_efd_date(
    session: CachedSession,
) -> dict[str, dict[str, list[dict[str, float | str]]]]:
    # Adapted from https://github.com/neelsomani/senator-filings/tree/master
    global _EFD_DATA
    if _EFD_DATA is None:
        urls = set()
        with session.cache_disabled():
            landing_page_response = session.get(
                "https://efdsearch.senate.gov/search/home/"
            )
            landing_page_response.raise_for_status()
            landing_page = BeautifulSoup(landing_page_response.text, "lxml")
            form_csrf = landing_page.find(attrs={"name": "csrfmiddlewaretoken"})[  # type: ignore
                "value"
            ]  # type: ignore
            form_payload = {
                "csrfmiddlewaretoken": form_csrf,
                "prohibition_agreement": "1",
            }
            session.post(
                "https://efdsearch.senate.gov/search/home/",
                data=form_payload,
                headers={"Referer": "https://efdsearch.senate.gov/search/home/"},
            )
            if "csrftoken" in session.cookies:
                csrftoken = session.cookies["csrftoken"]
            else:
                csrftoken = session.cookies["csrf"]

            def reports_api(
                offset: int,
            ) -> list[list[str]]:
                login_data = {
                    "start": str(offset),
                    "length": str(100),
                    "report_types": "[11]",
                    "filer_types": "[]",
                    "submitted_start_date": "01/01/2012 00:00:00",
                    "submitted_end_date": "",
                    "candidate_state": "",
                    "senator_state": "",
                    "office_id": "",
                    "first_name": "",
                    "last_name": "",
                    "csrfmiddlewaretoken": csrftoken,
                }
                response = session.post(
                    "https://efdsearch.senate.gov/search/report/data/",
                    data=login_data,
                    headers={"Referer": "https://efdsearch.senate.gov/search/"},
                )
                return response.json()["data"]

            idx = 0
            reports = reports_api(idx)
            all_reports: list[list[str]] = []
            while len(reports) != 0:
                all_reports.extend(reports)
                idx += 100
                reports = reports_api(idx)

        for report in all_reports:
            for line in report:
                match = re.search(r'<a\s[^>]*href=["\'](.*?)["\']', line, re.IGNORECASE)
                if match:
                    href = match.group(1)
                    url = urllib.parse.urljoin(
                        "https://efdsearch.senate.gov/search/report/data/", href
                    )
                    urls.add(url)

        traded_assets: dict[str, dict[str, list[dict[str, float | str]]]] = {}

        for url in urls:
            o = urlparse(url)
            path_components = o.path.split("/")
            if path_components[-3] != "ptr":
                continue

            response = session.get(url)
            response.raise_for_status()

            handle = io.StringIO()
            handle.write(response.text)
            handle.seek(0)
            dfs = pd.read_html(handle)
            df = dfs[0]

            soup = BeautifulSoup(response.text, "lxml")
            filed_date = None
            for h1 in soup.find_all("h1"):
                filed_date = parser.parse(
                    h1.get_text().strip().split("(")[0].strip().split()[-1]
                )
            if filed_date is None:
                raise ValueError("filed_date is null")

            for _, row in df.iterrows():
                ticker = row["Ticker"]
                if "--" in ticker:
                    continue
                date = str(filed_date)
                amount = float(
                    row["Amount"]
                    .split("-")[0]
                    .strip()
                    .replace(",", "")
                    .replace("$", "")
                )
                interaction_type = row["Type"].split("(")[0].strip()
                trade_interaction_type = None
                if interaction_type in {"Purchase", "Exchange"}:
                    trade_interaction_type = "buy"
                elif interaction_type == "Sale":
                    trade_interaction_type = "sale"
                else:
                    raise ValueError(
                        f"Unrecognised interaction type: {interaction_type}"
                    )
                timeline = traded_assets.get(ticker, {})
                trades = timeline.get(date, [])
                trades.append({"amount": amount, "interaction": trade_interaction_type})
                timeline[date] = trades
                traded_assets[ticker] = timeline

        _EFD_DATA = traded_assets
    return _EFD_DATA


def pull(series: str, session: CachedSession) -> list[pd.Series]:
    """Pull the EFD data."""
    logging.info("Pulling EFD series %s", series)
    data = _fetch_efd_date(session)
    ticker = data[series]
    actions = set()
    for value in ticker.values():
        for trade in value:
            actions.add(trade["interaction"])
    action_series = []
    for action in actions:
        summed_dates = {}
        for k, v in ticker.items():
            summed_amounts = 0.0
            for trade in v:
                if trade["interaction"] != action:
                    continue
                summed_amounts += trade["amount"]  # type: ignore
            if summed_amounts == 0.0:
                continue
            summed_dates[k] = summed_amounts
        action_ser = pd.Series(
            data=list(summed_dates.values()), index=list(summed_dates.keys())
        )
        action_ser.index = pd.to_datetime(action_ser.index).date  # type: ignore
        action_ser.name = f"EFD_{series}_{action}"
        action_ser = action_ser.sort_index()
        action_series.append(action_ser)
    return action_series
