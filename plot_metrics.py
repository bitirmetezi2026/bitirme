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

# We will save each plot as a separate PNG file

# 1. Latency Bar Chart (Average Latency)
plt.figure(figsize=(8, 6))
df_valid_latency = df[df["Latency_sec"] > 0]
if not df_valid_latency.empty:
    sns.histplot(data=df_valid_latency, x="Latency_sec", bins=10, kde=True, color="skyblue")
    plt.title("Response Latency Distribution", fontsize=14, fontweight='bold')
    plt.xlabel("Latency (Seconds)")
    plt.ylabel("Number of Questions")
    plt.tight_layout()
    plt.savefig("chart_1_latency_distribution.png", dpi=300)
    plt.close()

# 2. Donut Chart for Routing Decisions
plt.figure(figsize=(8, 6))
if "Router_Decision" in df.columns:
    route_counts = df["Router_Decision"].value_counts()
else:
    route_counts = pd.Series({"Vectorstore (RAG)": len(df[df["Has_Documents"]=="Yes"]), "Web Search": len(df[df["Has_Documents"]=="No"]), "Out of Domain": len(df[df["Hallucination"].str.contains("Greeting|Error", na=False)])})

labels = route_counts.index
sizes = route_counts.values
colors = sns.color_palette("pastel")[0:len(labels)]

wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, 
                                   wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title("Router Decisions (Source)", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("chart_2_router_decisions.png", dpi=300)
plt.close()

# 3. Bar Chart for Success Rates
plt.figure(figsize=(8, 6))
# Sadece Pass veya Fail alanları (N/A olmayanları) sayalım
graded_hallucination = df[df["Hallucination"].isin(["Pass", "Fail"])]
graded_relevance = df[df["Relevance"].isin(["Pass", "Fail"])]

pass_counts = {
    "Hallucination Test Passed": len(graded_hallucination[graded_hallucination["Hallucination"] == "Pass"]) / len(graded_hallucination) * 100 if len(graded_hallucination) > 0 else 0,
    "Answer Relevance Passed": len(graded_relevance[graded_relevance["Relevance"] == "Pass"]) / len(graded_relevance) * 100 if len(graded_relevance) > 0 else 0
}

sns.barplot(x=list(pass_counts.keys()), y=list(pass_counts.values()), hue=list(pass_counts.keys()), palette="viridis", legend=False)
plt.title("Success Rates (%)", fontsize=14, fontweight='bold')
plt.ylim(0, 110)

# Add percentage text on top of bars
ax = plt.gca()
for p in ax.patches:
    ax.annotate(format(p.get_height(), '.1f') + '%', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points')

plt.tight_layout()
plt.savefig("chart_3_success_rates.png", dpi=300)
plt.close()

# 4. Boxplot of Latency by Has_Documents
plt.figure(figsize=(8, 6))
if not df_valid_latency.empty:
    sns.boxplot(data=df_valid_latency, x="Has_Documents", y="Latency_sec", hue="Has_Documents", palette="Set2", legend=False)
    plt.title("Latency by Retrieval Status", fontsize=14, fontweight='bold')
    plt.xlabel("Has Documents Retrieved")
    plt.ylabel("Latency (Seconds)")
    plt.tight_layout()
    plt.savefig("chart_4_latency_by_retrieval.png", dpi=300)
    plt.close()

print("All individual charts saved successfully!")
