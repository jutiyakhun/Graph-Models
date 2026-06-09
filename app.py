import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import plotly.express as px
import math
from pathlib import Path

DATA_PATH = Path(__file__).parent / "set50_stakeholders.csv"

st.set_page_config(page_title="SET50 Shareholder Network", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

@st.cache_data
def build_graph(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        company = f"{row['company_symbol']}: {row['company_name']}"
        stakeholder = row['stakeholder_name']
        G.add_node(company, type='company', sector=row['sector'], symbol=row['company_symbol'])
        G.add_node(stakeholder, type=row['stakeholder_type'])
        G.add_edge(company, stakeholder, weight=row['ownership_pct'], label=f"{row['ownership_pct']}%")
    return G

def generate_pyvis_html(G, sector_filter, type_filter):
    net = Network(height="700px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=False)

    sector_colors = {
        'Energy & Utilities': '#ff6b6b', 'Banking': '#4ecdc4', 'Commerce': '#45b7d1',
        'Food & Beverage': '#96ceb4', 'Property Development': '#ffeaa7',
        'Health Care Services': '#dfe6e9', 'Transportation & Logistics': '#fdcb6e',
        'Information & Communication Technology': '#6c5ce7', 'Electronic Components': '#00cec9',
        'Petrochemicals & Chemicals': '#fab1a0', 'Finance & Securities': '#81ecec',
        'Construction Materials': '#636e72', 'Packaging': '#b2bec3', 'Insurance': '#fd79a8',
    }
    type_colors = {
        'Corporate': '#0984e3', 'Family': '#e17055', 'Nominee': '#636e72',
        'Government': '#00b894', 'Government Fund': '#00b894',
        'Foreign Institution': '#6c5ce7', 'Individual': '#fdcb6e', 'Asset Management': '#a29bfe',
    }

    visible_companies = {n for n, d in G.nodes(data=True) if d['type'] == 'company' and d.get('sector') in sector_filter}

    visible_stakeholders = set()
    for u, v, d in G.edges(data=True):
        if u in visible_companies and v not in visible_stakeholders:
            if G.nodes[v].get('type') in type_filter:
                visible_stakeholders.add(v)
        if v in visible_companies and u not in visible_stakeholders:
            if G.nodes[u].get('type') in type_filter:
                visible_stakeholders.add(u)

    visible = visible_companies | visible_stakeholders

    pos = {}
    company_list = sorted(visible_companies)
    n = len(company_list)
    radius = 400
    for i, node in enumerate(company_list):
        angle = 2 * math.pi * i / n
        pos[node] = (radius * math.cos(angle), radius * math.sin(angle))

    for node in visible_stakeholders:
        connected = [c for c in G.neighbors(node) if c in visible_companies]
        if connected:
            pos[node] = (sum(pos[c][0] for c in connected) / len(connected),
                         sum(pos[c][1] for c in connected) / len(connected))
        else:
            pos[node] = (0, 0)

    for node in visible:
        data = G.nodes[node]
        x, y = pos[node]
        if data['type'] == 'company':
            net.add_node(
                node, label=data.get('symbol', node),
                title=f"{node}<br>Sector: {data['sector']}",
                color=sector_colors.get(data['sector'], '#dfe6e9'),
                size=28, shape='dot', borderWidth=2, borderColor='#ffffff',
                x=x, y=y,
            )
        else:
            net.add_node(
                node, label=node,
                title=f"Type: {data['type']}",
                color=type_colors.get(data['type'], '#b2bec3'),
                size=14, shape='dot',
                x=x, y=y,
            )

    for u, v, d in G.edges(data=True):
        if u in visible and v in visible:
            net.add_edge(u, v, value=max(d['weight'] / 10, 0.5),
                         title=d['label'], color='rgba(255,255,255,0.25)')

    net.set_options("""var options = {
  "nodes": {
    "font": {"size": 10, "face": "Tahoma", "color": "#ffffff"},
    "borderWidth": 1, "borderWidthSelected": 3
  },
  "edges": {
    "smooth": {"type": "continuous", "roundness": 0.3},
    "color": {"inherit": false},
    "width": 1
  },
  "physics": {"enabled": false},
  "interaction": {
    "hover": true,
    "hoverConnectedEdges": true,
    "tooltipDelay": 100,
    "hideEdgesOnDrag": true
  }
}""")
    return net.generate_html()

df = load_data()
G = build_graph(df)

all_sectors = sorted(df['sector'].unique())
all_types = sorted(df['stakeholder_type'].unique())

st.title("SET50 Shareholder Social Network")
st.markdown("Mapping ownership relationships between SET50 companies and their top 5 stakeholders")

col1, col2 = st.columns(2)
with col1:
    selected_sectors = st.multiselect("Filter by Sector", all_sectors, default=all_sectors)
with col2:
    selected_types = st.multiselect("Filter by Stakeholder Type", all_types, default=all_types)

tab1, tab2, tab3, tab4 = st.tabs(["Network Graph", "Ownership Analysis", "Sector Overview", "Data Table"])

with tab1:
    st.markdown("**Nodes:** Companies (large) — Stakeholders (small) | Hover to highlight connections")
    if not selected_sectors:
        st.warning("Please select at least one sector.")
    else:
        with st.spinner("Generating network..."):
            html = generate_pyvis_html(G, selected_sectors, selected_types)
        st.components.v1.html(html, height=720)

with tab2:
    st.subheader("Top Stakeholders by Ownership")
    top_n = st.slider("Number of top stakeholders", 5, 30, 15)
    top_stakeholders = (
        df.groupby('stakeholder_name')['ownership_pct']
        .sum().sort_values(ascending=False).head(top_n).reset_index()
    )
    fig = px.bar(
        top_stakeholders, x='ownership_pct', y='stakeholder_name',
        orientation='h', title=f"Top {top_n} Stakeholders by Total Ownership Across SET50",
        labels={'ownership_pct': 'Total Ownership (%)', 'stakeholder_name': 'Stakeholder'},
        color='ownership_pct', color_continuous_scale='Viridis',
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Largest Concentrated Ownership")
    concentrated = df.nlargest(10, 'ownership_pct')[
        ['company_symbol', 'company_name', 'stakeholder_name', 'ownership_pct']
    ]
    fig2 = px.bar(
        concentrated, x='ownership_pct', y='stakeholder_name',
        color='company_symbol', orientation='h',
        title="Top 10 Largest Single-Shareholder Holdings",
        labels={'ownership_pct': 'Ownership (%)', 'stakeholder_name': 'Stakeholder'},
        text='company_symbol',
    )
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Sector Distribution of SET50")
    sector_counts = df[['company_symbol', 'sector']].drop_duplicates()['sector'].value_counts().reset_index()
    sector_counts.columns = ['sector', 'count']
    fig3 = px.pie(sector_counts, values='count', names='sector', title="Companies by Sector", hole=0.4)
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Average Ownership by Stakeholder Type per Sector")
    avg_own = df.groupby(['sector', 'stakeholder_type'])['ownership_pct'].mean().reset_index()
    fig4 = px.sunburst(
        avg_own, path=['sector', 'stakeholder_type'], values='ownership_pct',
        title="Stakeholder Type Composition by Sector", color='ownership_pct',
        color_continuous_scale='RdBu_r',
    )
    fig4.update_layout(height=600)
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("Raw Data")
    search = st.text_input("Search by company or stakeholder name")
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df['company_name'].str.contains(search, case=False, na=False) |
            filtered_df['stakeholder_name'].str.contains(search, case=False, na=False)
        ]
    st.dataframe(filtered_df, use_container_width=True, height=500)

st.markdown("---")
st.markdown("Data: SET50 constituent companies and their top 5 shareholders as reported to the Stock Exchange of Thailand.")
