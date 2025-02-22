import json
import os
import pickle
from typing import Dict, List, Tuple

import numpy as np
from faiss import IndexFlatIP, read_index, write_index

from lady_claude.common.ai.lady_claude import ask_lady
from lady_claude.common.aws.bedrock import converse, embed
from lady_claude.common.aws.s3 import download, upload
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.event.lady_claude import LadyClaudeCommand
from lady_claude.common.faiss import delete
from lady_claude.common.util import get_lady_error_comment

RECIPES_FAISS_FILE_NAME = "index.faiss"
RECIPES_PICKLE_FILE_NAME = "recipes.pkl"

RECIPE_VECTORSTORE_BUCKET_NAME = os.environ["RECIPE_VECTORSTORE_BUCKET_NAME"]


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

    download(
        bucket_name=RECIPE_VECTORSTORE_BUCKET_NAME,
        object_name=RECIPES_FAISS_FILE_NAME,
        file_name=f"/tmp/{RECIPES_FAISS_FILE_NAME}",
    )
    download(
        bucket_name=RECIPE_VECTORSTORE_BUCKET_NAME,
        object_name=RECIPES_PICKLE_FILE_NAME,
        file_name=f"/tmp/{RECIPES_PICKLE_FILE_NAME}",
    )

    index = read_index(f"/tmp/{RECIPES_FAISS_FILE_NAME}")
    with open(f"/tmp/{RECIPES_PICKLE_FILE_NAME}", "rb") as file:
        recipes = pickle.load(file)

    action, args = _extact_action(options["order"])

    match action:
        case "register":
            return _handle_regist_action(
                options["order"],
                index,
                recipes,
                bucket_name=RECIPE_VECTORSTORE_BUCKET_NAME,
            )
        case "answer":
            return _handle_ask_action(
                args["question"],
                index,
                recipes,
            )
        case "list":
            return _handle_list_action(recipes)
        case "delete":
            return _handle_delete_action(
                args["recipe_name"],
                index,
                recipes,
                bucket_name=RECIPE_VECTORSTORE_BUCKET_NAME,
            )
        case "none":
            return "レシピ関連の操作や質問以外の内容は受け付けられないですの...別の聞き方をしてくださるかしら?\n"
        case _:
            return (
                "わたくしそのようなアクションには対応しておりませんわ...セバスチャン(開発者)に聞いてくれるかしら?\n"
                "(どうやってわたくしに命じたのですの...?)"
            )


def _extact_action(order: str) -> Tuple[str, dict]:
    response = converse(
        message=order,
        system_message=(
            "あなたはとても優秀なアシスタントです。\n"
            "\n"
            "私はいまレシピ情報を利用してユーザの質問にRAGで回答するレシピヘルパーを作成しています。"
            "今からあなたには、ユーザから与えられたテキストを見てどのツールを実行するべきかを判断するタスクを行ってもらいます。\n"
            "与えられたツールを利用するべきではない、もしくは必要な引数を適切に渡すことができないと判断した場合は、ツール無理に利用するのではなく一般的な回答を返答してください。\n"
            "\n"
            "利用できるツールは以下の4つです。\n"
            "- `register`: ストアにレシピの情報を格納します。引数は不要です\n"
            "- `answer`: ストアからレシピの情報を内部で検索して、レシピに関する質問に回答する。引数には`ユーザの質問(question)`が必要です\n"
            "- `list`: ストアに格納されているレシピの一覧を表示します。引数は不要です\n"
            "- `delete`: ストアに格納されているレシピの情報を削除します。引数には`レシピ名(recipe_name)`が必要です\n"
            "\n"
            "それでは、以下にユーザから与えられたテキストを示します。"
        ),
        tool_config={
            "toolChoice": {
                "auto": {},
            },
            "tools": [
                {
                    "toolSpec": {
                        "name": "register",
                        "description": "ストアにレシピの情報を格納します",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {},
                            }
                        },
                    },
                },
                {
                    "toolSpec": {
                        "name": "answer",
                        "description": "ストアからレシピの情報を内部で検索して、レシピに関する質問に回答します",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "とあるレシピに関するユーザからの質問(ユーザから与えられたテキストそのままでも構いません)",
                                    },
                                },
                                "required": ["question"],
                            },
                        },
                    },
                },
                {
                    "toolSpec": {
                        "name": "list",
                        "description": "ストアに格納されているレシピの一覧を表示します",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {},
                            }
                        },
                    },
                },
                {
                    "toolSpec": {
                        "name": "delete",
                        "description": "ストアに格納されているレシピの情報を削除します",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "recipe_name": {
                                        "type": "string",
                                        "description": "削除したいレシピの名前",
                                    },
                                },
                                "required": ["recipe_name"],
                            },
                        },
                    }
                },
            ],
        },
    )

    if response["stopReason"] == "tool_use":
        for content in response["output"]["message"]["content"]:
            if "toolUse" in content:
                tool_name = content["toolUse"]["name"]
                tool_args = content["toolUse"]["input"]
    else:
        tool_name = "none"
        tool_args = {}

    return tool_name, tool_args


def _handle_regist_action(
    order: str,
    index: IndexFlatIP,
    recipes: List[Dict],
    bucket_name: str,
) -> str:
    response = converse(
        message=order,
        system_message=(
            "あなたはとても優秀なアシスタントです。\n"
            "\n"
            "今からあなたにレシピに関連する文章を与えるので、そこからレシピの名前や材料・手順を抽出し、ツールの引数として提供してもらいます。\n"
            "与えられた文章からレシピの情報を抽出することが困難な場合は、無理にツールの引数を埋めたりせずに、何が足りないかという理由を返答してください。\n"
            "\n"
            "それでは、以下にレシピに関連する文章を示します。"
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
            "あら?レシピに関する情報がうまく取得できなかったみたいですわ...\n"
            "わたくしへの命令に以下の情報が含まれているか確認してくださるかしら?\n"
            "```\n"
            "- レシピの名前\n"
            "- レシピの材料(数量なども含みますわ!!)\n"
            "- レシピの手順\n"
            "```"
        )


def _handle_ask_action(
    question: str,
    index: IndexFlatIP,
    recipes: List[Dict],
) -> str:
    if recipes:
        query_vector = np.array([embed(question)], dtype="float32")
        _, indices = index.search(query_vector, k=5)  # type: ignore

        valid_indices = [index for index in indices[0] if index != -1]
        relevant_recipes = [recipes[index] for index in valid_indices]

        recipes_info = "\n".join(
            (f"## レシピ名\n{recipe['name']}\n\n## レシピの手順\n{recipe['context']}\n")
            for recipe in relevant_recipes
        )

        return ask_lady(
            message=(
                f"今から質問に関係するレシピの名前とレシピの手順を見せるから、これらを参考に質問に答えて!!\n"
                f"もし、質問と全然関係ないレシピだったら「別の聞き方でもう一回聞いてほしい」っていう感じで返して!!\n"
                f"\n"
                f"{recipes_info}\n"
                f"\n"
                f"## 質問\n"
                f"{question}"
            )
        )
    else:
        return (
            "あら?わたくしまだ何もレシピを覚えていませんわ...\n"
            "わたくしに新しくレシピを覚えるよう命じてくださるかしら?"
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
            "あら?わたくしまだ何もレシピを覚えていませんわ...\n"
            "わたくしに新しくレシピを覚えるよう命じてくださるかしら?"
        )


def _handle_delete_action(
    recipe_name: str,
    index: IndexFlatIP,
    recipes: List[Dict],
    bucket_name: str,
) -> str:
    if recipes:
        delete_id = next(
            (
                index
                for index, recipe in enumerate(recipes)
                if recipe["name"] == recipe_name
            ),
            None,
        )

        if delete_id is None:
            return (
                f"わたくしの記憶に「{recipe_name}」という名前のレシピが見当たりませんわ...\n"
                f"レシピの名前を確認して、もう一度聞いていただけるかしら?"
            )

        recipe_name = recipes[delete_id]["name"]

        index = delete(index, delete_id)
        write_index(index, f"/tmp/{RECIPES_FAISS_FILE_NAME}")

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
            "あら?わたくしまだ何もレシピを覚えていませんわ...\n"
            "わたくしに新しくレシピを覚えるよう命じてくださるかしら?"
        )
