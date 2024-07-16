import pickle

import numpy as np
from faiss import IndexFlatIP, write_index

from lady_claude.common.aws.bedrock import embed
from lady_claude.common.aws.s3 import upload
from lady_claude.common.aws.ssm import get_parameter

# NOTE: Titan Text Embeddings v2のデフォルト次元数を採用
DEFAULT_INDEX_DIMENSIONS = 1024

RECIPES_FAISS_FILE_NAME = "index.faiss"
RECIPES_PICKLE_FILE_NAME = "recipes.pkl"

if __name__ == "__main__":
    recipes = [
        {
            "name": "レモネード",
            "procedure": """
                今回は漬け込みせずにすぐに飲める、レモネードをご紹介します。
                皮ごと煮込むので、できれば国産・無農薬のレモンを使用することをおすすめします。
                自家製ならではの苦味もいいところ。
                ソーダやお酒などで割ってお楽しみください。


                【材料】

                レモン lemon 4個（約300g）
                グラニュー糖 sugar 240g（レモンに対して8割）
                水 water 300g（レモンと同量）
                ソーダ

                【下準備】
                ・レモンはしっかり洗っておく

                【作り方】
                ①レモンの上下を切り落とし、3mm幅にスライスする。

                ②重さを計りながら鍋に並べ、グラニュー糖、水を加える。

                ③まず一度しっかり沸騰させ、その後弱火に落とし20分煮ていく。アクが出てきたら取り除く。

                ④20分経ったら火を止め、煮沸などをした密閉容器に移す。粗熱を取って冷蔵庫で保存する。
                ソーダや水、お酒などお好みのもので割ってお楽しみください。

                ※冷蔵庫で2週間程度保存可能です。
            """,
        },
        {
            "name": "ジンジャーエール",
            "procedure": """
                ▼材料
                ショウガ3片(約200g)
                レモン 1つ
                お砂糖 200g
                蜂蜜 大さじ1
                お水400ml
                スパイスはお好みで♩
                ex)シナモン、クローブ、ローレル、鷹の爪
                炭酸水
                氷

                ▼作り方
                ① ジンジャーとレモンを切って、お鍋に入れる
                ② お砂糖、蜂蜜、お水、各種スパイスを、お鍋に入れる
                ③ 沸騰するまで強火で熱し、灰汁を取る
                ④ 弱火にして10分ほど熱したら、瓶に移して完成!!
            """,
        },
        {
            "name": "ずんだもち",
            "procedure": """
                # 材料 （6個）
                ■ 餡
                枝豆(冷凍)
                さやつきで130g
                砂糖
                大さじ2
                塩
                1つまみ
                牛乳
                大さじ1
                ■ 餅
                白玉粉
                50g
                ぬるま湯
                45ml

                # 作り方
                1. 枝豆は茹でた後、水で冷やして、さやと薄皮を取り除きます。
                2. すり鉢ですり潰します。細かい方がなめらかで美味しいです。
                3. 砂糖と塩と牛乳を加えて混ぜたら、餡の完成です。
                4. 餅は袋に記載の作り方で作ってください。今回は白玉粉50g、ぬるま湯45mlでつくりました。茹でたら水で冷やします。
                5. 餡に加えます。
                6. 混ぜます。
                7. 完成！冷やしてお召し上がりください！
            """,
        },
    ]

    index = IndexFlatIP(DEFAULT_INDEX_DIMENSIONS)
    vectors = np.array(
        [embed(recipe["procedure"]) for recipe in recipes],
        dtype="float32",
    )
    index.add(vectors)  # type: ignore

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
