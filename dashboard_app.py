# -*- coding: utf-8 -*-
"""
لوحة تحليلات بيانات الناخبين — وزارة الداخلية (البيانات المفتوحة).
واجهة عربية ووضع فاتح ثابتين. تشغيل: py dashboard_app.py  →  http://127.0.0.1:8050
"""
from __future__ import annotations

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import send_from_directory
from dash import Dash, Input, Output, callback, dash_table, dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import AGE_REGISTERED_LABELS, load_all

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(BASE_DIR, "logo")

DF = load_all()

if not DF.empty:
    _KIND_LIST = sorted(DF["نوع_الانتخاب"].dropna().unique().tolist())
    _YEAR_LIST = sorted(DF["السنة"].dropna().unique().tolist())
    _GOV_LIST = sorted(DF["المحافظة"].dropna().unique().tolist())
    _KIND_OPTS = [{"label": k, "value": k} for k in _KIND_LIST]
    _YEAR_OPTS = [{"label": str(y), "value": y} for y in _YEAR_LIST]
    _GOV_OPTS = [{"label": g, "value": g} for g in _GOV_LIST]
else:
    _KIND_OPTS = _YEAR_OPTS = _GOV_OPTS = []
    _KIND_LIST = _YEAR_LIST = _GOV_LIST = []


def _discover_logo_url() -> str:
    if os.path.isdir(LOGO_DIR):
        exts = (".svg", ".png", ".jpg", ".jpeg", ".webp")
        for name in sorted(os.listdir(LOGO_DIR)):
            low = name.lower()
            if any(low.endswith(e) for e in exts) and not name.startswith("."):
                return f"/logo/{name}"
    return "/logo/logo.svg"


LOGO_URL = _discover_logo_url()

# واجهة ثابتة: عربية + وضع فاتح فقط (لا إعدادات ولا مبدّلات)
APP_LANG = "ar"


def get_palette() -> dict:
    """Light theme palette only."""
    return {
        "bg": "#f0f4f8",
        "card": "#ffffff",
        "plot_bg": "#f8fafc",
        "text": "#0f172a",
        "muted": "#64748b",
        "accent": "#2563eb",
        "accent2": "#059669",
        "border": "#e2e8f0",
        "table_alt": "#f1f5f9",
        "plot_template": "plotly_white",
    }


STR = {
    "ar": {
        "title": "لوحة تحليلات بيانات الناخبين",
        "subtitle": "بيانات مفتوحة — انتخابات المجالس البلدية ومجلس الشورى (حسب الولايات والأعمار)",
        "filters": "الفلاتر والبحث",
        "f_kind": "نوع الانتخاب",
        "f_year": "السنة",
        "f_gov": "المحافظة",
        "f_search": "بحث في اسم الولاية",
        "ph_search": "مثال: صلالة، السيب…",
        "ph_all": "الكل",
        "kpi_reg": "إجمالي الناخبين المسجلين (ضمن الفلاتر)",
        "kpi_vote": "إجمالي المصوتين",
        "kpi_turn": "نسبة المشاركة الإجمالية %",
        "kpi_rows": "عدد سجلات الولايات",
        "tab_ov": "نظرة عامة",
        "tab_tr": "اتجاهات زمنية",
        "tab_de": "تحليل تفصيلي",
        "tab_in": "رؤى وملخص",
        "sec_ov": "نظرة عامة",
        "sec_tr": "اتجاهات زمنية",
        "sec_de": "تحليل تفصيلي — جدول تفاعلي (فرز وتصفية)",
        "sec_de_hint": "انقر على رؤوس الأعمدة للفرز. استخدم مربع التصفية أسفل كل عمود للبحث السريع.",
        "sec_in": "رؤى تلقائية",
        "empty": "لم يتم العثور على ملفات بيانات في مجلد «البيانات المفتوحة». ضع ملفات الإكسل ثم أعد التشغيل.",
        "no_data": "لا توجد بيانات للفلاتر الحالية.",
        "insight_none": "اضبط الفلاتر لعرض المزيد من التفاصيل.",
        "note_2011": "ملاحظة: ملف 2011 (الشورى) يستخدم تجميعاً مختلفاً قليلاً لفئات أعمار المصوتين؛ مقارنة التوزيعات العمرية بين 2011 وباقي السنوات تكون تقريبية.",
        "chart_reg": "مسجلون",
        "chart_vote": "مصوتون",
        "axis_count": "العدد",
        "axis_year": "السنة",
        "pie_m": "ذكور",
        "pie_f": "إناث",
        "heat_x": "فئة عمرية",
        "heat_y": "محافظة",
        "heat_c": "عدد",
        "age_col": "الفئة العمرية",
        "tbl_gov": "المحافظة",
        "tbl_wil": "الولاية",
        "tbl_year": "السنة",
        "tbl_type": "نوع الانتخاب",
        "tbl_reg": "مسجلون",
        "tbl_vot": "مصوتون",
        "tbl_pct": "مشاركة %",
        "ins_best": "أعلى مشاركة ضمن الفلاتر: {w} ({g}) — {p}٪ سنة {y}.",
        "ins_worst": "أدنى مشاركة: {w} ({g}) — {p}٪ سنة {y}.",
        "ins_male": "نسبة المصوتين من الذكور من إجمالي المصوتين: {r}٪.",
        "ins_female": "نسبة المصوتين من الإناث من إجمالي المصوتين: {r}٪.",
        "ins_ctx": "ملخص نطاق البيانات: {n} سجل ولاية، السنوات من {y1} إلى {y2}، وأنواع الانتخاب: {kinds}.",
        "ins_govs": "المحافظات المعروضة ({m}): {govs}.",
        "ins_mean_med": "متوسط نسبة المشاركة بين السجلات المعروضة {mean}٪، والوسيط {med}٪.",
        "ins_top3": "أعلى ثلاث ولايات حسب المشاركة: {t}.",
        "ins_stdev": "الانحراف المعياري لنسبة المشاركة بين السجلات: {s}٪.",
    },
}


def T(lang: str, key: str) -> str:
    return STR.get(lang, STR["ar"]).get(key, key)


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="لوحة تحليلات بيانات الناخبين — وزارة الداخلية",
    update_title=None,
    assets_folder=os.path.join(BASE_DIR, "assets"),
)

server = app.server


@server.route("/logo/<path:filename>")
def _serve_logo(filename: str):
    return send_from_directory(LOGO_DIR, filename)


px.defaults.template = "plotly_white"


def _ico(name: str, *extra_classes: str) -> html.Img:
    """Inline SVG icons from assets/icons (stroke icons, slate tone)."""
    parts = ["ui-ico"] + [c for c in extra_classes if c]
    return html.Img(
        src=app.get_asset_url(f"icons/{name}.svg"),
        className=" ".join(parts),
        alt="",
        **{"aria-hidden": "true"},
    )


def _tab_label(lang: str, key: str, icon_name: str) -> html.Div:
    return html.Div(
        className="tab-label",
        children=[_ico(icon_name, "tab-ico"), html.Span(T(lang, key), className="tab-label-text")],
    )


def _filter_lbl(lang: str, key: str, icon_name: str) -> html.Div:
    return html.Div(
        className="filter-lbl",
        children=[_ico(icon_name, "filter-lbl-ico"), html.Span(T(lang, key))],
    )


def _toolbar() -> html.Div:
    """Header strip: ministry logo and title only (Arabic + light theme fixed)."""
    lang = APP_LANG
    return html.Div(
        className="app-toolbar app-toolbar--rtl",
        role="banner",
        dir="rtl",
        children=[
            html.Div(
                className="app-brand app-brand--rtl",
                children=[
                    html.Div(
                        className="app-logo-frame",
                        children=[
                            html.Img(
                                src=LOGO_URL,
                                alt="شعار الجهة",
                                className="app-logo-img",
                            ),
                        ],
                    ),
                    html.Div(
                        className="app-brand-text",
                        children=[
                            html.H1(id="hdr-title", children=T(lang, "title")),
                            html.P(id="hdr-sub", children=T(lang, "subtitle")),
                        ],
                    ),
                ],
            ),
        ],
    )


def _shell_style() -> dict:
    p = get_palette()
    return {
        "fontFamily": "'IBM Plex Sans Arabic', 'Inter', 'Segoe UI', Tahoma, sans-serif",
        "background": p["bg"],
        "minHeight": "100vh",
        "color": p["text"],
        "padding": "1.25rem clamp(1rem, 3vw, 2rem)",
        "maxWidth": "1680px",
        "margin": "0 auto",
        "transition": "background 0.2s ease, color 0.2s ease",
    }


def _figure_rtl_axes(fig) -> None:
    """Plotly: y-axis on the right and legend on the inner-start for RTL."""
    fig.update_layout(
        yaxis=dict(side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="right"),
    )


def _figure_rtl_pie(fig) -> None:
    fig.update_layout(legend=dict(orientation="h", y=1.05, x=0, xanchor="right"))


def _figure_rtl_heatmap(fig) -> None:
    fig.update_layout(
        yaxis=dict(side="right"),
        coloraxis_colorbar=dict(x=-0.02, xanchor="right", len=0.7),
    )


def _kpi_block(title: str, value: str, P: dict, icon_name: str) -> html.Div:
    return html.Div(
        className="kpi-card",
        style={"background": P["card"], "borderColor": P["border"], "color": P["text"]},
        children=[
            html.Div(
                className="kpi-card__head",
                children=[
                    html.Div(className="kpi-card__icon", children=[_ico(icon_name, "kpi-ico")]),
                    html.Div(title, className="kpi-card__title", style={"color": P["muted"]}),
                ],
            ),
            html.Div(value, className="kpi-card__value", style={"fontSize": "1.65rem", "fontWeight": "700", "marginTop": "0.35rem"}),
        ],
    )


def _section_title(text: str, P: dict, icon_name: str | None = None) -> html.H2:
    kids: list = []
    if icon_name:
        kids.append(html.Span(className="section-title__icon", children=[_ico(icon_name, "section-ico")]))
    kids.append(html.Span(text, className="section-title__text"))
    return html.H2(
        className="section-title" + (" section-title--with-icon" if icon_name else ""),
        children=kids,
        style={
            "fontSize": "1.12rem",
            "fontWeight": "600",
            "margin": "2rem 0 1rem",
            "color": P["text"],
            "borderBottom": f"1px solid {P['border']}",
            "paddingBottom": "0.5rem",
        },
    )


# --- Layout
_MAIN_DASHBOARD = html.Div(
    id="main-content",
    children=[
        html.Div(id="kpi-row", className="kpi-strip"),
        html.Div(
            className="filter-card",
            children=[
                html.Div(
                    id="filter-title",
                    className="filter-card__title",
                    children=[
                        _ico("funnel", "filter-title-ico"),
                        html.Span(T("ar", "filters")),
                    ],
                ),
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fill, minmax(220px, 1fr))",
                        "gap": "1rem",
                    },
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    id="lbl-kind",
                                    className="filter-lbl-slot",
                                    children=_filter_lbl("ar", "f_kind", "funnel"),
                                ),
                                dcc.Dropdown(
                                    id="filter-kind",
                                    options=_KIND_OPTS,
                                    value=_KIND_LIST,
                                    multi=True,
                                    placeholder=T("ar", "ph_all"),
                                    style={"color": "#111"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    id="lbl-year",
                                    className="filter-lbl-slot",
                                    children=_filter_lbl("ar", "f_year", "calendar"),
                                ),
                                dcc.Dropdown(
                                    id="filter-year",
                                    options=_YEAR_OPTS,
                                    value=_YEAR_LIST,
                                    multi=True,
                                    placeholder=T("ar", "ph_all"),
                                    style={"color": "#111"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    id="lbl-gov",
                                    className="filter-lbl-slot",
                                    children=_filter_lbl("ar", "f_gov", "map-pin"),
                                ),
                                dcc.Dropdown(
                                    id="filter-gov",
                                    options=_GOV_OPTS,
                                    value=_GOV_LIST,
                                    multi=True,
                                    placeholder=T("ar", "ph_all"),
                                    style={"color": "#111"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    id="lbl-search",
                                    className="filter-lbl-slot",
                                    children=_filter_lbl("ar", "f_search", "search"),
                                ),
                                dcc.Input(
                                    id="filter-search",
                                    type="text",
                                    placeholder=T("ar", "ph_search"),
                                    debounce=True,
                                    style={
                                        "width": "100%",
                                        "padding": "0.5rem 0.75rem",
                                        "borderRadius": "10px",
                                        "border": "1px solid var(--border)",
                                        "background": "var(--surface)",
                                        "color": "var(--text)",
                                    },
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
        dcc.Tabs(
            id="main-tabs",
            value="tab-overview",
            className="custom-tabs",
            colors={"border": "#e2e8f0", "primary": "#2563eb", "background": "#f8fafc"},
            children=[
                dcc.Tab(label=_tab_label("ar", "tab_ov", "layout-dashboard"), value="tab-overview"),
                dcc.Tab(label=_tab_label("ar", "tab_tr", "line-chart"), value="tab-trends"),
                dcc.Tab(label=_tab_label("ar", "tab_de", "table"), value="tab-detail"),
                dcc.Tab(label=_tab_label("ar", "tab_in", "lightbulb"), value="tab-insights"),
            ],
            style={"marginBottom": "1rem"},
        ),
        html.Div(id="tab-body"),
    ],
)

app.layout = html.Div(
    id="app-root",
    className="theme-light layout-rtl",
    dir="rtl",
    lang="ar",
    children=[
        _toolbar(),
        html.Div(
            id="app-inner",
            style=_shell_style(),
            children=[_MAIN_DASHBOARD] if not DF.empty else [html.Div(id="empty-state")],
        ),
    ],
)


if DF.empty:

    @callback(Output("empty-state", "children"), Input("app-root", "className"))
    def empty_message(_cls):
        return html.Div(T(APP_LANG, "empty"), style={"padding": "2.5rem", "textAlign": "center"})


if not DF.empty:

    @callback(
        Output("kpi-row", "children"),
        Output("filter-title", "children"),
        Output("lbl-kind", "children"),
        Output("lbl-year", "children"),
        Output("lbl-gov", "children"),
        Output("lbl-search", "children"),
        Output("tab-body", "children"),
        Input("filter-kind", "value"),
        Input("filter-year", "value"),
        Input("filter-gov", "value"),
        Input("filter-search", "value"),
        Input("main-tabs", "value"),
    )
    def update_all(kinds, years, govs, search, tab):
        lang = APP_LANG
        P = get_palette()
        px.defaults.template = P["plot_template"]

        def _filter_df(
            df: pd.DataFrame,
            kinds_f: list,
            years_f: list,
            govs_f: list,
            search_f: str,
        ) -> pd.DataFrame:
            if df.empty:
                return df
            out = df.copy()
            if kinds_f:
                out = out[out["نوع_الانتخاب"].isin(kinds_f)]
            if years_f:
                out = out[out["السنة"].isin(years_f)]
            if govs_f:
                out = out[out["المحافظة"].isin(govs_f)]
            if search_f and str(search_f).strip():
                q = str(search_f).strip()
                out = out[out["الولاية"].str.contains(q, case=False, na=False)]
            return out

        df = _filter_df(DF, kinds or [], years or [], govs or [], search or "")

        lbl_block = (
            html.Div(
                className="filter-card__title",
                children=[_ico("funnel", "filter-title-ico"), html.Span(T(lang, "filters"))],
            ),
            _filter_lbl(lang, "f_kind", "funnel"),
            _filter_lbl(lang, "f_year", "calendar"),
            _filter_lbl(lang, "f_gov", "map-pin"),
            _filter_lbl(lang, "f_search", "search"),
        )

        if df.empty:
            z = "—"
            kpi_children = [
                _kpi_block(T(lang, "kpi_reg"), z, P, "users"),
                _kpi_block(T(lang, "kpi_vote"), z, P, "user-check"),
                _kpi_block(T(lang, "kpi_turn"), z, P, "percent"),
                _kpi_block(T(lang, "kpi_rows"), z, P, "hash"),
            ]
            body = html.P(T(lang, "no_data"), style={"color": P["muted"]})
            return (
                kpi_children,
                lbl_block[0],
                lbl_block[1],
                lbl_block[2],
                lbl_block[3],
                lbl_block[4],
                body,
            )

        reg = df["ناخبون_مسجلون_إجمالي"].sum()
        vote = df["مصوتون_إجمالي"].sum()
        turnout = (vote / reg * 100) if reg and reg > 0 else float("nan")
        nrows = len(df)

        def fmt_num(x: float) -> str:
            if pd.isna(x):
                return "—"
            if x >= 1e6:
                return f"{x/1e6:.2f} مليون"
            return f"{x:,.0f}"

        k1 = fmt_num(reg)
        k2 = fmt_num(vote)
        k3 = f"{turnout:.1f}%" if pd.notna(turnout) else "—"
        k4 = str(nrows)

        kpi_children = [
            _kpi_block(T(lang, "kpi_reg"), k1, P, "users"),
            _kpi_block(T(lang, "kpi_vote"), k2, P, "user-check"),
            _kpi_block(T(lang, "kpi_turn"), k3, P, "percent"),
            _kpi_block(T(lang, "kpi_rows"), k4, P, "hash"),
        ]

        by_year = (
            df.groupby("السنة", as_index=False)
            .agg({"ناخبون_مسجلون_إجمالي": "sum", "مصوتون_إجمالي": "sum"})
            .sort_values("السنة")
        )

        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=by_year["السنة"],
                y=by_year["ناخبون_مسجلون_إجمالي"],
                name=T(lang, "chart_reg"),
                mode="lines+markers",
                line=dict(color=P["accent"]),
            )
        )
        fig_line.add_trace(
            go.Scatter(
                x=by_year["السنة"],
                y=by_year["مصوتون_إجمالي"],
                name=T(lang, "chart_vote"),
                mode="lines+markers",
                line=dict(color=P["accent2"]),
            )
        )
        fig_line.update_layout(
            template=P["plot_template"],
            paper_bgcolor=P["card"],
            plot_bgcolor=P["plot_bg"],
            font=dict(color=P["text"]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=48, r=24, t=44, b=44),
            yaxis_title=T(lang, "axis_count"),
            xaxis_title=T(lang, "axis_year"),
            height=380,
        )
        _figure_rtl_axes(fig_line)

        top_n = (
            df.groupby(["الولاية", "المحافظة"], as_index=False)
            .agg({"نسبة_المشاركة": "mean", "مصوتون_إجمالي": "sum"})
            .sort_values("نسبة_المشاركة", ascending=False)
            .head(15)
        )
        fig_bar = px.bar(
            top_n,
            x="نسبة_المشاركة",
            y="الولاية",
            orientation="h",
            color="المحافظة",
            text="نسبة_المشاركة",
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar.update_layout(
            template=P["plot_template"],
            paper_bgcolor=P["card"],
            plot_bgcolor=P["plot_bg"],
            font=dict(color=P["text"]),
            margin=dict(l=24, r=24, t=44, b=44),
            height=480,
            showlegend=True,
            yaxis={"categoryorder": "total ascending"},
        )
        _figure_rtl_axes(fig_bar)

        gender = pd.DataFrame(
            {
                "cat": [T(lang, "pie_m"), T(lang, "pie_f")],
                "val": [df["مصوتون_ذكور"].sum(), df["مصوتون_إناث"].sum()],
            }
        )
        fig_pie = px.pie(gender, names="cat", values="val", hole=0.45, color_discrete_sequence=[P["accent"], "#ec4899"])
        fig_pie.update_layout(
            template=P["plot_template"],
            paper_bgcolor=P["card"],
            font=dict(color=P["text"]),
            margin=dict(l=24, r=24, t=44, b=44),
            height=360,
        )
        _figure_rtl_pie(fig_pie)

        age_cols = [f"عمر_مسجل_{i}" for i in range(6)]
        age_labels = AGE_REGISTERED_LABELS
        age_sum = df[age_cols].sum()
        heat_data = pd.DataFrame({T(lang, "age_col"): age_labels, T(lang, "heat_c"): age_sum.values})
        fig_age_bar = px.bar(heat_data, x=T(lang, "age_col"), y=T(lang, "heat_c"), color=T(lang, "heat_c"), color_continuous_scale="Blues")
        fig_age_bar.update_layout(
            template=P["plot_template"],
            paper_bgcolor=P["card"],
            plot_bgcolor=P["plot_bg"],
            font=dict(color=P["text"]),
            height=360,
            showlegend=False,
        )
        _figure_rtl_axes(fig_age_bar)

        gov_age = df.groupby("المحافظة")[age_cols].sum()
        fig_heat = px.imshow(
            gov_age.values,
            labels=dict(x=T(lang, "heat_x"), y=T(lang, "heat_y"), color=T(lang, "heat_c")),
            x=age_labels,
            y=gov_age.index.tolist(),
            color_continuous_scale="Viridis",
            aspect="auto",
        )
        fig_heat.update_layout(
            template=P["plot_template"],
            paper_bgcolor=P["card"],
            font=dict(color=P["text"]),
            height=max(320, len(gov_age) * 28),
            margin=dict(l=120, r=24, t=44, b=60),
        )
        _figure_rtl_heatmap(fig_heat)

        # عرض نسبي (مجموع 100%) لملء العرض بدون شريط تمرير زائف أو فراغ RTL
        table_cols = [
            {"name": T(lang, "tbl_gov"), "id": "المحافظة", "width": "14%"},
            {"name": T(lang, "tbl_wil"), "id": "الولاية", "width": "18%"},
            {"name": T(lang, "tbl_year"), "id": "السنة", "type": "numeric", "width": "8%"},
            {"name": T(lang, "tbl_type"), "id": "نوع_الانتخاب", "width": "16%"},
            {
                "name": T(lang, "tbl_reg"),
                "id": "ناخبون_مسجلون_إجمالي",
                "type": "numeric",
                "format": {"specifier": ",.0f"},
                "width": "14%",
            },
            {
                "name": T(lang, "tbl_vot"),
                "id": "مصوتون_إجمالي",
                "type": "numeric",
                "format": {"specifier": ",.0f"},
                "width": "14%",
            },
            {
                "name": T(lang, "tbl_pct"),
                "id": "نسبة_المشاركة",
                "type": "numeric",
                "format": {"specifier": ".1f"},
                "width": "16%",
            },
        ]
        table_df = df.sort_values(["السنة", "المحافظة", "الولاية"])[
            ["المحافظة", "الولاية", "السنة", "نوع_الانتخاب", "ناخبون_مسجلون_إجمالي", "مصوتون_إجمالي", "نسبة_المشاركة"]
        ]

        tbl = dash_table.DataTable(
            id="detail-data-table",
            columns=table_cols,
            data=table_df.to_dict("records"),
            page_size=15,
            page_action="native",
            sort_action="native",
            filter_action="native",
            fill_width=True,
            style_table={
                "overflowX": "hidden",
                "borderRadius": "12px",
                "border": f"1px solid {P['border']}",
                "backgroundColor": P["card"],
                "width": "100%",
                "minWidth": "0",
                "maxWidth": "100%",
            },
            style_cell={
                "textAlign": "right",
                "padding": "5px 8px",
                "minHeight": "28px",
                "maxHeight": "36px",
                "lineHeight": "1.2",
                "verticalAlign": "middle",
                "backgroundColor": P["bg"],
                "color": P["text"],
                "border": f"1px solid {P['border']}",
                "fontFamily": "'IBM Plex Sans Arabic', Inter, sans-serif",
                "fontSize": "0.8125rem",
                "boxSizing": "border-box",
            },
            style_header={
                "fontWeight": "700",
                "backgroundColor": P["card"],
                "color": P["text"],
                "borderBottom": f"2px solid {P['accent']}",
                "padding": "5px 8px",
                "whiteSpace": "normal",
                "lineHeight": "1.2",
                "verticalAlign": "middle",
                "minHeight": "30px",
                "maxHeight": "44px",
                "boxSizing": "border-box",
            },
            style_data={
                "height": "32px",
                "minHeight": "32px",
                "maxHeight": "36px",
                "padding": "5px 8px",
                "verticalAlign": "middle",
                "boxSizing": "border-box",
            },
            style_filter={
                "backgroundColor": P["plot_bg"],
                "border": f"1px solid {P['border']}",
                "padding": "3px 6px",
                "minHeight": "28px",
                "maxHeight": "32px",
                "verticalAlign": "middle",
                "boxSizing": "border-box",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": P["table_alt"]},
            ],
            css=[
                {
                    "selector": "#detail-data-table",
                    "rule": "width: 100% !important; max-width: 100% !important; display: block !important; box-sizing: border-box !important;",
                },
                {
                    "selector": ".dash-filter input",
                    "rule": f"font-family: inherit; font-size: 0.75rem; padding: 3px 8px; border-radius: 6px; border: 1px solid {P['border']}; background: {P['card']}; color: {P['text']}; min-height: 26px; height: 28px; line-height: 1.2; box-sizing: border-box;",
                },
                {
                    "selector": ".dash-table-container .previous-next-container",
                    "rule": "font-size: 0.75rem; padding-top: 0.5rem; width: 100%; box-sizing: border-box;",
                },
                {
                    "selector": ".dash-spreadsheet-inner table",
                    "rule": "width: 100% !important; table-layout: fixed !important; min-width: 0 !important;",
                },
                {
                    "selector": ".dash-spreadsheet",
                    "rule": "min-width: 0 !important; width: 100% !important; max-width: 100% !important;",
                },
            ],
        )

        def _pct1(x: float) -> str:
            if pd.isna(x):
                return "—"
            return f"{float(x):.1f}"

        sub = df.dropna(subset=["نسبة_المشاركة"])
        best = sub.loc[sub["نسبة_المشاركة"].idxmax()] if len(sub) else None
        worst = sub.loc[sub["نسبة_المشاركة"].idxmin()] if len(sub) else None
        insight_lines: list = []

        years_s = df["السنة"].dropna()
        y1 = int(years_s.min()) if len(years_s) else None
        y2 = int(years_s.max()) if len(years_s) else None
        kinds_u = sorted(df["نوع_الانتخاب"].dropna().unique().tolist())
        kinds_str = "، ".join(str(k) for k in kinds_u) if kinds_u else "—"
        govs_u = sorted(df["المحافظة"].dropna().unique().tolist())
        m_gov = len(govs_u)
        if m_gov <= 8:
            govs_disp = "، ".join(str(g) for g in govs_u) if govs_u else "—"
        else:
            govs_disp = f"{m_gov} محافظة — استخدم فلتر المحافظة لعرض أسماء محددة"

        insight_lines.append(
            T(lang, "ins_ctx").format(n=len(df), y1=y1 or "—", y2=y2 or "—", kinds=kinds_str)
        )
        insight_lines.append(T(lang, "ins_govs").format(m=m_gov, govs=govs_disp))

        if len(sub):
            s = sub["نسبة_المشاركة"]
            mean_p = float(s.mean())
            med_p = float(s.median())
            std_p = float(s.std()) if len(s) > 1 else float("nan")
            insight_lines.append(
                T(lang, "ins_mean_med").format(mean=_pct1(mean_p), med=_pct1(med_p))
            )
            if pd.notna(std_p) and len(s) > 1:
                insight_lines.append(T(lang, "ins_stdev").format(s=_pct1(std_p)))

        if best is not None and not pd.isna(best["نسبة_المشاركة"]):
            insight_lines.append(
                T(lang, "ins_best").format(
                    w=best["الولاية"],
                    g=best["المحافظة"],
                    p=_pct1(best["نسبة_المشاركة"]),
                    y=int(best["السنة"]),
                )
            )
        if worst is not None and not pd.isna(worst["نسبة_المشاركة"]):
            insight_lines.append(
                T(lang, "ins_worst").format(
                    w=worst["الولاية"],
                    g=worst["المحافظة"],
                    p=_pct1(worst["نسبة_المشاركة"]),
                    y=int(worst["السنة"]),
                )
            )

        if len(sub) >= 3:
            top3 = sub.nlargest(3, "نسبة_المشاركة")
            parts = [f"{row['الولاية']} ({_pct1(row['نسبة_المشاركة'])}٪)" for _, row in top3.iterrows()]
            insight_lines.append(T(lang, "ins_top3").format(t="، ".join(parts)))

        f_ratio = (df["مصوتون_ذكور"].sum() / vote * 100) if vote > 0 else float("nan")
        if pd.notna(f_ratio):
            insight_lines.append(T(lang, "ins_male").format(r=_pct1(f_ratio)))
        f_fem = (df["مصوتون_إناث"].sum() / vote * 100) if vote > 0 else float("nan")
        if pd.notna(f_fem):
            insight_lines.append(T(lang, "ins_female").format(r=_pct1(f_fem)))

        insights_block = html.Div(
            [
                _section_title(T(lang, "sec_in"), P, "lightbulb"),
                html.Ul(
                    [html.Li(t, style={"marginBottom": "0.5rem", "lineHeight": "1.6"}) for t in insight_lines]
                    or [html.Li(T(lang, "insight_none"))]
                ),
                html.P(
                    T(lang, "note_2011"),
                    style={"color": P["muted"], "fontSize": "0.9rem", "marginTop": "1rem"},
                ),
            ],
            className="insights-section",
        )

        overview = html.Div(
            [
                _section_title(T(lang, "sec_ov"), P, "layout-dashboard"),
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))", "gap": "1rem"},
                    children=[
                        html.Div([dcc.Graph(figure=fig_pie, config={"displayModeBar": True})]),
                        html.Div([dcc.Graph(figure=fig_age_bar, config={"displayModeBar": True})]),
                    ],
                ),
                html.Div([dcc.Graph(figure=fig_heat, config={"displayModeBar": True})], style={"marginTop": "1rem"}),
            ]
        )

        trends = html.Div(
            [
                _section_title(T(lang, "sec_tr"), P, "line-chart"),
                dcc.Graph(figure=fig_line, config={"displayModeBar": True}),
                html.Div(style={"marginTop": "1rem"}, children=[dcc.Graph(figure=fig_bar, config={"displayModeBar": True})]),
            ]
        )

        detail = html.Div(
            className="detail-section",
            children=[
                _section_title(T(lang, "sec_de"), P, "table"),
                html.P(T(lang, "sec_de_hint"), className="detail-hint"),
                html.Div(
                    className="detail-table-wrap",
                    style={"width": "100%", "minWidth": "100%", "boxSizing": "border-box"},
                    children=[tbl],
                ),
            ],
        )

        if tab == "tab-overview":
            body = overview
        elif tab == "tab-trends":
            body = trends
        elif tab == "tab-detail":
            body = detail
        else:
            body = insights_block

        return (
            kpi_children,
            lbl_block[0],
            lbl_block[1],
            lbl_block[2],
            lbl_block[3],
            lbl_block[4],
            body,
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    app.run(debug=False, host="127.0.0.1", port=port)
