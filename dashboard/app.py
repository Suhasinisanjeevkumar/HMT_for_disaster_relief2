"""
Stage 8 -- Dashboard.

Run with:  streamlit run dashboard/app.py

Two tabs: (1) analyze a single claim through the full pipeline, (2) an
overview of the stored dataset -- both driven by real precomputed/live
values, nothing here is a placeholder number.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd

from analyze_claim import analyze_claim

st.set_page_config(page_title="HMT — Hyperlocal Misinformation Tracker", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "ifnd_full.parquet")

# Approximate state-capital coordinates, used only for the overview map.
# These are stable, well-known geographic facts (state capitals), not
# derived from the gazetteer dataset, which has no lat/lon columns.
STATE_COORDS = {
    "Karnataka": (12.9716, 77.5946), "Maharashtra": (19.0760, 72.8777),
    "Kerala": (8.5241, 76.9366), "Tamil Nadu": (13.0827, 80.2707),
    "Andhra Pradesh": (16.5062, 80.6480), "Telangana": (17.3850, 78.4867),
    "West Bengal": (22.5726, 88.3639), "Bihar": (25.5941, 85.1376),
    "Uttar Pradesh": (26.8467, 80.9462), "Uttaranchal": (30.3165, 78.0322),
    "Assam": (26.1445, 91.7362), "Orissa": (20.2961, 85.8245),
    "Gujarat": (23.0225, 72.5714), "Rajasthan": (26.9124, 75.7873),
    "Punjab": (30.7333, 76.7794), "Haryana": (29.0588, 76.0856),
    "Delhi": (28.6139, 77.2090), "Madhya Pradesh": (23.2599, 77.4126),
    "Chhattisgarh": (21.2787, 81.8661), "Jharkhand": (23.3441, 85.3096),
    "Himachal Pradesh": (31.1048, 77.1734), "Jammu & Kashmir": (34.0837, 74.7973),
    "Goa": (15.2993, 74.1240), "Arunachal Pradesh": (27.0844, 93.6053),
    "Meghalaya": (25.4670, 91.3662), "Manipur": (24.6637, 93.9063),
    "Mizoram": (23.1645, 92.9376), "Nagaland": (25.6751, 94.1086),
    "Tripura": (23.9408, 91.9882), "Sikkim": (27.5330, 88.5122),
    "Chandigarh": (30.7333, 76.7794), "Pondicherry": (11.9416, 79.8083),
}


@st.cache_resource
def load_data():
    return pd.read_parquet(DATA_PATH)


@st.cache_resource
def get_analyzer():
    return analyze_claim  # module-level singletons in analyze_claim.py handle model loading once


df = load_data()
analyze = get_analyzer()

st.title("HMT — Hyperlocal Misinformation Tracker")
st.caption("Research prototype · disaster relief · not a live monitoring system")

tab1, tab2 = st.tabs(["Analyze a claim", "Dataset overview"])

with tab1:
    st.subheader("Enter disaster-related claim:")
    text = st.text_area("Claim text", placeholder="e.g. Heavy rainfall has caused severe flooding in Whitefield, Bengaluru.",
                         height=100, label_visibility="collapsed")

    if st.button("Analyze", type="primary"):
        if not text.strip():
            st.warning("Enter a claim first.")
        else:
            with st.spinner("Running disaster detection → location → misinformation model → verification..."):
                r = analyze(text)

            c1, c2, c3 = st.columns(3)
            verdict_color = {"TRUE": "green", "FAKE": "red", "UNVERIFIED": "orange"}[r["prediction"]]
            c1.metric("Prediction", r["prediction"])
            c2.metric("Confidence", r["confidence"])
            c3.metric("Priority", r["priority"], help=f"score={r['priority_score']}")

            st.markdown(f"**Disaster Type:** {r['disaster_type']}")
            if r["location"]:
                loc = r["location"]
                parts = [p for p in [loc["locality"], loc["city"], loc["district"], loc["state"]] if p]
                st.markdown(f"**Location:** {', '.join(dict.fromkeys(parts))}  "
                            f"<span style='color:gray'>(matched at {loc['match_level']} level)</span>",
                            unsafe_allow_html=True)
                if len(r["all_locations"]) > 1:
                    others = ", ".join(f"{l['text']} ({l['state']})" for l in r["all_locations"])
                    st.caption(f"Multiple locations mentioned: {others}")
            else:
                st.markdown("**Location:** none detected")

            st.markdown("**Reason:**")
            st.write(r["reason"])

            st.markdown("**Verification:**")
            if r["verification"]["matched"]:
                st.success(f"Matching record found ({r['verification']['similarity']} similarity): "
                           f"\"{r['verification']['matched_claim']}\"")
            else:
                st.info("No matching record found in the verified corpus.")
            st.caption(r["verification"]["note"])

            if r["top_terms"]:
                st.markdown("**Why the model said this (top contributing words):**")
                terms_df = pd.DataFrame(r["top_terms"], columns=["term", "contribution"])
                st.dataframe(terms_df, hide_index=True, width='stretch')

with tab2:
    st.subheader("Dataset overview")
    st.caption("All figures below are computed from the 1,002-claim disaster subset processed through Stages 2-7. "
               "Not live data — a static research dataset.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total claims", len(df))
    c2.metric("TRUE", int((df["verdict"] == "TRUE").sum()))
    c3.metric("FAKE", int((df["verdict"] == "FAKE").sum()))
    c4.metric("UNVERIFIED", int((df["verdict"] == "UNVERIFIED").sum()))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Disaster type distribution**")
        st.bar_chart(df["primary_type"].value_counts())
    with col2:
        st.markdown("**Priority distribution**")
        st.bar_chart(df["priority"].value_counts())

    st.markdown("**Location distribution (top states)**")
    state_counts = df["location_state"].value_counts().head(15)
    st.bar_chart(state_counts)

    st.markdown("**Map (approximate state centroids — the gazetteer has no lat/lon data, "
               "so this is state-level only, not the hyperlocal precision the pipeline resolves)**")
    map_rows = []
    for state, count in df["location_state"].value_counts().items():
        if state in STATE_COORDS:
            lat, lon = STATE_COORDS[state]
            map_rows.append({"lat": lat, "lon": lon, "count": count})
    if map_rows:
        st.map(pd.DataFrame(map_rows), size="count")

    st.markdown("**Processed claims**")
    show_cols = ["Statement", "primary_type", "location_state", "location_level", "Label", "verdict", "priority"]
    st.dataframe(df[show_cols].rename(columns={
        "Statement": "Claim", "primary_type": "Disaster Type", "location_state": "State",
        "location_level": "Loc. Level", "Label": "IFND Label (ground truth)", "verdict": "Model Verdict",
        "priority": "Priority",
    }), hide_index=True, width='stretch', height=400)
