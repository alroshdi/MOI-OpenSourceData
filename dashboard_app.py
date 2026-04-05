# -*- coding: utf-8 -*-
"""
لوحة تحليلات بيانات الناخبين — وزارة الداخلية (البيانات المفتوحة).
تشغيل: py dashboard_app.py  →  http://127.0.0.1:8050
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
from dash import Dash, Input, Output, State, callback, clientside_callback, ctx, dash_table, dcc, html, no_update
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


def get_palette(mode: str) -> dict:
    if mode == "light":
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
    return {
        "bg": "#0b0f14",
        "card": "#1a2433",
        "plot_bg": "#121a24",
        "text": "#e8eef7",
        "muted": "#8b9cb3",
        "accent": "#3b82f6",
        "accent2": "#10b981",
        "border": "#2d3a4f",
        "table_alt": "#1a2535",
        "plot_template": "plotly_dark",
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
        "ins_best": "أعلى مشاركة ضمن الفلاتر: {w} ({g}) — {p}% سنة {y}.",
        "ins_worst": "أدنى مشاركة: {w} ({g}) — {p}% سنة {y}.",
        "ins_male": "نسبة المصوتين من الذكور من إجمالي المصوتين: {r}%.",
        "ui_appearance": "المظهر",
        "ui_language": "اللغة",
        "ui_dark": "داكن",
        "ui_light": "فاتح",
        "ui_ar_short": "عربي",
        "ui_en_short": "English",
        "aria_theme_group": "اختر مظهر الواجهة",
        "aria_lang_group": "اختر لغة الواجهة",
        "aria_toolbar_quick": "تبديل السريع للمظهر واللغة",
        "ui_theme_to_light": "التبديل إلى الوضع الفاتح",
        "ui_theme_to_dark": "التبديل إلى الوضع الداكن",
        "ui_lang_to_en": "التبديل إلى الإنجليزية",
        "ui_lang_to_ar": "التبديل إلى العربية",
    },
    "en": {
        "title": "Voter data analytics dashboard",
        "subtitle": "Open data — Municipal councils & Shura Council elections (by wilayat and age groups)",
        "filters": "Filters & search",
        "f_kind": "Election type",
        "f_year": "Year",
        "f_gov": "Governorate",
        "f_search": "Search wilayat name",
        "ph_search": "e.g. Salalah, Al-Seeb…",
        "ph_all": "All",
        "kpi_reg": "Total registered voters (filtered)",
        "kpi_vote": "Total voters",
        "kpi_turn": "Overall turnout %",
        "kpi_rows": "Wilayat records",
        "tab_ov": "Overview",
        "tab_tr": "Trends",
        "tab_de": "Details",
        "tab_in": "Insights",
        "sec_ov": "Overview",
        "sec_tr": "Trends over time",
        "sec_de": "Detailed analysis — interactive table (sort & filter)",
        "sec_de_hint": "Click column headers to sort. Use the filter row under each column for quick search.",
        "sec_in": "Automated insights",
        "empty": "No data files found in «البيانات المفتوحة». Add Excel files and restart.",
        "no_data": "No rows match the current filters.",
        "insight_none": "Adjust filters to see more detail.",
        "note_2011": "Note: the 2011 Shura file uses slightly different age bands for voters; age distributions are only roughly comparable across years.",
        "chart_reg": "Registered",
        "chart_vote": "Voted",
        "axis_count": "Count",
        "axis_year": "Year",
        "pie_m": "Male",
        "pie_f": "Female",
        "heat_x": "Age band",
        "heat_y": "Governorate",
        "heat_c": "Count",
        "age_col": "Age band",
        "tbl_gov": "Governorate",
        "tbl_wil": "Wilayat",
        "tbl_year": "Year",
        "tbl_type": "Election type",
        "tbl_reg": "Registered",
        "tbl_vot": "Voted",
        "tbl_pct": "Turnout %",
        "ins_best": "Highest turnout in selection: {w} ({g}) — {p}% in {y}.",
        "ins_worst": "Lowest turnout: {w} ({g}) — {p}% in {y}.",
        "ins_male": "Share of male voters in total voters: {r}%.",
        "ui_appearance": "Appearance",
        "ui_language": "Language",
        "ui_dark": "Dark",
        "ui_light": "Light",
        "ui_ar_short": "عربي",
        "ui_en_short": "English",
        "aria_theme_group": "Choose interface theme",
        "aria_lang_group": "Choose interface language",
        "aria_toolbar_quick": "Quick theme and language toggles",
        "ui_theme_to_light": "Switch to light theme",
        "ui_theme_to_dark": "Switch to dark theme",
        "ui_lang_to_en": "Switch to English",
        "ui_lang_to_ar": "Switch to Arabic",
    },
}


def T(lang: str, key: str) -> str:
    return STR.get(lang, STR["ar"]).get(key, key)


AGE_LABELS_EN = ["< 30", "30–39", "40–49", "50–59", "60–69", "70+"]

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Election analytics — MOI",
    update_title=None,
    assets_folder=os.path.join(BASE_DIR, "assets"),
)

server = app.server


@server.route("/logo/<path:filename>")
def _serve_logo(filename: str):
    return send_from_directory(LOGO_DIR, filename)


px.defaults.template = "plotly_dark"


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


def _toolbar(lang: str, theme: str) -> html.Div:
    """Single-icon toggles: sun/moon for theme, A/E for language."""
    rtl = lang == "ar"
    toolbar_dir = "app-toolbar--rtl" if rtl else "app-toolbar--ltr"
    # Icon shows the action: dark UI → sun (switch to light); light UI → moon (switch to dark)
    theme_icon = "sun" if theme == "dark" else "moon"
    theme_aria = T(lang, "ui_theme_to_light") if theme == "dark" else T(lang, "ui_theme_to_dark")
    lang_aria = T(lang, "ui_lang_to_en") if lang == "ar" else T(lang, "ui_lang_to_ar")

    return html.Div(
        className=f"app-toolbar {toolbar_dir}",
        role="banner",
        **({"dir": "rtl"} if rtl else {"dir": "ltr"}),
        children=[
            html.Div(
                className="app-brand" + (" app-brand--rtl" if rtl else " app-brand--ltr"),
                children=[
                    html.Div(
                        className="app-logo-frame",
                        children=[
                            html.Img(
                                src=LOGO_URL,
                                alt="شعار الجهة" if lang == "ar" else "Ministry logo",
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
            html.Div(
                className="toolbar-toggles",
                role="toolbar",
                **{"aria-label": T(lang, "aria_toolbar_quick")},
                children=[
                    html.Div(
                        className="toolbar-toggle-group",
                        children=[
                            html.Span(
                                className="toolbar-toggle-label",
                                children=[
                                    _ico("moon", "toolbar-label-ico"),
                                    T(lang, "ui_appearance"),
                                ],
                            ),
                            html.Button(
                                id="theme-toggle-btn",
                                type="button",
                                className="icon-toggle-btn icon-toggle-btn--theme",
                                title=theme_aria,
                                **{"aria-label": theme_aria},
                                children=[_ico(theme_icon, "toggle-ico")],
                            ),
                        ],
                    ),
                    html.Div(
                        className="toolbar-toggle-group",
                        children=[
                            html.Span(
                                className="toolbar-toggle-label",
                                children=[
                                    _ico("globe", "toolbar-label-ico"),
                                    T(lang, "ui_language"),
                                ],
                            ),
                            html.Button(
                                id="locale-toggle-btn",
                                type="button",
                                className="icon-toggle-btn icon-toggle-btn--ae",
                                title=lang_aria,
                                **{"aria-label": lang_aria},
                                lang="ar" if lang == "ar" else "en",
                                children=[
                                    html.Span("A/E", className="ae-toggle-mark", **{"aria-hidden": "true"}),
                                    html.Span(lang_aria, className="sr-only"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _shell_style(theme: str, lang: str) -> dict:
    p = get_palette("light" if theme == "light" else "dark")
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


def _root_class(theme: str, lang: str) -> str:
    base = "theme-light" if theme == "light" else "theme-dark"
    return base + (" layout-rtl" if lang == "ar" else " layout-ltr")


def _figure_rtl_axes(fig, lang: str) -> None:
    """Plotly: y-axis on the right and legend on the inner-start for Arabic RTL."""
    if lang != "ar":
        return
    fig.update_layout(
        yaxis=dict(side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="right"),
    )


def _figure_rtl_pie(fig, lang: str) -> None:
    if lang != "ar":
        return
    fig.update_layout(legend=dict(orientation="h", y=1.05, x=0, xanchor="right"))


def _figure_rtl_heatmap(fig, lang: str) -> None:
    if lang != "ar":
        return
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
            colors={"border": "#2d3a4f", "primary": "#3b82f6", "background": "#1a2433"},
            children=[
                dcc.Tab(label=_tab_label("ar", "tab_ov", "layout-dashboard"), value="tab-overview"),
                dcc.Tab(label=_tab_label("ar", "tab_tr", "line-chart"), value="tab-trends"),
                dcc.Tab(label=_tab_label("ar", "tab_de", "table"), value="tab-detail"),
                dcc.Tab(label=_tab_label("ar", "tab_in", "lightbulb"), value="tab-insights"),
            ],
            style={"marginBottom": "1rem"},
        ),
        html.Div(id="tab-body"),
        html.Div(id="detail-table-i18n-dummy", style={"display": "none"}),
    ],
)

app.layout = html.Div(
    id="app-root",
    className="theme-dark layout-rtl",
    dir="rtl",
    lang="ar",
    children=[
        dcc.Store(id="theme-store", data="dark", storage_type="local"),
        dcc.Store(id="locale-store", data="ar", storage_type="local"),
        html.Div(id="toolbar-slot"),
        html.Div(
            id="app-inner",
            style=_shell_style("dark", "ar"),
            children=[_MAIN_DASHBOARD] if not DF.empty else [html.Div(id="empty-state")],
        ),
    ],
)


@callback(
    Output("app-root", "className"),
    Output("app-root", "dir"),
    Output("app-root", "lang"),
    Output("app-inner", "style"),
    Output("toolbar-slot", "children"),
    Input("theme-store", "data"),
    Input("locale-store", "data"),
)
def sync_shell(theme: str | None, lang: str | None):
    theme = theme if theme in ("dark", "light") else "dark"
    lang = lang if lang in ("ar", "en") else "ar"
    dir_attr = "rtl" if lang == "ar" else "ltr"
    lang_attr = "ar" if lang == "ar" else "en"
    return (
        _root_class(theme, lang),
        dir_attr,
        lang_attr,
        _shell_style(theme, lang),
        _toolbar(lang, theme),
    )


@callback(
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(_n, current):
    cur = current if current in ("dark", "light") else "dark"
    return "light" if cur == "dark" else "dark"


@callback(
    Output("locale-store", "data"),
    Input("locale-toggle-btn", "n_clicks"),
    State("locale-store", "data"),
    prevent_initial_call=True,
)
def toggle_locale(_n, current):
    cur = current if current in ("ar", "en") else "ar"
    return "en" if cur == "ar" else "ar"


if DF.empty:

    @callback(Output("empty-state", "children"), Input("locale-store", "data"))
    def empty_message(lang):
        lang = lang if lang in ("ar", "en") else "ar"
        return html.Div(T(lang, "empty"), style={"padding": "2.5rem", "textAlign": "center"})


if not DF.empty:

    @callback(
        Output("main-tabs", "children"),
        Input("locale-store", "data"),
        State("main-tabs", "value"),
    )
    def localize_tabs(lang, val):
        lang = lang if lang in ("ar", "en") else "ar"
        val = val or "tab-overview"
        return [
            dcc.Tab(label=_tab_label(lang, "tab_ov", "layout-dashboard"), value="tab-overview"),
            dcc.Tab(label=_tab_label(lang, "tab_tr", "line-chart"), value="tab-trends"),
            dcc.Tab(label=_tab_label(lang, "tab_de", "table"), value="tab-detail"),
            dcc.Tab(label=_tab_label(lang, "tab_in", "lightbulb"), value="tab-insights"),
        ]

    @callback(
        Output("filter-search", "placeholder"),
        Input("locale-store", "data"),
    )
    def search_placeholder(lang):
        lang = lang if lang in ("ar", "en") else "ar"
        return T(lang, "ph_search")

    @callback(
        Output("filter-kind", "placeholder"),
        Output("filter-year", "placeholder"),
        Output("filter-gov", "placeholder"),
        Input("locale-store", "data"),
    )
    def dropdown_placeholders(lang):
        lang = lang if lang in ("ar", "en") else "ar"
        p = T(lang, "ph_all")
        return p, p, p

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
        Input("theme-store", "data"),
        Input("locale-store", "data"),
    )
    def update_all(kinds, years, govs, search, tab, theme, lang):
        theme = theme if theme in ("dark", "light") else "dark"
        lang = lang if lang in ("ar", "en") else "ar"
        P = get_palette("light" if theme == "light" else "dark")
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
                return f"{x/1e6:.2f} M" if lang == "en" else f"{x/1e6:.2f} مليون"
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
        _figure_rtl_axes(fig_line, lang)

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
        _figure_rtl_axes(fig_bar, lang)

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
        _figure_rtl_pie(fig_pie, lang)

        age_cols = [f"عمر_مسجل_{i}" for i in range(6)]
        age_labels = AGE_REGISTERED_LABELS if lang == "ar" else AGE_LABELS_EN
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
        _figure_rtl_axes(fig_age_bar, lang)

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
        _figure_rtl_heatmap(fig_heat, lang)

        table_cols = [
            {"name": T(lang, "tbl_gov"), "id": "المحافظة"},
            {"name": T(lang, "tbl_wil"), "id": "الولاية"},
            {"name": T(lang, "tbl_year"), "id": "السنة", "type": "numeric"},
            {"name": T(lang, "tbl_type"), "id": "نوع_الانتخاب"},
            {"name": T(lang, "tbl_reg"), "id": "ناخبون_مسجلون_إجمالي", "type": "numeric", "format": {"specifier": ",.0f"}},
            {"name": T(lang, "tbl_vot"), "id": "مصوتون_إجمالي", "type": "numeric", "format": {"specifier": ",.0f"}},
            {"name": T(lang, "tbl_pct"), "id": "نسبة_المشاركة", "type": "numeric", "format": {"specifier": ".1f"}},
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
            style_table={
                "overflowX": "auto",
                "borderRadius": "12px",
                "border": f"1px solid {P['border']}",
                "backgroundColor": P["card"],
            },
            style_cell={
                "textAlign": "right" if lang == "ar" else "left",
                "padding": "7px 12px",
                "minHeight": "36px",
                "backgroundColor": P["bg"],
                "color": P["text"],
                "border": f"1px solid {P['border']}",
                "fontFamily": "'IBM Plex Sans Arabic', Inter, sans-serif",
                "fontSize": "0.875rem",
            },
            style_header={
                "fontWeight": "700",
                "backgroundColor": P["card"],
                "color": P["text"],
                "borderBottom": f"2px solid {P['accent']}",
                "padding": "10px 12px",
                "whiteSpace": "normal",
            },
            style_filter={
                "backgroundColor": P["plot_bg"],
                "border": f"1px solid {P['border']}",
                "padding": "4px 6px",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": P["table_alt"]},
            ],
            css=[
                {
                    "selector": ".dash-filter input",
                    "rule": f"font-family: inherit; font-size: 0.8125rem; padding: 6px 8px; border-radius: 8px; border: 1px solid {P['border']}; background: {P['card']}; color: {P['text']}; min-height: 32px;",
                },
                {
                    "selector": ".dash-table-container .previous-next-container",
                    "rule": "font-size: 0.8125rem; padding-top: 0.5rem;",
                },
            ],
        )

        sub = df.dropna(subset=["نسبة_المشاركة"])
        best = sub.loc[sub["نسبة_المشاركة"].idxmax()] if len(sub) else None
        worst = sub.loc[sub["نسبة_المشاركة"].idxmin()] if len(sub) else None
        insight_lines: list = []
        if best is not None and not pd.isna(best["نسبة_المشاركة"]):
            insight_lines.append(
                T(lang, "ins_best").format(
                    w=best["الولاية"],
                    g=best["المحافظة"],
                    p=best["نسبة_المشاركة"],
                    y=int(best["السنة"]),
                )
            )
        if worst is not None and not pd.isna(worst["نسبة_المشاركة"]):
            insight_lines.append(
                T(lang, "ins_worst").format(
                    w=worst["الولاية"],
                    g=worst["المحافظة"],
                    p=worst["نسبة_المشاركة"],
                    y=int(worst["السنة"]),
                )
            )
        f_ratio = (df["مصوتون_ذكور"].sum() / vote * 100) if vote > 0 else float("nan")
        if pd.notna(f_ratio):
            insight_lines.append(T(lang, "ins_male").format(r=f_ratio))

        insights_block = html.Div(
            [
                _section_title(T(lang, "sec_in"), P, "lightbulb"),
                html.Ul(
                    [html.Li(t, style={"marginBottom": "0.5rem"}) for t in insight_lines]
                    or [html.Li(T(lang, "insight_none"))]
                ),
                html.P(
                    T(lang, "note_2011"),
                    style={"color": P["muted"], "fontSize": "0.9rem", "marginTop": "1rem"},
                ),
            ]
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
                html.Div(className="detail-table-wrap", children=[tbl]),
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

    clientside_callback(
        """
        function(lang, tab) {
            const phAr = "تصفية هذا العمود…";
            const phEn = "Filter this column…";
            const ph = (lang === "ar") ? phAr : phEn;
            function apply() {
                const root = document.getElementById("detail-data-table");
                if (!root) return;
                root.querySelectorAll(".dash-filter input").forEach(function(el) {
                    el.placeholder = ph;
                });
            }
            apply();
            setTimeout(apply, 0);
            setTimeout(apply, 150);
            setTimeout(apply, 400);
            return "";
        }
        """,
        Output("detail-table-i18n-dummy", "children"),
        Input("locale-store", "data"),
        Input("main-tabs", "value"),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    app.run(debug=False, host="127.0.0.1", port=port)
