import json
import pickle
from typing import Dict, List

import numpy as np
from faiss import IndexFlatIP, read_index, write_index

from lady_claude.common.ai.lady_claude import ask_lady
from lady_claude.common.aws.bedrock import converse, embed
from lady_claude.common.aws.s3 import download, upload
from lady_claude.common.aws.ssm import get_parameter
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.event.lady_claude import (
    LadyClaudeCommand,
    LadyClaudeRecipeOptionCommand,
)
from lady_claude.common.faiss import delete
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
        raise exception

    return None


def _handle_request(request: dict) -> str:
    options = get_option_dict(request["data"]["options"])
    order = options.get("order", "")
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
        case LadyClaudeRecipeOptionCommand.REGIST.value:
            return _handle_regist_action(order, index, recipes, bucket_name)
        case LadyClaudeRecipeOptionCommand.ASK.value:
            return _handle_ask_action(order, index, recipes)
        case LadyClaudeRecipeOptionCommand.LIST.value:
            return _handle_list_action(recipes)
        case LadyClaudeRecipeOptionCommand.DELETE.value:
            return _handle_delete_action(order, index, recipes, bucket_name)
        case _:
            return (
                "わたくしそのようなアクションには対応しておりませんわ...セバスチャン(開発者)に聞いてくれるかしら?\n"
                "(どうやってわたくしに命じたのですの...?)"
            )


def _handle_regist_action(
    order: str,
    index: IndexFlatIP,
    recipes: List[Dict],
    bucket_name: str,
) -> str:
    if not order:
        return (
            f"あら?わたくしへの命令が見当たらないですわ!!\n"
            f"わたくしに覚えてほしいレシピの名前や材料・手順などを「order」に入力してくださいまし!!"
        )

    response = converse(
        message=order,
        system_message=(
            f"あなたはとても優秀なアシスタントです。\n"
            f"\n"
            f"今からあなたにレシピに関連する文章を与えるので、そこからレシピの名前や材料・手順を抽出し、ツールの引数として提供してもらいます。\n"
            f"与えられた文章からレシピの情報を抽出することが困難な場合は、無理にツールの引数を埋めたりせずに、何が足りないかという理由を返答してください。\n"
            f"\n"
            f"それでは、以下にレシピに関連する文章を示します。"
        ),
        tool_config={
            "toolChoice": {
                "auto": {},
            },
            "tools": [
                {
                    "toolSpec": {
                        "name": "extract",
                        "description": "レシピの名前とレシピの材料・手順を抽出する",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "抽出されたレシピの名前 例: レモネード",
                                    },
                                    "ingredients": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "type": "string",
                                                    "description": "材料の名前 例: レモン",
                                                },
                                                "amount": {
                                                    "type": "string",
                                                    "description": "材料の量 例: 2個, 300gなど",
                                                },
                                                "notes": {
                                                    "type": "string",
                                                    "description": "材料に関する備考 例: 新鮮なものを使用",
                                                },
                                            },
                                            "required": ["name", "amount"],
                                        },
                                        "description": "抽出されたレシピに含まれる材料のリスト",
                                    },
                                    "steps": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "index": {
                                                    "type": "number",
                                                    "description": "手順の番号 例: 1",
                                                },
                                                "step": {
                                                    "type": "string",
                                                    "description": "材料の量 例: レモンの上下を切り落とし、3mm幅にスライスする",
                                                },
                                            },
                                            "required": ["name", "amount"],
                                        },
                                        "description": "抽出されたレシピに含まれる材料のリスト",
                                    },
                                },
                                "required": ["name", "ingredients", "steps"],
                            }
                        },
                    }
                }
            ],
        },
    )

    if response["stopReason"] == "tool_use":
        for content in response["output"]["message"]["content"]:
            if "toolUse" in content:
                tool_args = content["toolUse"]["input"]

        recipe_name = tool_args["name"]
        recipe_ingredients = tool_args["ingredients"]
        recipe_steps = tool_args["steps"]

        formatted_recipe_ingredients = "\n".join(
            [
                f"- {ingredient['name']} {ingredient['amount']} {ingredient.get('notes', '')}"
                for ingredient in recipe_ingredients
            ]
        )
        formatted_recipe_steps = "\n".join(
            [f"{step['index']}. {step['step']}" for step in recipe_steps]
        )

        context = (
            f"# レシピの名前\n"
            f"{recipe_name}\n"
            f"\n"
            f"## レシピの材料\n"
            f"{formatted_recipe_ingredients}\n"
            f"\n"
            f"## レシピの手順\n"
            f"{formatted_recipe_steps}\n"
        )

        index.add(np.array([embed(context)], dtype="float32"))  # type: ignore
        write_index(index, f"/tmp/{RECIPES_FAISS_FILE_NAME}")

        recipes.append(
            {
                "name": recipe_name,
                "context": context,
            }
        )
        with open(f"/tmp/{RECIPES_PICKLE_FILE_NAME}", "wb") as file:
            pickle.dump(recipes, file)

        upload(
            bucket_name,
            object_name=RECIPES_FAISS_FILE_NAME,
            file_name=f"/tmp/{RECIPES_FAISS_FILE_NAME}",
        )
        upload(
            bucket_name,
            object_name=RECIPES_PICKLE_FILE_NAME,
            file_name=f"/tmp/{RECIPES_PICKLE_FILE_NAME}",
        )

        return (
            f"新しく{recipe_name}のレシピを覚えましたわ!!\n"
            f"レシピについて聞きたくなったら、いつでもわたくしに命令してくださいまし!!"
        )
    else:
        return (
            f"あら?レシピに関する情報がうまく取得できなかったみたいですわ...\n"
            f"わたくしへの命令に以下の情報が含まれているか確認してくださるかしら?\n"
            f"```\n"
            f"- レシピの名前\n"
            f"- レシピの材料(数量なども含みますわ!!)\n"
            f"- レシピの手順\n"
            f"```"
        )


def _handle_ask_action(
    order: str,
    index: IndexFlatIP,
    recipes: List[Dict],
) -> str:
    if not order:
        return (
            f"あら?わたくしへの命令が見当たらないですわ!!\n"
            f"わたくしに聞きたいレシピに関する質問を「order」に入力してくださいまし!!"
        )

    if recipes:
        query_vector = np.array([embed(order)], dtype="float32")
        _, indices = index.search(query_vector, k=1)  # type: ignore
        recipe = recipes[indices[0][0]]

        return ask_lady(
            message=(
                f"今から質問に関係するレシピの名前とレシピの手順を見せるから、これらを参考に質問に答えて!!\n"
                f"もし、質問と全然関係ないレシピだったら「別の聞き方でもう一回聞いてほしい」っていう感じで返して!!\n"
                f"\n"
                f"## レシピ名\n"
                f"{recipe['name']}\n"
                f"\n"
                f"## レシピの手順\n"
                f"{recipe['context']}\n"
                f"\n"
                f"## 質問\n"
                f"{order}"
            )
        )
    else:
        return (
            f"あら?わたくしまだ何もレシピを覚えていませんわ...\n"
            f"わたくしに新しくレシピを覚えるよう命じてくださるかしら?"
        )


def _handle_list_action(recipes: List[Dict]) -> str:
    if recipes:
        formatted_recipes = "\n".join(["- " + recipe["name"] for recipe in recipes])

        return (
            f"わたくしが覚えているレシピの一覧ですわ!!\n"
            f"こちらに載っていないレシピがあれば、わたくしに新しくレシピの登録を命じてくださいまし!!\n"
            f"```\n"
            f"{formatted_recipes}\n"
            f"```"
        )
    else:
        return (
            f"あら?わたくしまだ何もレシピを覚えていませんわ...\n"
            f"わたくしに新しくレシピを覚えるよう命じてくださるかしら?"
        )


def _handle_delete_action(
    order: str,
    index: IndexFlatIP,
    recipes: List[Dict],
    bucket_name: str,
) -> str:
    if not order:
        return (
            f"あら?わたくしへの命令が見当たらないですわ!!\n"
            f"わたくしに忘れてほしいレシピの名前や特徴を「order」に入力してくださいまし!!"
        )

    if recipes:
        query_vector = np.array([embed(order)], dtype="float32")
        _, indices = index.search(query_vector, k=1)  # type: ignore
        delete_id = indices[0][0]
        recipe_name = recipes[delete_id]["name"]

        index = delete(index, delete_id)
        recipes.pop(delete_id)
        with open(f"/tmp/{RECIPES_PICKLE_FILE_NAME}", "wb") as file:
            pickle.dump(recipes, file)

        upload(
            bucket_name,
            object_name=RECIPES_FAISS_FILE_NAME,
            file_name=f"/tmp/{RECIPES_FAISS_FILE_NAME}",
        )
        upload(
            bucket_name,
            object_name=RECIPES_PICKLE_FILE_NAME,
            file_name=f"/tmp/{RECIPES_PICKLE_FILE_NAME}",
        )

        return (
            f"わたくしの記憶から{recipe_name}のレシピを削除しましたわ!!\n"
            f"レシピを覚えるのは大変ですし、あまり忘れさせないようにしてくださるかしら...\n"
        )
    else:
        return (
            f"あら?わたくしまだ何もレシピを覚えていませんわ...\n"
            f"わたくしに新しくレシピを覚えるよう命じてくださるかしら?"
        )
