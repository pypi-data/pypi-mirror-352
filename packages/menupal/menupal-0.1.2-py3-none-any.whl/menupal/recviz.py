from matplotlib.axes import Axes
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd
from sklearn.decomposition import PCA
from typing import Tuple
from dataclasses import dataclass

# Font configuration
FONT_PATH = Path('./data/Microsoft JhengHei.ttf')
if FONT_PATH.exists():
    font_entry = fm.FontEntry(fname=str(FONT_PATH), name='Microsoft JhengHei')
    fm.fontManager.ttflist.append(font_entry)
    plt.rcParams['font.family'] = 'Microsoft JhengHei'
    plt.rcParams['axes.unicode_minus'] = False

@dataclass
class RecommendationData:
    """
    封裝推薦系統所需的數據參數。
    
    Attributes
    ----------
    feature_data : pd.DataFrame
        經過特徵工程後的特徵數據框
    raw_data : pd.DataFrame
        包含原始欄位（特別是 'id' 欄位）的數據框
    similarity_matrix : np.ndarray
        相似度矩陣，形狀為 (n_items, n_items)
    target_id : int
        查詢的目標項目 ID
    neighbor_count : int, default=5
        要顯示的推薦項目數量
    """
    feature_data: pd.DataFrame
    raw_data: pd.DataFrame
    similarity_matrix: np.ndarray
    target_id: int
    neighbor_count: int = 5

def find_similar_items(data: RecommendationData) -> Tuple[int, np.ndarray]:
    """
    找出目標項目和其最相似的鄰居項目。
    
    Parameters
    ----------
    data : RecommendationData
        包含推薦所需數據的對象
        
    Returns
    -------
    Tuple[int, np.ndarray]
        目標項目索引和相似鄰居索引數組
    """
    target_index = data.raw_data.index[data.raw_data['id'] == data.target_id][0]
    neighbor_indices = np.argsort(data.similarity_matrix[target_index])[::-1]
    neighbor_indices = neighbor_indices[neighbor_indices != target_index][:data.neighbor_count]
    return target_index, neighbor_indices

def reduce_dimensions_with_pca(feature_data: pd.DataFrame, component_count: int = 2) -> Tuple[PCA, np.ndarray]:
    """
    使用 PCA 對特徵數據進行降維處理。
    
    Parameters
    ----------
    feature_data : pd.DataFrame
        特徵數據框
    component_count : int, default=2
        主成分數量
        
    Returns
    -------
    Tuple[PCA, np.ndarray]
        擬合的 PCA 模型和降維後的坐標
    """
    pca_model = PCA(n_components=component_count, random_state=42)
    reduced_coordinates = pca_model.fit_transform(feature_data.values)
    return pca_model, reduced_coordinates

def draw_recommendation_scatter(ax: Axes, coordinates: np.ndarray, target_index: int, 
                               neighbor_indices: np.ndarray, target_id: int) -> None:
    """
    繪製推薦系統的散點圖，顯示目標項目和推薦項目。
    
    Parameters
    ----------
    ax : Axes
        matplotlib 軸對象
    coordinates : np.ndarray
        2D 坐標數組
    target_index : int
        目標項目索引
    neighbor_indices : np.ndarray
        推薦項目索引數組
    target_id : int
        目標項目 ID
    """
    all_x, all_y = coordinates[:, 0], coordinates[:, 1]
    target_x, target_y = coordinates[target_index]
    neighbor_x, neighbor_y = coordinates[neighbor_indices].T

    ax.scatter(all_x, all_y, c='lightgray', s=30, label='All Items')
    ax.scatter(neighbor_x, neighbor_y, c='blue', s=60, label='Recommendations')
    ax.scatter(target_x, target_y, c='red', s=100, label='Target')

    # Draw connection arrows
    for nx, ny in zip(neighbor_x, neighbor_y):
        dx, dy = nx - target_x, ny - target_y
        ax.arrow(target_x, target_y, dx, dy, color='blue', alpha=0.6,
                width=0.002, head_width=0.1, length_includes_head=True)

    ax.set_title(f'Recommendation Results (PCA 2D) - Target ID={target_id}')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.legend(loc='upper right')
    ax.grid(True)

def draw_simple_recommendations(data: RecommendationData) -> None:
    """
    顯示簡單的推薦結果可視化圖表。
    
    在 PCA 2D 空間中顯示目標項目與其推薦項目的關係，
    使用箭頭連線來表示推薦關聯性。
    
    Parameters
    ----------
    data : RecommendationData
        包含推薦所需數據的對象
        
    Examples
    --------
    >>> rec_data = RecommendationData(features_df, raw_df, similarity_matrix, 123, 10)
    >>> draw_simple_recommendations(rec_data)
    """
    target_index, neighbor_indices = find_similar_items(data)
    pca_model, coordinates = reduce_dimensions_with_pca(data.feature_data, component_count=2)
    
    plt.figure(figsize=(8, 6))
    draw_recommendation_scatter(plt.gca(), coordinates, target_index, neighbor_indices, data.target_id)
    plt.tight_layout()
    plt.show()

def draw_enhanced_scatter(ax: Axes, coordinates: np.ndarray, target_index: int, 
                         neighbor_indices: np.ndarray, similarity_matrix: np.ndarray, 
                         target_id: int) -> None:
    """
    繪製增強版散點圖，包含相似度顏色映射。
    
    Parameters
    ----------
    ax : Axes
        matplotlib 軸對象
    coordinates : np.ndarray
        2D 坐標數組
    target_index : int
        目標項目索引
    neighbor_indices : np.ndarray
        推薦項目索引數組
    similarity_matrix : np.ndarray
        相似度矩陣
    target_id : int
        目標項目 ID
        
    Returns
    -------
    matplotlib.collections.PathCollection
        散點圖對象，用於添加顏色條
    """
    all_x, all_y = coordinates[:, 0], coordinates[:, 1]
    target_x, target_y = coordinates[target_index]
    neighbor_x, neighbor_y = coordinates[neighbor_indices].T

    ax.scatter(all_x, all_y, c='lightgray', s=30, alpha=0.5, label='All Items')
    scatter = ax.scatter(neighbor_x, neighbor_y, c=similarity_matrix[target_index][neighbor_indices], 
                        s=100, cmap='viridis', label='Recommendations')
    ax.scatter(target_x, target_y, c='red', s=150, label='Target', marker='*')
    
    ax.set_title(f'PCA 2D Visualization - Target ID={target_id}')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return scatter

def draw_similarity_heatmap(ax: Axes, similarity_matrix: np.ndarray, target_index: int, 
                           neighbor_indices: np.ndarray) -> None:
    """
    繪製相似度矩陣熱力圖。
    
    Parameters
    ----------
    ax : Axes
        matplotlib 軸對象
    similarity_matrix : np.ndarray
        相似度矩陣
    target_index : int
        目標項目索引
    neighbor_indices : np.ndarray
        推薦項目索引數組
        
    Returns
    -------
    matplotlib.image.AxesImage
        熱力圖對象，用於添加顏色條
    """
    selected_indices = np.append([target_index], neighbor_indices)
    sub_matrix = similarity_matrix[np.ix_(selected_indices, selected_indices)]
    heatmap = ax.imshow(sub_matrix, cmap='Blues')
    
    ax.set_title('Similarity Matrix (Target + Recommendations)')
    ax.set_xlabel('Item Index')
    ax.set_ylabel('Item Index')
    
    return heatmap

def draw_detailed_recommendations(data: RecommendationData) -> None:
    """
    顯示詳細的推薦結果分析圖表。
    
    創建雙面板視圖：左側顯示 PCA 降維後的散點圖，右側顯示相似度矩陣熱力圖，
    幫助用戶同時理解空間關係和數值相似度關係。
    
    Parameters
    ----------
    data : RecommendationData
        包含推薦所需數據的對象
        
    Examples
    --------
    >>> rec_data = RecommendationData(features_df, raw_df, similarity_matrix, 123)
    >>> draw_detailed_recommendations(rec_data)
    """
    target_index, neighbor_indices = find_similar_items(data)
    pca_model, coordinates = reduce_dimensions_with_pca(data.feature_data, component_count=2)
    
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Left panel: PCA scatter plot
    scatter = draw_enhanced_scatter(ax1, coordinates, target_index, neighbor_indices, 
                                   data.similarity_matrix, data.target_id)
    
    # Right panel: Similarity matrix heatmap
    heatmap = draw_similarity_heatmap(ax2, data.similarity_matrix, target_index, neighbor_indices)
    
    # Add color bars
    plt.colorbar(scatter, ax=ax1, label='Similarity Score')
    plt.colorbar(heatmap, ax=ax2, label='Similarity Value')
    
    plt.tight_layout()
    plt.show()

def calculate_variance_statistics(pca_model: PCA) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    計算 PCA 變異度統計資訊。
    
    Parameters
    ----------
    pca_model : PCA
        擬合的 PCA 模型
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray, int]
        解釋變異度比例、累積變異度、達到95%變異度所需的主成分數
    """
    variance_ratios = pca_model.explained_variance_ratio_
    cumulative_variance = np.cumsum(variance_ratios) * 100
    components_for_95_percent = np.argmax(cumulative_variance >= 95) + 1
    return variance_ratios, cumulative_variance, components_for_95_percent

def draw_variance_charts(data: RecommendationData) -> None:
    """
    繪製變異度分析圖表。
    
    顯示個別主成分解釋變異度和累積解釋變異度，
    幫助用戶理解 PCA 降維的效果。
    
    Parameters
    ----------
    data : RecommendationData
        包含推薦所需數據的對象
        
    Examples
    --------
    >>> rec_data = RecommendationData(features_df, raw_df, similarity_matrix, 123)
    >>> draw_variance_charts(rec_data)
    """
    max_components = min(data.feature_data.shape[0], data.feature_data.shape[1])
    pca_model, _ = reduce_dimensions_with_pca(data.feature_data, component_count=max_components)
    variance_ratios, cumulative_variance, components_for_95_percent = calculate_variance_statistics(pca_model)
    
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Individual component variance
    display_count = min(20, len(variance_ratios))
    ax1.bar(range(1, display_count + 1), variance_ratios[:display_count] * 100)
    ax1.set_title(f'Individual Component Variance (Top {display_count})')
    ax1.set_xlabel('Principal Component')
    ax1.set_ylabel('Explained Variance (%)')
    ax1.grid(True, alpha=0.3)
    
    # Cumulative explained variance
    ax2.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'bo-', 
             linewidth=2, markersize=4)
    ax2.axhline(y=95, color='r', linestyle='--', alpha=0.7, label='95% Threshold')
    ax2.axvline(x=components_for_95_percent, color='g', linestyle=':', alpha=0.7, 
                label=f'{components_for_95_percent} Components for 95%')
    ax2.set_title('Cumulative Explained Variance')
    ax2.set_xlabel('Number of Components')
    ax2.set_ylabel('Cumulative Variance (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print statistics
    variance_2d = variance_ratios[:2].sum() * 100
    variance_3d = variance_ratios[:3].sum() * 100 if len(variance_ratios) >= 3 else 0
    
    print(f"Data Dimensions: Samples={data.feature_data.shape[0]}, Features={data.feature_data.shape[1]}")
    print("PCA Analysis Results:")
    print(f"First 2 Components Variance: {variance_2d:.2f}%")
    if variance_3d > 0:
        print(f"First 3 Components Variance: {variance_3d:.2f}%")
    print(f"Components for 95% Variance: {components_for_95_percent}")

def draw_detailed_2d_scatter(data: RecommendationData) -> None:
    """
    繪製詳細的 2D PCA 散點圖。
    
    顯示目標項目和推薦項目在 PCA 2D 空間中的分布，
    包含相似度顏色映射和詳細的變異度資訊。
    
    Parameters
    ----------
    data : RecommendationData
        包含推薦所需數據的對象
        
    Examples
    --------
    >>> rec_data = RecommendationData(features_df, raw_df, similarity_matrix, 123)
    >>> draw_detailed_2d_scatter(rec_data)
    """
    target_index, neighbor_indices = find_similar_items(data)
    
    # Use PCA to reduce high-dimensional features to 2D space
    pca_model, coordinates = reduce_dimensions_with_pca(data.feature_data, component_count=2)
    variance_ratios = pca_model.explained_variance_ratio_
    
    # Calculate and display 2D PCA explained variance
    explained_variance_2d = variance_ratios[:2].sum() * 100
    print(f"2D PCA Explained Variance: {explained_variance_2d:.2f}%")
    print(f"PC1: {variance_ratios[0]*100:.2f}%, PC2: {variance_ratios[1]*100:.2f}%")
    
    # Extract coordinate data
    all_x, all_y = coordinates[:, 0], coordinates[:, 1]  # x, y coordinates of all items
    target_x, target_y = coordinates[target_index]        # target item coordinates
    neighbor_x, neighbor_y = coordinates[neighbor_indices].T  # recommended item coordinates
    
    plt.figure(figsize=(10, 7))
    
    # Plot background scatter points for all items (light gray)
    plt.scatter(all_x, all_y, c='lightgray', s=20, alpha=0.5, label='All Items')
    
    # Plot recommended items with color mapping based on similarity scores
    # Use viridis colormap where higher similarity shows brighter colors
    scatter = plt.scatter(neighbor_x, neighbor_y, 
                         c=data.similarity_matrix[target_index][neighbor_indices], 
                         s=80, cmap='viridis', edgecolors='black', 
                         linewidth=0.5, label='Recommendations')
    
    # Plot target item (red star marker)
    plt.scatter(target_x, target_y, c='red', s=120, marker='*', 
               edgecolors='darkred', linewidth=2, label='Target')
    
    # Set chart title and axis labels
    plt.title(f'Detailed 2D PCA Projection - Target ID={data.target_id}')
    plt.xlabel(f'PC1 ({variance_ratios[0]*100:.1f}%)')  # First principal component with explained variance
    plt.ylabel(f'PC2 ({variance_ratios[1]*100:.1f}%)')  # Second principal component with explained variance
    
    # Add legend, grid, and colorbar
    plt.legend()
    plt.grid(True, alpha=0.3)  # Add semi-transparent grid lines
    plt.colorbar(scatter, label='Similarity Score')  # Show colorbar for similarity scores
    
    plt.tight_layout()
    plt.show()

def draw_3d_visualization(data: RecommendationData) -> None:
    """
    繪製 3D PCA 可視化。
    
    在 3D 空間中顯示目標項目和推薦項目的關係，
    包含連接線來表示推薦關聯性。
    
    Parameters
    ----------
    data : RecommendationData
        包含推薦所需數據的對象
        
    Examples
    --------
    >>> rec_data = RecommendationData(features_df, raw_df, similarity_matrix, 123)
    >>> draw_3d_visualization(rec_data)
    """
    target_index, neighbor_indices = find_similar_items(data)
    max_components = min(data.feature_data.shape[0], data.feature_data.shape[1])
    
    if max_components < 3:
        print("Insufficient components for 3D visualization")
        return
    
    pca_model, coordinates = reduce_dimensions_with_pca(data.feature_data, component_count=3)
    variance_ratios = pca_model.explained_variance_ratio_
    
    # Calculate and print 3D PCA explained variance
    explained_variance_3d = variance_ratios[:3].sum() * 100
    print(f"3D PCA Explained Variance: {explained_variance_3d:.2f}%")
    print(f"PC1: {variance_ratios[0]*100:.2f}%, PC2: {variance_ratios[1]*100:.2f}%, PC3: {variance_ratios[2]*100:.2f}%")
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Background points
    ax.scatter(coordinates[:, 0], coordinates[:, 1], coordinates[:, 2], 
               c='lightgray', s=15, alpha=0.8, label='All Items')
    
    # Target point
    ax.scatter(coordinates[target_index, 0], coordinates[target_index, 1], 
               coordinates[target_index, 2], c='red', s=100, marker='*', 
               edgecolors='darkred', linewidth=2, label='Target')
    
    # Recommendation points
    ax.scatter(coordinates[neighbor_indices, 0], coordinates[neighbor_indices, 1], 
               coordinates[neighbor_indices, 2], c='blue', s=60, label='Recommendations')
    
    # Connection lines
    for neighbor_idx in neighbor_indices:
        ax.plot([coordinates[target_index, 0], coordinates[neighbor_idx, 0]],
                [coordinates[target_index, 1], coordinates[neighbor_idx, 1]],
                [coordinates[target_index, 2], coordinates[neighbor_idx, 2]],
                'b-', alpha=0.4, linewidth=1)
    
    ax.set_title(f'3D PCA Visualization - Target ID={data.target_id}')
    ax.set_xlabel(f'PC1 ({variance_ratios[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({variance_ratios[1]*100:.1f}%)')
    ax.set_zlabel(f'PC3 ({variance_ratios[2]*100:.1f}%)')
    ax.legend()
    
    plt.tight_layout()
    plt.show()