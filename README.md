<h1 align="center">🎀 Lady Claude 🎀</h1>

<div align="center">
  <img src="https://img.shields.io/badge/-Discord-7289DA.svg?logo=discord&style=plastic">
  <img src="https://img.shields.io/badge/Python-3.10.6-3776AB.svg?logo=python&style=plastic">
  <img src="https://img.shields.io/badge/uv-0.5.24-D7FF64.svg?logo=astral&style=plastic">
  <img src="https://img.shields.io/badge/-Amazon%20Web%20Service-232F3E.svg?logo=amazon&style=plastic">
  <img src="https://img.shields.io/badge/AWS%20SAM-1.113.0-232F3E.svg?logo=amazon&style=plastic">
</div>

<br>

<div align="center">
  <blockquote>
  ごきげんよう!!<br>
  そうですわ!!素敵な日差しの中、お庭でお茶でもいかがかしら?
  </blockquote>
</div>

## 🌟 Overview

**Lady Claude**(Claudeお嬢様)は、AWS上で動作するサーバレスのDiscord Botです。

DiscordのWebhookで受け取ったSlash commandsのコマンドごとに、Amazon SNSで処理を行うLambdaを振り分けます。

また、Discord Botとしてのメッセージの生成にAmazon Bedrockの**Claude**を使用しており、さながらお嬢様のように回答してくれます。

<div align="center">
  <img width="560px" src="./images/overall-architecture.png" />
</div>

## 💡 Usage

対象となるサーバにClaudeお嬢様を追加し、Slash commandsを呼び出すことで使用することができます。

また、定期的にClaudeお嬢様からDiscordへ通知などのアクションを行うサービスも存在し、デプロイの段階で有効化やスケジューリングを設定することが可能です。

現在は、以下のslash commandsおよび定期実行サービスを利用することができます。

#### 🤔 [`ask`](https://github.com/tosuri13/lady-claude/blob/main/documents/ask-architecture.md)

- Claudeお嬢様に何でも質問してみましょう!!

#### ⛏️ [`minecraft`](https://github.com/tosuri13/lady-claude/blob/main/documents/minecraft-architecture.md)

- Claudeお嬢様と一緒にMinecraft Serverで遊びましょう!!

#### 🍰 [`recipe`](https://github.com/tosuri13/lady-claude/blob/main/documents/recipe-architecture.md)

- Claudeお嬢様に料理のレシピを聞いてみましょう!!

#### ~~📢 [`connpass`](https://github.com/tosuri13/lady-claude/blob/main/documents/connpass-architecture.md)~~

- ~~Claudeお嬢様に最新のイベントを教えてもらいましょう!!~~

#### 🗑️ [`garbage`](https://github.com/tosuri13/lady-claude/blob/main/documents/garbage-architecture.md)

- Claudeお嬢様にゴミ出しのリマインドをしてもらいましょう!!

## 🚧 Develop

### 依存関係のインストール

Pythonのパッケージ管理に**uv**を使用しています。

```
$ uv install
```

### ツールの実行

Discord Botへのコマンド登録などは、`tools`以下のツールを利用して行います。

```
$ uv run tools/xxx.py
```

### アプリケーションのビルドとAWSへのデプロイ

uvのタスクランナーとして**taskipy**を使用しており、AWSへのデプロイツールとして**AWS SAM**を使用しています。

```
$ task build & task deploy
```
