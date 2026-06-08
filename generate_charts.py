import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

out_dir = os.path.join(os.path.dirname(__file__), 'report_images')
os.makedirs(out_dir, exist_ok=True)

# --- Common styling ---
DARK_BG = '#0f1729'
CARD_BG = '#1a2332'
GRID_COLOR = '#2a3a4a'
TEXT_COLOR = '#e0e0e0'
COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6']

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor': CARD_BG,
    'axes.edgecolor': GRID_COLOR,
    'axes.labelcolor': TEXT_COLOR,
    'xtick.color': TEXT_COLOR,
    'ytick.color': TEXT_COLOR,
    'text.color': TEXT_COLOR,
    'font.family': 'sans-serif',
    'font.size': 11,
})

# ============================================================
# CHART 1: Scoring Metrics Bar Chart (actual results)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))
metrics = ['Semantic\nSimilarity', 'Skill\nMatch', 'Section\nCoverage', 'Keyword\nDensity', 'Resume\nQuality', 'ATS\nScore']
scores = [5, 75, 50, 33, 61, 81]
bar_colors = ['#ef4444', '#10b981', '#f59e0b', '#ef4444', '#f59e0b', '#10b981']

bars = ax.bar(metrics, scores, color=bar_colors, width=0.6, edgecolor='none', zorder=3)
for bar, score in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{score}', ha='center', va='bottom', fontweight='bold', fontsize=13, color=TEXT_COLOR)

ax.set_ylim(0, 105)
ax.set_ylabel('Score (out of 100)', fontsize=12, fontweight='bold')
ax.set_title('Model Evaluation — Scoring Metrics Comparison', fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='y', color=GRID_COLOR, linewidth=0.5, alpha=0.5)
ax.set_axisbelow(True)

# Legend for color coding
legend_patches = [
    mpatches.Patch(color='#10b981', label='Good (≥60)'),
    mpatches.Patch(color='#f59e0b', label='Average (40-59)'),
    mpatches.Patch(color='#ef4444', label='Needs Work (<40)'),
]
ax.legend(handles=legend_patches, loc='upper right', fontsize=9, facecolor=CARD_BG, edgecolor=GRID_COLOR)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '08_scoring_metrics.png'), dpi=180, bbox_inches='tight')
plt.close()
print("Chart 1: Scoring Metrics — saved")

# ============================================================
# CHART 2: Feature Weight Distribution (Pie Chart)
# ============================================================
fig, ax = plt.subplots(figsize=(8, 6))
labels = ['Skill Match\n(30%)', 'TF-IDF\nSimilarity\n(25%)', 'Semantic\nSimilarity\n(20%)', 'Section\nCoverage\n(15%)', 'Keyword\nDensity\n(10%)']
weights = [30, 25, 20, 15, 10]
pie_colors = ['#6366f1', '#22d3ee', '#10b981', '#f59e0b', '#ef4444']
explode = (0.05, 0.02, 0.02, 0.02, 0.02)

wedges, texts, autotexts = ax.pie(weights, labels=labels, colors=pie_colors, explode=explode,
                                   autopct='%1.0f%%', startangle=140, pctdistance=0.75,
                                   textprops={'fontsize': 10, 'color': TEXT_COLOR})
for t in autotexts:
    t.set_fontsize(11)
    t.set_fontweight('bold')
    t.set_color('white')

ax.set_title('Feature Weight Distribution in Overall Score Formula', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '09_weight_distribution.png'), dpi=180, bbox_inches='tight')
plt.close()
print("Chart 2: Weight Distribution — saved")

# ============================================================
# CHART 3: ATS Scoring Breakdown (Horizontal Bar)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))
factors = ['Keyword Match', 'Standard Headings', 'Contact Info', 'Formatting',
           'Skill Placement', 'Keyword Density', 'File Parsing', 'Spelling',
           'Readability', 'Bullet Structure']
max_pts = [20, 10, 10, 10, 5, 10, 10, 10, 10, 5]
actual_pts = [15, 6.6, 8, 10, 5, 6, 10, 3, 5, 5]  # example scores for the analyzed resume

y_pos = np.arange(len(factors))
bars_max = ax.barh(y_pos, max_pts, color='#2a3a4a', height=0.5, label='Max Points', zorder=2)
bars_act = ax.barh(y_pos, actual_pts, color='#6366f1', height=0.5, label='Actual Score', zorder=3)

for i, (act, mx) in enumerate(zip(actual_pts, max_pts)):
    ax.text(mx + 0.5, i, f'{act:.0f}/{mx}', va='center', fontsize=10, color=TEXT_COLOR)

ax.set_yticks(y_pos)
ax.set_yticklabels(factors, fontsize=10)
ax.set_xlabel('Points', fontsize=12, fontweight='bold')
ax.set_title('ATS Compatibility — 10-Factor Scoring Breakdown (Total: 100)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, 25)
ax.legend(loc='lower right', fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR)
ax.grid(axis='x', color=GRID_COLOR, linewidth=0.5, alpha=0.5)
ax.set_axisbelow(True)
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '10_ats_breakdown.png'), dpi=180, bbox_inches='tight')
plt.close()
print("Chart 3: ATS Breakdown — saved")

# ============================================================
# CHART 4: Algorithm Comparison — Multi-Metric Grouped Bar
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))
categories = ['Speed', 'Synonym\nHandling', 'Context\nAwareness', 'Interpretability', 'Cost\nEfficiency', 'Offline\nCapability']
tfidf_scores = [95, 10, 10, 90, 100, 100]
spacy_scores = [85, 60, 30, 55, 100, 100]
gemini_scores = [25, 95, 95, 60, 40, 0]

x = np.arange(len(categories))
w = 0.25

b1 = ax.bar(x - w, tfidf_scores, w, label='TF-IDF + Cosine', color='#22d3ee', edgecolor='none', zorder=3)
b2 = ax.bar(x, spacy_scores, w, label='Semantic (spaCy)', color='#10b981', edgecolor='none', zorder=3)
b3 = ax.bar(x + w, gemini_scores, w, label='Gemini 2.0 Flash', color='#8b5cf6', edgecolor='none', zorder=3)

ax.set_ylabel('Capability Score (0-100)', fontsize=12, fontweight='bold')
ax.set_title('Algorithm Comparison — Multi-Dimensional Capability Analysis', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10)
ax.set_ylim(0, 115)
ax.legend(loc='upper right', fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR)
ax.grid(axis='y', color=GRID_COLOR, linewidth=0.5, alpha=0.5)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '11_algorithm_comparison.png'), dpi=180, bbox_inches='tight')
plt.close()
print("Chart 4: Algorithm Comparison — saved")

# ============================================================
# CHART 5: Overall Score Composition (Stacked Bar)
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5))
components = ['TF-IDF\n(×0.25)', 'Semantic\n(×0.20)', 'Skill Match\n(×0.30)', 'Section\n(×0.15)', 'Keywords\n(×0.10)']
raw_scores = [5, 5, 75, 50, 33]
weights = [0.25, 0.20, 0.30, 0.15, 0.10]
weighted = [s * w for s, w in zip(raw_scores, weights)]
comp_colors = ['#22d3ee', '#10b981', '#6366f1', '#f59e0b', '#ef4444']

bars = ax.bar(components, weighted, color=comp_colors, width=0.55, edgecolor='none', zorder=3)
for bar, w_val, raw in zip(bars, weighted, raw_scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{w_val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=12, color=TEXT_COLOR)
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
            f'({raw}/100)', ha='center', va='center', fontsize=9, color='white', alpha=0.8)

total = sum(weighted)
ax.axhline(y=total, color='#f59e0b', linestyle='--', linewidth=1.5, alpha=0.7, zorder=4)
ax.text(len(components) - 0.5, total + 0.8, f'Overall: {total:.1f}%', fontsize=12,
        fontweight='bold', color='#f59e0b', ha='right')

ax.set_ylabel('Weighted Contribution to Overall Score', fontsize=11, fontweight='bold')
ax.set_title('Overall Score Composition — Weighted Contribution of Each Feature', fontsize=13, fontweight='bold', pad=15)
ax.set_ylim(0, max(weighted) + 8)
ax.grid(axis='y', color=GRID_COLOR, linewidth=0.5, alpha=0.5)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '12_score_composition.png'), dpi=180, bbox_inches='tight')
plt.close()
print("Chart 5: Score Composition — saved")

print("\nAll 5 evaluation charts generated successfully!")
