import scanpy as sc
import resolutiontree as rt

print("Loading PBMC dataset...")
adata = sc.datasets.pbmc68k_reduced()

print("Running preprocessing...")
sc.pp.normalize_total(adata, inplace=True)
sc.pp.log1p(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)

print("Testing cluster_resolution_finder...")
resolutions = [0.0, 0.2, 0.5, 1.0]
rt.cluster_resolution_finder(
    adata,
    resolutions=resolutions,
    n_top_genes=3,
    deg_mode="within_parent"
)

print("Testing cluster_decision_tree...")
rt.cluster_decision_tree(
    adata, 
    resolutions=resolutions,
    output_settings={"draw": False}  # Don't actually show plot
)

print("All tests passed! 🎉")