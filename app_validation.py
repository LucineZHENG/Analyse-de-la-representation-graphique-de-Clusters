import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
from Levenshtein import ratio as lev_ratio
import os

# --- 1. 页面配置 ---
st.set_page_config(page_title="Validation Gold Standard - AIMARD", layout="wide")
st.title("🎯 Interface de Validation : Humain vs Automatisé")

# 定义您提供的三个硬编码路径
paths = {
    "REF (Gold Standard)": "/Users/zhengruixing/Desktop/mini-corpus/corpus_fr/AIMARD_TRAPPEURS/AIMARD-TRAPPEURS_REF/AIMARD_les-trappeurs_PP_AffpropKeepVectors_df_points_for_corr-annot-OK.csv",
    "OCR Kraken (Annoté)": "/Users/zhengruixing/Desktop/mini-corpus/corpus_fr/AIMARD_TRAPPEURS/AIMARD-TRAPPEURS_OCR/AIMARD-TRAPPEURS_kraken/AIMARD_les-trappeurs_Kraken-base_AffpropKeepVectors_df_points_for_corr-annot-OK.csv",
    "OCR Tesseract (Annoté)": "/Users/zhengruixing/Desktop/1.9_Gael_Projet/Representation-Graph-Clustering/ClusteringTests-master/corpus/AIMARD_TRAPPEURS/AIMARD-TRAPPEURS_OCR/AIMARD-TRAPPEURS_TesseractFra-PNG/AIMARD_les-trappeurs_TesseractFra-PNG_AffpropKeepVectors_df_points_for_corr-annot-OK.csv"
}


# --- 2. 核心评估逻辑 ---
def compute_metrics(ocr_words, ref_words):
    if not ocr_words or not ref_words: return 0.0, 0.0, 0.0
    matches = sum(1 for ow in ocr_words if any(lev_ratio(str(ow).lower(), str(rw).lower()) > 0.8 for rw in ref_words))
    purity = matches / len(ocr_words)
    union_len = len(set(ocr_words) | set(ref_words))
    aos = matches / union_len if union_len > 0 else 0
    if len(ocr_words) > 1:
        sims = [lev_ratio(str(a), str(b)) for i, a in enumerate(ocr_words) for b in ocr_words[i + 1:]]
        sil = sum(sims) / len(sims)
    else:
        sil = 1.0
    return purity, aos, sil


# --- 3. 数据加载 ---
@st.cache_data
def load_data():
    datasets = {}
    for name, path in paths.items():
        if os.path.exists(path):
            # 自动处理分号分隔符
            df = pd.read_csv(path, sep=None, engine='python')
            datasets[name] = df
        else:
            st.warning(f"Fichier non trouvé : {path}")
    return datasets


data = load_data()

# --- 4. 侧边栏：测试词与规则说明 ---
st.sidebar.header("📋 Règles d'Annotation")
st.sidebar.markdown("""
- **Cluster -1** : Non-entité, chiffres, ponctuation répétée.
- **Symboles** :
  - `?` : Doute sur l'appartenance.
  - `'` : Ne devrait pas faire partie du cluster.
  - `-1` : Hors cluster.
""")

# 基于 AIMARD_les-trappeurs 黄金标准内容的测试词
test_entities = ["Mexico", "Amérique", "Indien", "Soleil", "Comanche", "Espagne", "Rouge", "États", "Luz"]
search_query = st.sidebar.selectbox("Sélectionner un terme de test :", test_entities)

# --- 5. 主界面对比 ---
if data:
    # 提取 REF 中的黄金簇 (基于 cluster_corrected)
    ref_df = data["REF (Gold Standard)"]
    target_row = ref_df[ref_df['text'].astype(str).str.contains(search_query, case=False, na=False)]

    if not target_row.empty:
        gold_cid = target_row['cluster_corrected'].iloc[0]
        gold_cluster = ref_df[ref_df['cluster_corrected'] == gold_cid]['text'].astype(str).tolist()

        st.success(f"📍 Référence Humaine (REF) pour '{search_query}' : {len(gold_cluster)} variantes.")

        cols = st.columns(2)
        flows = ["OCR Kraken (Annoté)", "OCR Tesseract (Annoté)"]

        for idx, flow_name in enumerate(flows):
            with cols[idx]:
                st.subheader(f"🌐 {flow_name}")
                if flow_name in data:
                    df_flow = data[flow_name]
                    # 寻找算法输出的簇
                    found = df_flow[df_flow['text'].astype(str).str.contains(search_query, case=False, na=False)]

                    if not found.empty:
                        algo_cid = found['cluster'].iloc[0]
                        ocr_words = df_flow[df_flow['cluster'] == algo_cid]['text'].astype(str).tolist()

                        p, a, s = compute_metrics(ocr_words, gold_cluster)

                        # 显示指标
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Purity", f"{p:.2f}")
                        m2.metric("AOS", f"{a:.2f}")
                        m3.metric("Silh.", f"{s:.2f}")

                        # 拓扑可视化
                        net = Network(height="400px", width="100%", bgcolor="#f8f9fa")
                        net.add_node(search_query, label=search_query, color="#2ecc71", size=30)
                        for word in ocr_words:
                            if str(word) != search_query:
                                # 检查人工是否判定为噪声 (-1)
                                is_noise = not df_flow[
                                    (df_flow['text'] == word) & (df_flow['cluster_corrected'] == -1)].empty
                                color = "#e67e22" if is_noise else "#3498db"
                                net.add_node(str(word), label=str(word), color=color, size=15)
                                net.add_edge(search_query, str(word))

                        net.save_graph(f"val_{idx}.html")
                        components.html(open(f"val_{idx}.html", 'r').read(), height=420)
                    else:
                        st.error("Entité non trouvée.")
    else:
        st.warning("Terme non présent dans le fichier REF.")