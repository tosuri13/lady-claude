import json
import pickle
from typing import Dict, List

import numpy as np
from faiss import IndexFlatIP, read_index

from lady_claude.common.ai.lady_claude import ask_lady
from lady_claude.common.aws.bedrock import converse, embed
from lady_claude.common.aws.s3 import download
from lady_claude.common.aws.ssm import get_parameter
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.event.lady_claude import (
    LadyClaudeCommand,
    LadyClaudeRecipeOptionCommand,
)
from lady_claude.common.util import get_lady_error_comment

RECIPES_FAISS_FILE_NAME = "index.faiss"
RECIPES_PICKLE_FILE_NAME = "recipes.pkl"


def handler(event: dict, context: dict) -> None:
    try:
        for record in event["Records"]:
            message = record["Sns"]["Message"]
            message_attributes = record["Sns"]["MessageAttributes"]
            command = message_attributes["command"]["Value"]

            if command != LadyClaudeCommand.RECIPE.value:
                raise ValueError(
                    f"This Lambda only supports '/{LadyClaudeCommand.RECIPE.value}' [command: /{command}]"
                )

            request = json.loads(message)
            content = _handle_request(request)
            respond_interaction(content, interaction_token=request["token"])

    except Exception as exception:
        respond_interaction(
            get_lady_error_comment(exception),
            interaction_token=request["token"],
        )

    return None


def _handle_request(request: dict) -> str:
    options = get_option_dict(request["data"]["options"])
    bucket_name = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/RECIPE/VECTORSTORE_BUCKET_NAME"
    )

    download(
        bucket_name,
        object_name=RECIPES_FAISS_FILE_NAME,
        file_name=f"/tmp/{RECIPES_FAISS_FILE_NAME}",
    )
    download(
        bucket_name,
        object_name=RECIPES_PICKLE_FILE_NAME,
        file_name=f"/tmp/{RECIPES_PICKLE_FILE_NAME}",
    )

    index = read_index(f"/tmp/{RECIPES_FAISS_FILE_NAME}")
    with open(f"/tmp/{RECIPES_PICKLE_FILE_NAME}", "rb") as file:
        recipes = pickle.load(file)

    match options["action"]:
        case LadyClaudeRecipeOptionCommand.LIST.value:
            return _handle_list_action(recipes)
        case LadyClaudeRecipeOptionCommand.SEARCH.value:
            return _handle_search_action(options["order"], index, recipes)
        # case LadyClaudeRecipeOptionCommand.REGIST.value:
        #     return _handle_regist_action(table_name)
        # case LadyClaudeRecipeOptionCommand.DELETE.value:
        #     return _handle_delete_action(table_name)
        case _:
            return (
                "わたくしそのようなアクションには対応しておりませんわ...セバスチャン(開発者)に聞いてくれるかしら?\n"
                "(どうやってわたくしに命じたのですの...?)"
            )


def _handle_list_action(recipes: List[Dict]) -> str:
    formatted_recipes = "\n".join(["- " + recipe["name"] for recipe in recipes])

    return (
        f"わたくしが覚えているレシピの一覧ですわ!!\n"
        f"こちらに載っていないレシピがありましたら、わたくしにレシピの登録を命じてくださいまし!!\n"
        f"```\n"
        f"{formatted_recipes}\n"
        f"```"
    )


def _handle_search_action(order: str, index: IndexFlatIP, recipes: List[Dict]) -> str:
    query_vector = np.array([embed(order)], dtype="float32")
    _, indices = index.search(query_vector, k=1)  # type: ignore

    recipe = recipes[indices[0][0]]
    return ask_lady(
        message=(
            f"今から質問に関係するレシピの名前とレシピの手順を見せるから、これらを参考に質問に答えて!!\n"
            f"\n"
            f"## レシピ名\n"
            f"{recipe['name']}\n"
            f"\n"
            f"## レシピの手順\n"
            f"{recipe['procedure']}\n"
            f"\n"
            f"## 質問\n"
            f"{order}"
        )
    )
