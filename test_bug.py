import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DATA_PATH = Path(__file__).parent / "set50_stakeholders.csv"

df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} rows, {df['company_symbol'].nunique()} companies, {df['stakeholder_name'].nunique()} stakeholders")

G = nx.Graph()
for _, row in df.iterrows():
    company = f"{row['company_symbol']}: {row['company_name']}"
    stakeholder = row['stakeholder_name']
    G.add_node(company, type='company', sector=row['sector'])
    G.add_node(stakeholder, type=row['stakeholder_type'])
    G.add_edge(company, stakeholder, weight=row['ownership_pct'])

print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

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

for node, data in G.nodes(data=True):
    if data['type'] == 'company':
        net.add_node(node, label=node, title=f"Sector: {data['sector']}", color=sector_colors.get(data['sector'], '#dfe6e9'), size=25)
    else:
        net.add_node(node, label=node, title=f"Type: {data['type']}", color=type_colors.get(data['type'], '#b2bec3'), size=15)
for u, v, d in G.edges(data=True):
    net.add_edge(u, v, value=d['weight'] / 5, title=f"{d['weight']}%")

result = net.generate_html()
print(f"HTML generated: {len(result)} characters")
print("SUCCESS: No errors")
