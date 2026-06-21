import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")

# Load the data
csv_file = "evaluation_results.csv"
if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found.")
    exit(1)

df = pd.read_csv(csv_file)

# We will create a dashboard with 4 subplots
fig = plt.figure(figsize=(16, 10))
fig.suptitle("Chatbot Evaluation Metrics Dashboard", fontsize=20, fontweight='bold')

# 1. Latency Bar Chart (Average Latency)
ax1 = plt.subplot(2, 2, 1)
df_valid_latency = df[df["Latency_sec"] > 0]
if not df_valid_latency.empty:
    sns.histplot(data=df_valid_latency, x="Latency_sec", bins=10, kde=True, color="skyblue", ax=ax1)
    ax1.set_title("Response Latency Distribution", fontsize=14)
    ax1.set_xlabel("Latency (Seconds)")
    ax1.set_ylabel("Number of Questions")

# 2. Donut Chart for Routing Decisions
ax2 = plt.subplot(2, 2, 2)
if "Router_Decision" in df.columns:
    route_counts = df["Router_Decision"].value_counts()
else:
    # If using older CSV format, estimate from Has_Documents and relevance
    route_counts = pd.Series({"Vectorstore (RAG)": len(df[df["Has_Documents"]=="Yes"]), "Web Search": len(df[df["Has_Documents"]=="No"]), "Out of Domain": len(df[df["Hallucination"].str.contains("Greeting|Error", na=False)])})

labels = route_counts.index
sizes = route_counts.values
colors = sns.color_palette("pastel")[0:len(labels)]

wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, 
                                   wedgeprops=dict(width=0.4, edgecolor='w'))
ax2.set_title("Router Decisions (Source)", fontsize=14)

# 3. Bar Chart for Success Rates
ax3 = plt.subplot(2, 2, 3)
pass_counts = {
    "Hallucination Test Passed": len(df[df["Hallucination"] == "Pass"]) / len(df) * 100,
    "Answer Relevance Passed": len(df[df["Relevance"] == "Pass"]) / len(df) * 100
}

sns.barplot(x=list(pass_counts.keys()), y=list(pass_counts.values()), palette="viridis", ax=ax3)
ax3.set_title("Success Rates (%)", fontsize=14)
ax3.set_ylim(0, 100)
for p in ax3.patches:
    ax3.annotate(format(p.get_height(), '.1f') + '%', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points')

# 4. Boxplot of Latency by Has_Documents
ax4 = plt.subplot(2, 2, 4)
if not df_valid_latency.empty:
    sns.boxplot(data=df_valid_latency, x="Has_Documents", y="Latency_sec", palette="Set2", ax=ax4)
    ax4.set_title("Latency by Retrieval Status", fontsize=14)
    ax4.set_xlabel("Has Documents Retrieved")
    ax4.set_ylabel("Latency (Seconds)")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
output_filename = "evaluation_dashboard.png"
plt.savefig(output_filename, dpi=300)
print(f"Dashboard saved successfully as {output_filename}")
