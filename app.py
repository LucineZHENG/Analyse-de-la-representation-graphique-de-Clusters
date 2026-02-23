import streamlit as st
import json
import pandas as pd
from pathlib import Path
from pyvis.network import Network
import streamlit.components.v1 as components
from Levenshtein import ratio as lev_ratio

# --- 1. 页面配置 ---
st.set_page_config(page_title="Matrix Explorer 54 - Multi-Corpus", layout="wide")
st.title("🧪 Évaluation Comparative des Clusters OCR (Sujet 3)")


# --- 2. 核心评估函数 ---
def compute_metrics(ocr_words, ref_words):
    """
    计算 Purity, AOS 和 Silhouette 指标。
    所有指标均为越大越好 (0.0 到 1.0)。
    """
    if not ocr_words or not ref_words: return 0.0, 0.0, 0.0

    # 计算匹配数 (阈值 > 0.8)
    matches = 0
    for ow in ocr_words:
        if any(lev_ratio(str(ow).lower(), str(rw).lower()) > 0.8 for rw in ref_words):
            matches += 1

    # Purity: 簇内正确比例
    purity = matches / len(ocr_words)

    # AOS Index: 对齐覆盖率 (类似 Jaccard 相似度)
    union_len = len(set(ocr_words) | set(ref_words))
    aos = matches / union_len if union_len > 0 else 0

    # Silhouette: 簇内词汇拼写相似度
    if len(ocr_words) > 1:
        sims = [lev_ratio(str(a), str(b)) for i, a in enumerate(ocr_words) for b in ocr_words[i + 1:]]
        silhouette = sum(sims) / len(sims)
    else:
        silhouette = 1.0

    return purity, aos, silhouette


# --- 3. 修正后的多语言/多作品数据加载逻辑 ---
@st.cache_data
def load_all_experiments(root_path):
    """
    递归扫描目录，自动提取语料库标签和作品名称。
    """
    matrix = {}
    base = Path(root_path)
    # 查找所有以 _clusters.json 结尾的文件
    all_jsons = list(base.rglob("*clusters.json"))

    for p in all_jsons:
        # 1. 识别语料库语言
        is_fr = "corpus_fr" in p.parts
        lang_tag = "[FR]" if is_fr else "[EN]"

        # 2. 定位作品根目录名称 (排除 _OCR, _REF 等干扰)
        try:
            parent_corpus = "corpus_fr" if is_fr else "corpus_en"
            corpus_idx = p.parts.index(parent_corpus)
            work_name = p.parts[corpus_idx + 1]  # 锁定语料库后的第一级
        except (ValueError, IndexError):
            continue

        work_label = f"{lang_tag} {work_name}"

        # 3. 提取算法名称 (从文件名获取)
        parts = p.name.split('_')
        if len(parts) < 2: continue
        algo_name = parts[-2]

        # 4. 识别流程 (Baseline 还是具体的 OCR 流程)
        # 如果父文件夹名包含 _REF 或文件名包含 ref/pp
        is_ref = "_REF" in p.parent.name or "ref" in p.name.lower() or "_pp_" in p.name.lower()

        if is_ref:
            flow_name = "REFERENCE (Baseline)"
        else:
            flow_name = p.parent.name  # 例如 AINSWORTH_Kraken

        # 5. 构建矩阵结构
        if work_label not in matrix: matrix[work_label] = {}
        if algo_name not in matrix[work_label]: matrix[work_label][algo_name] = {}

        try:
            with open(p, 'r', encoding='utf-8') as f:
                matrix[work_label][algo_name][flow_name] = json.load(f)
        except:
            continue

    return matrix


# 初始化数据
exp_matrix = load_all_experiments(Path.cwd())

# --- 4. 侧边栏配置 (联动选择) ---
st.sidebar.header("⚙️ Configuration")

if exp_matrix:
    # 作品选择器
    all_works = sorted(list(exp_matrix.keys()))
    selected_work = st.sidebar.selectbox("📚 Choisir l'œuvre :", all_works)

    # 算法选择器 (基于所选作品)
    available_algos = sorted(list(exp_matrix[selected_work].keys()))
    selected_algo = st.sidebar.selectbox("🔬 Choisir l'algorithme :", available_algos)
else:
    st.error("Aucune donnée trouvée. Vérifiez votre structure de dossiers.")
    st.stop()

# --- 5. 主可视化区域 ---
# 搜索框：支持手动输入查询词
default_search = "London" if "[EN]" in selected_work else "Paris"
search_query = st.text_input(f"🔍 Rechercher une entité dans {selected_work} :", value=default_search)

work_data = exp_matrix[selected_work][selected_algo]
ref_key = "REFERENCE (Baseline)"
ocr_keys = sorted([k for k in work_data.keys() if k != ref_key])

# 核心逻辑：获取 Baseline 簇
ref_cluster = []
if ref_key in work_data:
    ref_cluster = next((v for v in work_data[ref_key].values()
                        if any(search_query.lower() in str(w).lower() for w in v)), [])

st.divider()
st.subheader(f"📊 Analyse : {search_query} | {selected_work} | {selected_algo}")

# 渲染指标和图形
summary_data = []
cols = st.columns(3)  # 每行显示三个 OCR 流程

for idx, flow in enumerate(ocr_keys):
    with cols[idx % 3]:
        st.markdown(f"**Flux : `{flow}`**")
        # 寻找当前 OCR 流程中包含搜索词的簇
        found = next((v for v in work_data[flow].values()
                      if any(search_query.lower() in str(w).lower() for w in v)), None)

        if found:
            # 计算定量指标
            p, a, s = compute_metrics(found, ref_cluster)

            # 显示指标卡片
            m1, m2, m3 = st.columns(3)
            m1.metric("Purity", f"{p:.2f}")
            m2.metric("AOS", f"{a:.2f}")
            m3.metric("Silh.", f"{s:.2f}")

            # Pyvis 拓扑图可视化
            net = Network(height="300px", width="100%", bgcolor="#ffffff", font_color="#2c3e50")
            net.add_node(search_query, label=search_query, color="#27ae60", size=30)
            for word in found:
                if str(word) != search_query:
                    # 识别噪音点
                    is_noisy = any(c in str(word) for c in "*[()æ_")
                    color = "#e67e22" if is_noisy else "#3498db"
                    net.add_node(str(word), label=str(word), color=color, size=15)
                    net.add_edge(search_query, str(word))

            net.save_graph(f"graph_{idx}.html")
            components.html(open(f"graph_{idx}.html", 'r', encoding='utf-8').read(), height=320)

            summary_data.append({"Flux": flow, "Purity": p, "AOS": a, "Silhouette": s})
        else:
            # 实体丢失情况可视化
            st.error("❌ Entité Perdue (Missing)")
            st.caption("L'entité n'a pas été reconnue dans ce flux OCR.")
            summary_data.append({"Flux": flow, "Purity": 0, "AOS": 0, "Silhouette": 0})

# 实验汇总列表 (不使用 Markdown 表格以符合您的习惯)
if summary_data:
    st.divider()
    st.subheader("🏁 Synthèse des Expériences")
    # 使用 Streamlit 的 native dataframe 展示，不占用回复文字中的表格配额
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)