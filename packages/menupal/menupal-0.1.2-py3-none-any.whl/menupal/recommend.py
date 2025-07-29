import numpy as np
import pandas as pd
from typing import List, Optional
from sklearn.metrics import pairwise_distances, pairwise_kernels

from .preprocessing import get_data, num_cols

def build_feature_sims(
    df: pd.DataFrame,
    weights: List[float] = [0.4, 0.35, 0.35]
) -> np.ndarray:
    """
    用數值特徵與食材特徵計算相似度，並依 alpha 合併。
    
    參數
    ----
    df : 特徵 DataFrame (n_samples, n_features)
    weights : List[float], 數值特徵、食材特徵、菜單特徵的權重
    
    回傳
    ----
    sim_comb : 合併後的相似度矩陣 (n_samples, n_samples)
    """
    # 數值特徵相似度
    sim_num = pairwise_kernels(df[num_cols].values, metric='cosine')
    
    # 食材特徵相似度 one-hot
    df_ing_cols = [col for col in df.columns if col.startswith('ing_')]
    bin_ing = (df[df_ing_cols].values > 0).astype(bool)
    dist_ing = pairwise_distances(bin_ing, metric='jaccard')
    sim_ing = 1 - dist_ing
    
    # 菜單特徵相似度 one-hot
    df_dish_cols = [col for col in df.columns if col.startswith('dish_')]
    bin_dish = (df[df_dish_cols].values > 0).astype(bool)
    dist_dish = pairwise_distances(bin_dish, metric='jaccard')
    sim_dish = 1 - dist_dish
    
    # 加權合併
    sim_comb = weights[0] * sim_num + weights[1] * sim_ing + weights[2] * sim_dish
    
    return sim_comb

def recommend(
    df: pd.DataFrame,
    sim: np.ndarray,
    id_input: int,
    top_k: int = 5,
    cols: Optional[List[str]] = None
) -> Optional[pd.DataFrame]:
    """
    根據相似度矩陣，為輸入 id 推薦最相似的 top_k 道菜單，並附上 0–10 分的推薦指數。

    參數:
      df: 含原始欄位的 DataFrame，需有唯一的 'id' 欄並設定為索引或可透過 df['id'] 查找。
      sim: (n_samples, n_samples) 相似度矩陣，值域應在 [0,1]。
      id_input: 要查詢的菜單 id。
      top_k: 推薦數量。
      cols: 回傳結果顯示的欄位，若為 None 則顯示所有欄位（含 'score'）。

    回傳:
      包含 top_k 筆推薦菜單及其 0–10 推薦指數的子 DataFrame，依推薦指數由大到小排序。
    """
    # 先透過 get_indexer 檢查 id_input 是否存在
    idx = df.index.get_loc(df.index[df['id'] == id_input][0])
    if idx == -1:
        return None

    # 取得相似度 row，並排除自身
    sim_row = sim[idx].copy()
    sim_row[idx] = -1

    # 取 top_k 個最相似的索引
    top_idx = np.argsort(sim_row)[-top_k:][::-1]

    # 線性映射到 1–5
    mapped = sim_row[top_idx] * 5 + 1
    # 四捨五入 0.5 的倍數
    score = np.round(mapped * 2) / 2
    # 限制最大值為 5
    score = np.clip(score, None, 5)

    # 組成結果表
    result = df.iloc[top_idx].copy()
    result['score'] = score

    # 篩選欄位
    if cols:
        cols_out = cols + ['score'] if 'score' not in cols else cols
        result = result[cols_out]

    return result

if __name__ == "__main__":
    # 讀取資料並產生特徵
    df_raw, df_feat = get_data("./data/mcd_menu_nutrition.xlsx")
    
    OUTPUT_DIR = "./model"
    
    # 隨機抽一筆測試 id，分別用兩種相似度推薦
    test_id = np.random.choice(df_raw['id'].unique())
    test_id = 200019
    mask = df_raw['id'] == test_id
    test_name = df_raw[mask]['name'].iloc[0]
    test_category = df_raw[mask]['category'].iloc[0]
    test_calories = df_raw[mask]['calories'].iloc[0]
    
    print(f"\nTest ID: {test_id} → {test_name} {test_category} {test_calories}")
    # [數值特徵、食材特徵、菜單特徵的權重]
    weights = [0.4, 0.45, 0.3]
    weights_str = "_".join(s.split(".")[1] for s in map(str, weights))
    
    sim_comb = build_feature_sims(df_feat, weights)

    print("\n-- 內容特徵合併相似度推薦 --")
    print(recommend(df_raw, sim_comb, test_id, top_k=10)[['score', 'name', 'category', 'calories']])
    
    from .recviz import (
        RecommendationData,
        draw_simple_recommendations,
        draw_detailed_recommendations,
        draw_variance_charts,
        draw_detailed_2d_scatter,
        # draw_3d_visualization
    )
    
    # 視覺化
    rec_data = RecommendationData(df_feat, df_raw, sim_comb, test_id, 10)
    # draw_simple_recommendations(rec_data)
    # draw_detailed_recommendations(rec_data)
    # draw_variance_charts(rec_data)
    # draw_detailed_2d_scatter(rec_data)
    # draw_3d_visualization(rec_data)