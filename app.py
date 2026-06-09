import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DATA_PATH = Path(__file__).parent / "set50_stakeholders.csv"

st.set_page_config(page_title="SET50 Shareholder Network", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

@st.cache_data
def build_graph(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        company = f"{row['company_symbol']}: {row['company_name']}"
        stakeholder = row['stakeholder_name']
        G.add_node(company, type='company', sector=row['sector'])
        G.add_node(stakeholder, type=row['stakeholder_type'])
        G.add_edge(company, stakeholder, weight=row['ownership_pct'], label=f"{row['ownership_pct']}%")
    return G

def generate_pyvis_html(G, company_nodes, sector_filter=None, type_filter=None):
    net = Network(height="700px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=False)
    net.toggle_physics(True)

    sector_colors = {
        'Energy & Utilities': '#ff6b6b',
        'Banking': '#4ecdc4',
        'Commerce': '#45b7d1',
        'Food & Beverage': '#96ceb4',
        'Property Development': '#ffeaa7',
        'Health Care Services': '#dfe6e9',
        'Transportation & Logistics': '#fdcb6e',
        'Information & Communication Technology': '#6c5ce7',
        'Electronic Components': '#00cec9',
        'Petrochemicals & Chemicals': '#fab1a0',
        'Finance & Securities': '#81ecec',
        'Construction Materials': '#636e72',
        'Packaging': '#b2bec3',
        'Insurance': '#fd79a8',
    }

    type_colors = {
        'Corporate': '#0984e3',
        'Family': '#e17055',
        'Nominee': '#636e72',
        'Government': '#00b894',
        'Government Fund': '#00b894',
        'Foreign Institution': '#6c5ce7',
        'Individual': '#fdcb6e',
        'Asset Management': '#a29bfe',
    }

    for node in G.nodes(data=True):
        if sector_filter and node[1].get('type') == 'company' and node[1].get('sector') not in sector_filter:
            continue
        if type_filter and node[1].get('type') != 'company' and node[1].get('type') not in type_filter:
            continue
        if node[1]['type'] == 'company':
            sector = node[1].get('sector', 'Other')
            color = sector_colors.get(sector, '#dfe6e9')
            net.add_node(node[0], label=node[0], title=f"Sector: {sector}<br>Type: Company", color=color, size=25, shape='dot', borderWidth=2, borderColor='#ffffff')
        else:
            color = type_colors.get(node[1]['type'], '#b2bec3')
            net.add_node(node[0], label=node[0], title=f"Type: {node[1]['type']}", color=color, size=15, shape='dot')

    for edge in G.edges(data=True):
        u, v, d = edge
        net.add_edge(u, v, value=d['weight'] / 5, title=d['label'], color='rgba(255,255,255,0.3)')

    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 10,
          "face": "Tahoma",
          "color": "#ffffff"
        },
        "borderWidth": 1
      },
      "edges": {
        "smooth": {
          "type": "continuous"
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "centralGravity": 0.005,
          "springLength": 200,
          "springConstant": 0.01,
          "damping": 0.4
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "iterations": 200
        }
      }
    }
    """)
    return net.generate_html()

st.title("SET50 Shareholder Social Network")
st.markdown("Mapping ownership relationships between SET50 companies and their top 5 stakeholders")

df = load_data()
G = build_graph(df)

company_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'company']
stakeholder_nodes = [n for n, d in G.nodes(data=True) if d['type'] != 'company']

all_sectors = sorted(df['sector'].unique())
all_types = sorted(df['stakeholder_type'].unique())

col1, col2 = st.columns(2)
with col1:
    selected_sectors = st.multiselect("Filter by Sector", all_sectors, default=all_sectors[:3] if len(all_sectors) > 0 else all_sectors)
with col2:
    selected_types = st.multiselect("Filter by Stakeholder Type", all_types, default=all_types)

tab1, tab2, tab3, tab4 = st.tabs(["Network Graph", "Ownership Analysis", "Sector Overview", "Data Table"])

with tab1:
    st.subheader("Interactive Ownership Network")
    st.markdown("**Nodes:** Companies (large) and Stakeholders (small) | **Edges:** Ownership %")
    st.markdown("Drag nodes to explore. Scroll to zoom.")
    with st.spinner("Generating network..."):
        html = generate_pyvis_html(G, company_nodes, selected_sectors, selected_types)
    st.components.v1.html(html, height=720)

with tab2:
    st.subheader("Top Stakeholders by Ownership")
    top_n = st.slider("Number of top stakeholders", 5, 30, 15)
    top_stakeholders = (
        df.groupby('stakeholder_name')['ownership_pct']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    fig = px.bar(
        top_stakeholders,
        x='ownership_pct',
        y='stakeholder_name',
        orientation='h',
        title=f"Top {top_n} Stakeholders by Total Ownership Across SET50",
        labels={'ownership_pct': 'Total Ownership (%)', 'stakeholder_name': 'Stakeholder'},
        color='ownership_pct',
        color_continuous_scale='Viridis',
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Largest Concentrated Ownership")
    concentrated = df.nlargest(10, 'ownership_pct')[['company_symbol', 'company_name', 'stakeholder_name', 'ownership_pct']]
    fig2 = px.bar(
        concentrated,
        x='ownership_pct',
        y='stakeholder_name',
        color='company_symbol',
        orientation='h',
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
        avg_own,
        path=['sector', 'stakeholder_type'],
        values='ownership_pct',
        title="Stakeholder Type Composition by Sector",
        color='ownership_pct',
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
