import pandas as pd
import ast
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.decomposition import TruncatedSVD

# 定義數值欄位
num_cols = [
    'calories','energy_kcal','protein','fat',
    'carbohydrate','salt','saturated_fat','sugars','trans_fat'
]

def parse_components(s: str) -> dict:
    """將 components 欄位的 JSON 字串解析為 dict"""
    if pd.isna(s):
        return {}
    return ast.literal_eval(s)

def preprocess_data(
    df: pd.DataFrame,
    n_components: int = 50,
    use_svd: bool = False
) -> pd.DataFrame:
    """
    對輸入 DataFrame 做特徵工程：
      1. 數值欄位標準化
      2. 品名與食材 one-hot 編碼，可選 SVD 降維

    參數:
      df           : 原始 DataFrame，需含 num_cols、'dish_names'、'ingredients'
      n_components : 若 use_svd=True，則 SVD 降維後維度
      use_svd      : 是否對 one-hot 矩陣執行 TruncatedSVD

    回傳:
      DataFrame：合併後的特徵矩陣 (n_samples × n_features)
    """
    # 數值標準化
    scaler = StandardScaler()
    num_arr = scaler.fit_transform(df[num_cols])
    df_num = pd.DataFrame(num_arr, columns=num_cols, index=df.index)

    # 品名 one-hot
    mlb_dish = MultiLabelBinarizer(sparse_output=False)
    dish_ohe = mlb_dish.fit_transform(df['dish_names'])
    if use_svd:
        svd_d = TruncatedSVD(n_components=n_components, random_state=42)
        dish_feat = svd_d.fit_transform(dish_ohe)
        dish_cols = [f"dish_svd_{i}" for i in range(dish_feat.shape[1])]
    else:
        dish_feat = dish_ohe
        dish_cols = [f"dish_{c}" for c in mlb_dish.classes_]
    df_dish = pd.DataFrame(dish_feat, columns=dish_cols, index=df.index)

    # 食材 one-hot
    mlb_ing = MultiLabelBinarizer(sparse_output=False)
    ing_ohe = mlb_ing.fit_transform(df['ingredients'])
    if use_svd:
        svd_i = TruncatedSVD(n_components=n_components, random_state=42)
        ing_feat = svd_i.fit_transform(ing_ohe)
        ing_cols = [f"ing_svd_{i}" for i in range(ing_feat.shape[1])]
    else:
        ing_feat = ing_ohe
        ing_cols = [f"ing_{c}" for c in mlb_ing.classes_]
    df_ing = pd.DataFrame(ing_feat, columns=ing_cols, index=df.index)

    # 合併並回傳
    df_all = pd.concat([df_num, df_dish, df_ing], axis=1)
    return df_all

def get_data(file_path: str = "./data/mcd_menu_nutrition.xlsx") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    讀取 Excel，清洗與解析後回傳：
      df_raw: 含原始欄位、components_dict、dish_names、ingredients
      df_feat: 經 preprocess_data() 處理後的特徵 DataFrame
    """
    # 讀取資料
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # 數值欄位清洗
    df[num_cols] = (
        df[num_cols]
        .apply(lambda col: col.fillna(-1).astype(str).str.replace(',', '', regex=True))
        .astype(float)
    )
    df['price'] = df['price'].fillna(-1).astype(float)
    
    # 解析 components
    df['components_dict'] = df['components'].apply(parse_components)
    df['dish_names']  = df['components_dict'].apply(lambda d: list(d.keys()))
    df['ingredients'] = df['components_dict'].apply(lambda d: sum(d.values(), []))
    
    # 產生特徵
    df_feat = preprocess_data(df)
    return df, df_feat

if __name__ == "__main__":
    # 範例執行
    df_raw, df_feat = get_data("./data/mcd_menu_nutrition.xlsx")
    print("原始資料前五筆：")
    print(df_raw.head())
    print("\n處理後特徵前五筆：")
    print(df_feat.head())
