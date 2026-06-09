from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from typing import Any

import requests

API_URL = "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"


def fetch_api_json(day: date) -> dict[str, Any]:
    """API 원본 JSON 1일 (10절)."""
    service_key = os.environ["DATA_GO_KR_SERVICE_KEY"]
    stn_id = os.getenv("ASOS_STN_ID", "108")
    ymd = day.strftime("%Y%m%d")
    params = {
        "serviceKey": service_key,
        "pageNo": "1",
        "numOfRows": "24",
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "HR",
        "startDt": ymd,
        "startHh": "00",
        "endDt": ymd,
        "endHh": "23",
        "stnIds": stn_id,
    }
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_hourly(start: date, end: date) -> list[dict[str, Any]]:
    """여러 날 시간별 행 (11절 backfill)."""
    service_key = os.environ["DATA_GO_KR_SERVICE_KEY"]
    stn_id = os.getenv("ASOS_STN_ID", "108")
    location_key = f"stn:{stn_id}"
    rows: list[dict[str, Any]] = []
    d = start
    while d <= end:
        data = fetch_api_json(d)
        header = data.get("response", {}).get("header", {})
        if header.get("resultCode") != "00":
            raise RuntimeError(
                f"공공 API 오류: {header.get('resultCode')} / {header.get('resultMsg')}"
            )
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item")
        if not items:
            d += timedelta(days=1)
            continue
        if not isinstance(items, list):
            items = [items]
        for item in items:
            tm = item.get("tm")
            obs_time = datetime.strptime(tm, "%Y-%m-%d %H:%M")
            rows.append(
                {
                    "obs_time": obs_time,
                    "source": "public",
                    "location_key": location_key,
                    "temperature": _num(item.get("ta")),
                    "humidity": _num(item.get("hm")),
                    "wind_speed": _num(item.get("ws")),
                    "solar_radiation": None,
                    "precipitation": _num(item.get("rn")),
                    "raw_json": json.dumps(item, ensure_ascii=False),
                }
            )
        d += timedelta(days=1)
    return rows


def _num(v):
    if v is None or v == "":
        return None
    return float(v)