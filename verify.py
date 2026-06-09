import csv
import networkx as nx
from pyvis.network import Network

with open('set50_stakeholders.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f'{len(rows)} rows, {len(set(r["company_symbol"] for r in rows))} companies')

G = nx.Graph()
for row in rows:
    G.add_node(row['company_symbol'], type='company')
    G.add_node(row['stakeholder_name'], type=row['stakeholder_type'])
    G.add_edge(row['company_symbol'], row['stakeholder_name'], weight=float(row['ownership_pct']))

print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

net = Network(height='400px', width='100%', bgcolor='#1a1a2e', font_color='white')
for n, d in G.nodes(data=True):
    net.add_node(n, label=n, color='#ff6b6b' if d['type'] == 'company' else '#4ecdc4')
for u, v, d in G.edges(data=True):
    net.add_edge(u, v, value=d['weight'] / 5)

html = net.generate_html()
assert len(html) > 1000
print('HTML generated OK (' + str(len(html)) + ' chars)')
print('ALL CHECKS PASSED')
