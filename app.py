"""
Mental Health in Tech — Interactive Survey Dashboard
=====================================================
A polished Streamlit app for exploring the 2014 OSMI Mental Health in
Tech Survey. Run with:  streamlit run app.py
(the survey.csv file must be in the same folder, or upload it via the sidebar)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# PAGE CONFIG & GLOBAL STYLE
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Mental Health in Tech | Survey Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#6C5CE7"
ACCENT = "#00CEC9"
BG_CARD = "#161B22"
TEXT_MUTED = "#9AA5B1"

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background: radial-gradient(1200px 600px at 10% -10%, #1b1030 0%, #0e1117 55%),
                    radial-gradient(1000px 500px at 110% 0%, #06282a 0%, #0e1117 60%);
    }}
    #MainMenu, footer {{visibility: hidden;}}

    section[data-testid="stSidebar"] {{
        background-color: #12151c;
        border-right: 1px solid #262a34;
    }}

    h1, h2, h3 {{
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: -0.5px;
    }}

    .hero-title {{
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, {PRIMARY}, {ACCENT});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }}
    .hero-sub {{
        color: {TEXT_MUTED};
        font-size: 1.02rem;
        margin-top: -6px;
    }}

    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid #262a34;
        border-radius: 14px;
        padding: 16px 18px 10px 18px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    }}
    div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED}; }}
    div[data-testid="stMetricValue"] {{ color: #F2F4F8; }}

    .card {{
        background: {BG_CARD};
        border: 1px solid #262a34;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    }}
    .insight-box {{
        background: linear-gradient(135deg, rgba(108,92,231,0.12), rgba(0,206,201,0.10));
        border-left: 4px solid {PRIMARY};
        border-radius: 10px;
        padding: 14px 18px;
        color: #E4E6EB;
        font-size: 0.95rem;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #12151c;
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        border: 1px solid #262a34;
        border-bottom: none;
        color: {TEXT_MUTED};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {BG_CARD};
        color: #F2F4F8 !important;
        border-top: 2px solid {PRIMARY};
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_dark"
COLOR_SEQ = ["#6C5CE7", "#00CEC9", "#FD79A8", "#FDCB6E", "#74B9FF", "#55EFC4", "#E17055"]


# ----------------------------------------------------------------------
# DATA LOADING & CLEANING
# ----------------------------------------------------------------------
@st.cache_data(show_spinner="Loading and cleaning survey data...")
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)

    # Age cleanup
    df.loc[(df["Age"] < 18) | (df["Age"] > 75), "Age"] = np.nan
    df["Age"] = df["Age"].fillna(df["Age"].median()).astype(int)
    bins = [17, 24, 29, 34, 39, 44, 49, 75]
    labels = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50+"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels)

    # Gender cleanup
    def clean_gender(g):
        g = str(g).strip().lower()
        male_terms = {"male", "m", "man", "cis male", "cis man", "mail", "malr", "maile",
                      "make", "mal", "msle", "guy (-ish) ^_^", "male-ish", "male (cis)",
                      "male leaning androgynous",
                      "ostensibly male, unsure what that really means",
                      "something kinda male?"}
        female_terms = {"female", "f", "woman", "cis female", "cis-female/femme", "femake",
                        "female (cis)", "female (trans)", "femail", "trans-female",
                        "trans woman"}
        if g in male_terms:
            return "Male"
        elif g in female_terms:
            return "Female"
        return "Other"

    df["Gender_Clean"] = df["Gender"].apply(clean_gender)

    # Missing value handling
    df["self_employed"] = df["self_employed"].fillna("No")
    df["work_interfere"] = df["work_interfere"].fillna("Not applicable")
    df["state"] = df["state"].fillna("Not in US")
    if "comments" in df.columns:
        df = df.drop(columns=["comments"])

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    return df


def kpi_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)


# ----------------------------------------------------------------------
# SIDEBAR — DATA SOURCE + FILTERS
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧠 Mental Health in Tech")
    st.caption("2014 OSMI Survey Explorer")
    st.divider()

    uploaded = st.file_uploader("Upload survey.csv (optional)", type=["csv"])
    data_path = uploaded if uploaded is not None else "survey.csv"

try:
    raw_df = load_data(data_path)
except FileNotFoundError:
    st.error(
        "Couldn't find **survey.csv**. Place it next to `app.py`, "
        "or upload it using the sidebar uploader."
    )
    st.stop()

with st.sidebar:
    st.markdown("### 🔎 Filters")

    countries = sorted(raw_df["Country"].unique().tolist())
    top_countries_default = raw_df["Country"].value_counts().head(5).index.tolist()
    sel_countries = st.multiselect("Country", countries, default=top_countries_default)

    gender_opts = sorted(raw_df["Gender_Clean"].unique().tolist())
    sel_genders = st.multiselect("Gender", gender_opts, default=gender_opts)

    age_min, age_max = int(raw_df["Age"].min()), int(raw_df["Age"].max())
    sel_age = st.slider("Age range", age_min, age_max, (age_min, age_max))

    company_sizes = ["1-5", "6-25", "26-100", "100-500", "500-1000", "More than 1000"]
    company_sizes = [c for c in company_sizes if c in raw_df["no_employees"].unique()]
    sel_company = st.multiselect("Company size", company_sizes, default=company_sizes)

    treatment_opts = raw_df["treatment"].unique().tolist()
    sel_treatment = st.multiselect("Sought treatment?", treatment_opts, default=treatment_opts)

    st.divider()
    reset = st.button("↺ Reset filters", use_container_width=True)

if reset:
    st.rerun()

mask = (
    raw_df["Country"].isin(sel_countries if sel_countries else countries)
    & raw_df["Gender_Clean"].isin(sel_genders)
    & raw_df["Age"].between(sel_age[0], sel_age[1])
    & raw_df["no_employees"].isin(sel_company if sel_company else company_sizes)
    & raw_df["treatment"].isin(sel_treatment if sel_treatment else treatment_opts)
)
df = raw_df.loc[mask].copy()

with st.sidebar:
    st.caption(f"Showing **{len(df):,}** of {len(raw_df):,} responses")
    st.download_button(
        "⬇ Download filtered data (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_mental_health_survey.csv",
        mime="text/csv",
        use_container_width=True,
    )

if df.empty:
    st.warning("No responses match the current filters. Try widening your selection in the sidebar.")
    st.stop()


# ----------------------------------------------------------------------
# HERO HEADER
# ----------------------------------------------------------------------
st.markdown('<div class="hero-title">Mental Health in Tech — Survey Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Interactive exploration of the 2014 OSMI Mental Health in Tech Survey — '
    "demographics, workplace support, and attitudes toward mental health disclosure.</div>",
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------------------------------------------------
# KPI ROW
# ----------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
treated_pct = (df["treatment"] == "Yes").mean() * 100
fam_hist_pct = (df["family_history"] == "Yes").mean() * 100
benefits_pct = (df["benefits"] == "Yes").mean() * 100
know_care_pct = (df["care_options"] == "Yes").mean() * 100

with c1:
    kpi_card("Respondents", f"{len(df):,}")
with c2:
    kpi_card("Sought Treatment", f"{treated_pct:.1f}%", "% who have sought mental health treatment")
with c3:
    kpi_card("Family History", f"{fam_hist_pct:.1f}%", "% with a family history of mental illness")
with c4:
    kpi_card("Have Benefits", f"{benefits_pct:.1f}%", "% whose employer provides mental health benefits")
with c5:
    kpi_card("Know Care Options", f"{know_care_pct:.1f}%", "% who know their employer's mental health care options")

st.write("")

# ----------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------
tab_overview, tab_demo, tab_support, tab_attitudes, tab_corr, tab_data = st.tabs(
    ["📊 Overview", "👥 Demographics", "🏢 Workplace Support", "💬 Attitudes", "🔗 Correlations", "🗂 Raw Data"]
)

# ---------------- OVERVIEW ----------------
with tab_overview:
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown("#### Treatment-Seeking Overview")
        treat_counts = df["treatment"].value_counts().reset_index()
        treat_counts.columns = ["Sought Treatment", "Count"]
        fig = px.pie(
            treat_counts, names="Sought Treatment", values="Count", hole=0.55,
            color_discrete_sequence=[PRIMARY, ACCENT], template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Age Distribution")
        fig = px.histogram(
            df, x="Age", nbins=25, template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[ACCENT],
        )
        fig.add_vline(x=df["Age"].median(), line_dash="dash", line_color=PRIMARY,
                       annotation_text=f"median={df['Age'].median():.0f}")
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=360, bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""<div class="insight-box">💡 <b>Insight:</b> In the current selection,
        <b>{treated_pct:.1f}%</b> of respondents have sought mental health treatment.
        The respondent base is concentrated in the 25–40 age range, reflecting the
        core working-age tech population captured by this survey.</div>""",
        unsafe_allow_html=True,
    )

    st.write("")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### Top Countries by Respondents")
        top_c = df["Country"].value_counts().head(10).reset_index()
        top_c.columns = ["Country", "Count"]
        fig = px.bar(
            top_c.sort_values("Count"), x="Count", y="Country", orientation="h",
            template=PLOTLY_TEMPLATE, color="Count", color_continuous_scale="Purp",
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.markdown("#### Respondents by Company Size")
        size_order = ["1-5", "6-25", "26-100", "100-500", "500-1000", "More than 1000"]
        size_counts = df["no_employees"].value_counts().reindex(size_order).dropna().reset_index()
        size_counts.columns = ["Company Size", "Count"]
        fig = px.bar(
            size_counts, x="Company Size", y="Count", template=PLOTLY_TEMPLATE,
            color="Count", color_continuous_scale="Teal",
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- DEMOGRAPHICS ----------------
with tab_demo:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Gender Distribution")
        gender_counts = df["Gender_Clean"].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig = px.bar(
            gender_counts, x="Gender", y="Count", color="Gender",
            color_discrete_sequence=COLOR_SEQ, template=PLOTLY_TEMPLATE, text="Count",
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Age Group vs Treatment")
        age_treat = df.groupby(["Age_Group", "treatment"], observed=True).size().reset_index(name="Count")
        fig = px.bar(
            age_treat, x="Age_Group", y="Count", color="treatment", barmode="group",
            color_discrete_sequence=[PRIMARY, ACCENT], template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380, legend_title="Sought Treatment")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Age Distribution by Treatment Status")
    fig = px.box(
        df, x="treatment", y="Age", color="treatment",
        color_discrete_sequence=[PRIMARY, ACCENT], template=PLOTLY_TEMPLATE, points="outliers",
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """<div class="insight-box">💡 <b>Insight:</b> Treatment-seeking rates and
        age distributions look broadly similar across groups, suggesting mental health
        support needs are widespread rather than concentrated in one demographic segment.</div>""",
        unsafe_allow_html=True,
    )

# ---------------- WORKPLACE SUPPORT ----------------
with tab_support:
    st.markdown("#### How Employer Support Relates to Treatment-Seeking")
    support_var = st.selectbox(
        "Choose a workplace-support factor to compare against treatment:",
        ["benefits", "care_options", "wellness_program", "seek_help", "anonymity", "remote_work"],
        format_func=lambda x: x.replace("_", " ").title(),
    )

    col1, col2 = st.columns([1.4, 1])
    with col1:
        ct = pd.crosstab(df[support_var], df["treatment"], normalize="index") * 100
        ct = ct.reset_index().melt(id_vars=support_var, var_name="treatment", value_name="pct")
        fig = px.bar(
            ct, x=support_var, y="pct", color="treatment", barmode="group",
            color_discrete_sequence=[PRIMARY, ACCENT], template=PLOTLY_TEMPLATE,
            labels={"pct": "% Sought Treatment", support_var: support_var.replace("_", " ").title()},
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Ease of Mental Health Leave")
        leave_order = ["Very easy", "Somewhat easy", "Don't know", "Somewhat difficult", "Very difficult"]
        leave_counts = df["leave"].value_counts().reindex(leave_order).dropna().reset_index()
        leave_counts.columns = ["Leave Ease", "Count"]
        fig = px.bar(
            leave_counts, x="Count", y="Leave Ease", orientation="h",
            color="Count", color_continuous_scale="Sunset", template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    best = ct.loc[ct["treatment"] == "Yes"].sort_values("pct", ascending=False).iloc[0]
    st.markdown(
        f"""<div class="insight-box">💡 <b>Insight:</b> Respondents whose answer to
        <b>{support_var.replace('_',' ')}</b> is <b>"{best[support_var]}"</b> show the highest
        treatment-seeking rate (<b>{best['pct']:.1f}%</b>) among this factor's categories —
        awareness of support tends to matter as much as its existence.</div>""",
        unsafe_allow_html=True,
    )

# ---------------- ATTITUDES ----------------
with tab_attitudes:
    st.markdown("#### Willingness to Discuss Mental Health")
    comfort_vars = ["coworkers", "supervisor", "mental_health_interview", "phys_health_interview"]
    comfort_data = []
    for v in comfort_vars:
        vc = df[v].value_counts(normalize=True) * 100
        for k, val in vc.items():
            comfort_data.append({"Question": v.replace("_", " ").title(), "Response": k, "Percent": val})
    comfort_df = pd.DataFrame(comfort_data)
    fig = px.bar(
        comfort_df, x="Question", y="Percent", color="Response", barmode="stack",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQ,
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=420)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Fear of Negative Consequences")
        mhc = df["mental_health_consequence"].value_counts().rename_axis("Response").reset_index(name="Count")
        fig = px.bar(
            mhc, x="Response", y="Count", template=PLOTLY_TEMPLATE,
            color="Response", color_discrete_sequence=COLOR_SEQ,
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Observed Negative Consequences for Coworkers")
        oc = df["obs_consequence"].value_counts().rename_axis("Response").reset_index(name="Count")
        fig = px.pie(
            oc, names="Response", values="Count", hole=0.55,
            color_discrete_sequence=[PRIMARY, ACCENT], template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=360)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """<div class="insight-box">💡 <b>Insight:</b> Employees are typically more
        comfortable discussing mental health with coworkers than with a direct supervisor,
        pointing to a trust gap that manager training could help close.</div>""",
        unsafe_allow_html=True,
    )

# ---------------- CORRELATIONS ----------------
with tab_corr:
    st.markdown("#### Correlation Heatmap of Key Encoded Variables")
    encode_cols = ["family_history", "treatment", "remote_work", "tech_company",
                   "benefits", "care_options", "wellness_program", "seek_help",
                   "anonymity", "mental_health_consequence", "phys_health_consequence",
                   "obs_consequence"]
    df_enc = df[encode_cols + ["Age"]].copy()
    for c in encode_cols:
        df_enc[c] = df_enc[c].astype("category").cat.codes
    corr = df_enc.corr()
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        template=PLOTLY_TEMPLATE, aspect="auto",
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=560)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """<div class="insight-box">💡 <b>Insight:</b> <code>family_history</code> shows the
        strongest positive correlation with <code>treatment</code>, while support-related
        variables (benefits, care options, anonymity) cluster together — confirming that both
        personal risk factors and workplace support infrastructure drive treatment-seeking.</div>""",
        unsafe_allow_html=True,
    )

# ---------------- RAW DATA ----------------
with tab_data:
    st.markdown("#### Filtered Dataset")
    st.dataframe(df, use_container_width=True, height=520)
    st.caption(f"{len(df):,} rows × {df.shape[1]} columns (after filtering)")

st.write("")
st.markdown(
    '<div style="text-align:center; color:#5b6472; font-size:0.85rem; padding: 10px;">'
    "Built with Streamlit &nbsp;•&nbsp; Data: 2014 OSMI Mental Health in Tech Survey"
    "</div>",
    unsafe_allow_html=True,
)
