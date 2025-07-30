import math
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import spectral_clustering
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
from scipy.spatial.distance import pdist, squareform

"""
### get indexes list in a rectengle of shape (H,W)
indexes = [(i, j) for i in range(H) for j in range(W)]
print(indexes)
"""

def three_pca_as_rgb_image(feats_list,final_image_shape):
    # PCA to 3 components
    """
    Applies Principal Component Analysis (PCA) to reduce a feature array to 3 components 
    and reshapes the result into an RGB image for visualization.

    Parameters:
    ----------
    feats_list : np.ndarray
        A 2D array of shape (N, C), where N is the number of pixels (or spatial locations) 
        and C is the number of feature channels at each location. C must be >= 1.
    
    final_image_shape : tuple
        A tuple of three integers representing the shape (Z, Y, X) or (H, W, D) of the output 
        image volume. The product of these dimensions must match N.

    Returns:
    -------
    rgb_vis : np.ndarray
        A 4D array of shape (*final_image_shape, 3), where the last dimension represents
        the three principal components mapped to RGB channels. The values are normalized 
        to the range [0, 1] for display.
    """
    C = feats_list.shape[-1]

    if C <=3:
        return feats_list.reshape(*final_image_shape,C)
    
    pca = PCA(n_components=3)
    rgb_vis = pca.fit_transform(feats_list).reshape(*final_image_shape, 3)
    # Normalize for display
    rgb_vis = (rgb_vis - rgb_vis.min()) / (rgb_vis.max() - rgb_vis.min())
    return rgb_vis


def construct_knn_graph(feat_lst, knn, image_shape,spatial_neighbour_flag =False, distance_decay_flag=True,d_sigma=2):
    """
    """
    N = feat_lst.shape[0]
    loc_lst = list(np.ndindex(image_shape))

    similarity_matrix = cosine_similarity(feat_lst)
    np.fill_diagonal(similarity_matrix, 0)  # Remove self-loops

    # compute distance deacay
    dist = pdist(loc_lst, metric='euclidean')
    dist_matrix = squareform(dist)
    print(f"distacne_matrix: {dist_matrix.shape}")
    dist_matrix = np.exp(- dist_matrix**2/(2*d_sigma**2))

    if distance_decay_flag:
        similarity_matrix = similarity_matrix * dist_matrix
    else :
        similarity_matrix = similarity_matrix

    
    if spatial_neighbour_flag:
        vec_lst = loc_lst
        nn = NearestNeighbors(n_neighbors= knn +1, metric='euclidean') #self similarity has been removed
        nn.fit(vec_lst)
    else:
        vec_lst = feat_lst
        nn = NearestNeighbors(n_neighbors= knn +1, metric='cosine') #self similarity has been removed
        nn.fit(vec_lst)

    
    knn_graph = np.zeros_like(similarity_matrix)
    for i in range(N):
        neighbors = nn.kneighbors([vec_lst[i]], return_distance=False)[0]
        knn_graph[i, neighbors] = similarity_matrix[i, neighbors]
    
    return (knn_graph + knn_graph.T) / 2  # Ensure symmetry


def sc_plot_grid_results(encoded, img_size, knn_values, num_clusters_values,spatial_neighbour_flag = False ,spatial_decay_flag = True ,d_sigma=8):
    """
    Plot clustering results in a grid for different KNN and cluster numbers.

    Args:
        encoded (np.ndarray or torch.Tensor): Feature map of shape (N, C), where N = H * W.
        img_size (tuple): Size of the original image (H, W).
        knn_values (list of int): List of KNN values to try.
        num_clusters_values (list of int): List of number of clusters to try.

    Example:
        >>> num_clusters_values = [4, 6, 8]
        >>> knn_values = [4, 8, 16, 32]
        >>> sc_plot_grid_results(encoded, img_size, knn_values, num_clusters_values)
    """

    fig, axes = plt.subplots(len(knn_values), len(num_clusters_values), figsize=(len(num_clusters_values) * 4, len(knn_values) * 4))
    
    for i, knn in enumerate(knn_values):
        for j, num_clusters in enumerate(num_clusters_values):
            knn_graph = construct_knn_graph(feat_lst=encoded, knn=knn, image_shape=(img_size),spatial_neighbour_flag=spatial_neighbour_flag,distance_decay_flag=spatial_decay_flag,d_sigma=d_sigma)
            labels = spectral_clustering(knn_graph, n_clusters=num_clusters, eigen_solver="arpack")
            label_image = labels.reshape(img_size)
            
            ax = axes[i,j]
            ax.imshow(label_image, cmap='tab20')
            ax.set_title(f'sc: knn={knn}, clusters={num_clusters},spatial:{spatial_neighbour_flag},d_sigma:{d_sigma}')
            ax.axis('off')
    
    plt.tight_layout()
    plt.show()

def kmeans_grid_results(encoded,img_shape,K_values = [4, 6, 8, 12]):

    fig, axes = plt.subplots(1, len(K_values), figsize=(len(K_values) * 4, 4))  # One row, multiple columns

    for ax, K in zip(axes, K_values):
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=K, random_state=42)
        labels = kmeans.fit_predict(encoded)
        
        # Display label image
        ax.imshow(labels.reshape(img_shape), cmap='tab20')
        ax.set_title(f'sklearn_{K} KMeans')
        ax.axis('off')

    plt.tight_layout()
    plt.show()

def grid_plot_list_imgs(images,col_labels=None,row_labels=None,ncols=3,fig_size=4):

    n_images = len(images)
    ncols = ncols
    nrows = math.ceil(n_images / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_size*ncols,  fig_size*nrows))

    for i, ax in enumerate(axes.flat):
        if i < n_images:
            ax.imshow(images[i], cmap='gray')
        ax.axis('off')
            # Add column labels at top row

        if i < ncols:
            if col_labels:
                ax.set_title(col_labels[i], fontsize=14)

        # Add row labels at first column
        if i % ncols == 0:
            if row_labels:
                ax.set_ylabel(row_labels[i // ncols], fontsize=14, rotation=0, labelpad=40, va='center')


    plt.tight_layout()
    plt.show()