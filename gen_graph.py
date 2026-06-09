import pandas as pd
import networkx as nx
from pyvis.network import Network

df = pd.read_csv("set50_stakeholders.csv")
G = nx.Graph()
for _, r in df.iterrows():
    co = f"{r['company_symbol']}: {r['company_name']}"
    sh = r['stakeholder_name']
    G.add_node(co, type='company', sector=r['sector'])
    G.add_node(sh, type=r['stakeholder_type'])
    G.add_edge(co, sh, weight=r['ownership_pct'])

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
    'Foreign Institution': '#6c5ce7', 'Individual': '#fdcb6e',
    'Asset Management': '#a29bfe',
}

net = Network(height="750px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=False)
net.toggle_physics(True)

for n, d in G.nodes(data=True):
    if d['type'] == 'company':
        net.add_node(
            n, label=n.split(":")[0], title=f"Sector: {d['sector']}<br>Type: Company",
            color=sector_colors.get(d.get('sector', 'Other'), '#dfe6e9'),
            size=28, shape='dot', borderWidth=2,
        )
    else:
        net.add_node(
            n, label=n, title=f"Type: {d['type']}",
            color=type_colors.get(d['type'], '#b2bec3'),
            size=14, shape='dot',
        )

for u, v, d in G.edges(data=True):
    net.add_edge(u, v, value=d['weight'] / 5, title=f"{d['weight']:.1f}%", color='rgba(255,255,255,0.25)')

net.set_options("""var options = {
  "nodes": {"font": {"size": 10, "face": "Tahoma"}},
  "edges": {"smooth": {"type": "continuous"}},
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -100,
      "centralGravity": 0.005,
      "springLength": 200,
      "springConstant": 0.01,
      "damping": 0.4
    },
    "maxVelocity": 50,
    "solver": "forceAtlas2Based",
    "stabilization": {"iterations": 300}
  }
}""")
net.write_html("set50_network.html", open_browser=False, notebook=False)
print("Generated set50_network.html")
