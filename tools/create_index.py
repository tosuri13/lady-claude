import os
import pickle

from faiss import IndexFlatIP, write_index

from lady_claude.common.aws.s3 import upload

# NOTE: Cohere Embed - Multilingualモデルの次元数
DEFAULT_INDEX_DIMENSIONS = 1024

RECIPES_FAISS_FILE_NAME = "index.faiss"
RECIPES_PICKLE_FILE_NAME = "recipes.pkl"

RECIPE_VECTORSTORE_BUCKET_NAME = os.environ["RECIPE_VECTORSTORE_BUCKET_NAME"]

if __name__ == "__main__":
    index = IndexFlatIP(DEFAULT_INDEX_DIMENSIONS)
    recipes = []

    write_index(index, f"./tmp/{RECIPES_FAISS_FILE_NAME}")
    with open(f"./tmp/{RECIPES_PICKLE_FILE_NAME}", "wb") as file:
        pickle.dump(recipes, file)

    upload(
        bucket_name=RECIPE_VECTORSTORE_BUCKET_NAME,
        object_name=RECIPES_FAISS_FILE_NAME,
        file_name=f"./tmp/{RECIPES_FAISS_FILE_NAME}",
    )
    upload(
        bucket_name=RECIPE_VECTORSTORE_BUCKET_NAME,
        object_name=RECIPES_PICKLE_FILE_NAME,
        file_name=f"./tmp/{RECIPES_PICKLE_FILE_NAME}",
    )
