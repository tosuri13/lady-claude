import pickle

from faiss import IndexFlatIP, write_index

from lady_claude.common.aws.s3 import upload
from lady_claude.common.aws.ssm import get_parameter

# NOTE: Cohere Embed - Multilingual次元数を採用
DEFAULT_INDEX_DIMENSIONS = 1024

RECIPES_FAISS_FILE_NAME = "index.faiss"
RECIPES_PICKLE_FILE_NAME = "recipes.pkl"

if __name__ == "__main__":
    index = IndexFlatIP(DEFAULT_INDEX_DIMENSIONS)
    recipes = []

    write_index(index, f"./tmp/{RECIPES_FAISS_FILE_NAME}")
    with open(f"./tmp/{RECIPES_PICKLE_FILE_NAME}", "wb") as file:
        pickle.dump(recipes, file)

    bucket_name = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/RECIPE/VECTORSTORE_BUCKET_NAME"
    )
    upload(
        bucket_name,
        object_name=RECIPES_FAISS_FILE_NAME,
        file_name=f"./tmp/{RECIPES_FAISS_FILE_NAME}",
    )
    upload(
        bucket_name,
        object_name=RECIPES_PICKLE_FILE_NAME,
        file_name=f"./tmp/{RECIPES_PICKLE_FILE_NAME}",
    )
