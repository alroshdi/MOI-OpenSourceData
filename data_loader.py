# -*- coding: utf-8 -*-
"""Load and normalize MOI open data election Excel files."""
from __future__ import annotations

import os
import re
from typing import Any

import pandas as pd

DATA_DIR_NAME = "البيانات المفتوحة"


def _base_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _list_xlsx() -> list[str]:
    base = _base_dir()
    roots = [os.path.join(base, DATA_DIR_NAME)]
    if not os.path.isdir(roots[0]):
        roots = [base]
    out: list[str] = []
    for start in roots:
        if not os.path.isdir(start):
            continue
        for root, _, files in os.walk(start):
            for f in files:
                if f.lower().endswith(".xlsx") and not f.startswith("~"):
                    out.append(os.path.join(root, f))
    return sorted(set(out))


def _metadata_year(path: str) -> int | None:
    try:
        xl = pd.ExcelFile(path)
        for name in xl.sheet_names:
            if "metadata" in name.lower():
                meta = pd.read_excel(path, sheet_name=name, header=None)
                for i in range(len(meta)):
                    k = meta.iloc[i, 0]
                    if k is not None and "DataReferencePeriod" in str(k):
                        v = meta.iloc[i, 1]
                        if pd.notna(v):
                            try:
                                return int(float(str(v).strip()))
                            except ValueError:
                                pass
    except Exception:
        pass
    return None


def _year_from_filename(path: str) -> int | None:
    m = re.search(r"(20\d{2}|19\d{2})", os.path.basename(path))
    if m:
        return int(m.group(1))
    return None


def _election_kind(path: str) -> str:
    b = os.path.basename(path)
    if "البلدية" in b or "المجالس البلدية" in b:
        return "مجالس بلدية"
    if "الشورى" in b:
        return "مجلس الشورى"
    return "أخرى"


def _first_data_sheet(xl: pd.ExcelFile) -> str:
    for s in xl.sheet_names:
        if "metadata" in s.lower():
            continue
        return s
    return xl.sheet_names[0]


def _to_num(x: Any) -> float:
    if pd.isna(x):
        return float("nan")
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def _load_sheet(path: str) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    sheet = _first_data_sheet(xl)
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    year = _metadata_year(path) or _year_from_filename(path)
    kind = _election_kind(path)
    ncols = raw.shape[1]

    # Data starts row 2; rows 0-1 are headers
    body = raw.iloc[2:].copy()
    body = body.dropna(how="all")
    if body.empty:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    last_gov: str | float = float("nan")

    for _, r in body.iterrows():
        gov = r.iloc[0]
        wil = r.iloc[1]
        if pd.isna(gov) or str(gov).strip() == "":
            gov = last_gov
        else:
            last_gov = gov
        if pd.isna(wil):
            continue

        rec: dict[str, Any] = {
            "المحافظة": str(gov).strip(),
            "الولاية": str(wil).strip(),
            "السنة": year,
            "نوع_الانتخاب": kind,
            "ملف_المصدر": os.path.basename(path),
        }

        rec["ناخبون_مسجلون_ذكور"] = _to_num(r.iloc[2])
        rec["ناخبون_مسجلون_إناث"] = _to_num(r.iloc[3])
        rec["ناخبون_مسجلون_إجمالي"] = _to_num(r.iloc[4])

        for j in range(6):
            rec[f"عمر_مسجل_{j}"] = _to_num(r.iloc[5 + j]) if 5 + j < ncols else float("nan")

        rec["مصوتون_ذكور"] = _to_num(r.iloc[11])
        rec["مصوتون_إناث"] = _to_num(r.iloc[12])
        rec["مصوتون_إجمالي"] = _to_num(r.iloc[13])

        if ncols >= 24:
            # 2011 Shura: ذكور حسب العمر 14–18، إناث 19–23 (خمس فئات)
            for j in range(5):
                m = _to_num(r.iloc[14 + j])
                f = _to_num(r.iloc[19 + j])
                if pd.isna(m) and pd.isna(f):
                    rec[f"عمر_مصوت_{j}"] = float("nan")
                else:
                    rec[f"عمر_مصوت_{j}"] = (m or 0) + (f or 0)
            rec["عمر_مصوت_5"] = float("nan")
        elif ncols >= 20:
            for j in range(6):
                rec[f"عمر_مصوت_{j}"] = _to_num(r.iloc[14 + j])

        rows.append(rec)

    return pd.DataFrame(rows)


def load_all() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for p in _list_xlsx():
        try:
            df = _load_sheet(p)
            if not df.empty:
                frames.append(df)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    # Turnout
    out["نسبة_المشاركة"] = out.apply(
        lambda r: (r["مصوتون_إجمالي"] / r["ناخبون_مسجلون_إجمالي"] * 100)
        if pd.notna(r["ناخبون_مسجلون_إجمالي"]) and r["ناخبون_مسجلون_إجمالي"] > 0
        else float("nan"),
        axis=1,
    )
    out["ذكور_من_المصوتين_%"] = out.apply(
        lambda r: (r["مصوتون_ذكور"] / r["مصوتون_إجمالي"] * 100)
        if pd.notna(r["مصوتون_إجمالي"]) and r["مصوتون_إجمالي"] > 0
        else float("nan"),
        axis=1,
    )
    dup = out.duplicated(subset=["المحافظة", "الولاية", "السنة", "نوع_الانتخاب"], keep=False)
    out["تكرار_محتمل"] = dup
    return out


AGE_REGISTERED_LABELS = [
    "< 30",
    "30–39",
    "40–49",
    "50–59",
    "60–69",
    "70+",
]
