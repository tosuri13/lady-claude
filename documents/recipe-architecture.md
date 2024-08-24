<h1 align="center">🎀 Lady Claude - recipe 🎀</h1>

<div align="center">
  <blockquote>
  まあ、ジンジャーエールのレシピについてお尋ねですの？<br>
  材料はショウガ、レモン、お砂糖、蜂蜜が主役ですわ。そして、シナモンやクローブ、ローレル、鷹の爪といったスパイスも加えて、より深みのある味わいに仕上げますの！
  </blockquote>
</div>

## 🌟 Overview

**recipe**コマンドでは、Claudeお嬢様にお気に入りのレシピを教えることによって、セマンティックなレシピの検索とレシピに関する質問に対する回答を提供します。

いわゆるRAGとしてサーバレスに動作しており、ベクトル検索には**FAISS**を使用し、インデックスと実データのペアをS3に保管しています。また、レシピのベクトル化には**Titan Text Embedding V2**、レシピに関する質問への回答には**Claude 3.5 Sonnet**を使用しています。

Claudeお嬢様に覚えさせたレシピを一覧表示する機能や間違って覚えさせたレシピを削除する機能なども搭載されています。

<div align="center">
  <img width="440px" src="../images/recipe-architecture.png" />
</div>

## 💡 Usage

このサービスは定期的に実行されるため、特にユーザからアクションを行う必要はありません。

## 🧱 Additional Infrastructure

以下の形式でDiscordのSlash commandを入力してください。

```
/recipe {action} {order}
```

- `action`: Claudeお嬢様に行ってもらいたいアクション

  - `regist`: レシピを覚えてもらう

  - `ask`: 覚えているレシピを検索して質問に回答する

  - `list`: 覚えているレシピの一覧を表示する

  - `delete`: レシピを忘れてもらう

- `order`: Claudeお嬢様に対する命令

### モデルアクセスの有効化

LLMによる回答を生成するために、Amazon BedrockのコンソールからClaude 3.5 Sonnetのモデルアクセスを有効化する必要があります。

> [!WARNING]
> 2024年6月現在、Claude 3.5 Sonnetはバージニア北部リージョンでしか利用できないため、モデルアクセス有効化の際には注意してください。
