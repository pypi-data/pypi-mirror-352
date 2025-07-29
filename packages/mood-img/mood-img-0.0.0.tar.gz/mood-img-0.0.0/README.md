English description follows Japanese.

以下に、`mood_img` ライブラリの**日本語版**および**英語版**のドキュメントを記述します。
内容は概要、特徴、使い方、注意点、CLI対応などを含んでいます。

---

## 概要

`mood_img` は、与えられた説明文にもっともマッチする画像を提示する Python ライブラリです。
プレゼン資料、スライド、動画などで適切な画像を探したいときに役立ちます。

## 特徴

* **説明文から画像検索**：
  例：「毎朝朝食を急いで食べます」→ 朝食の写真を取得
* **ローカル画像から選定**：
  ユーザー自身が指定した画像ディレクトリ内から選ばれます
* **重複回避機能**：
  同じスクリプト実行中は、同じ画像が繰り返し選ばれにくくなっています
* **コマンドライン対応**：
  Python スクリプトなしでも画像取得が可能です

## 使い方

### 1. 初期設定

画像ファイルが入っているディレクトリを指定します。これは最初に一度だけ必要です。

```python
import mood_img

mood_img.set_imgdir("path/to/imgs")
```

### 2. 画像を取得する

任意の説明文に対応する画像のパスが返されます。

```python
print(mood_img.get("私がタヌキで"))	# 例: ./imgs/tanuki01.png
print(mood_img.get("こちらがキツネです。"))	# 例: ./imgs/fox_surprised.jpg
```

### 3. コマンドラインから使用

```sh
mood_img "私がタヌキで" "こちらがキツネです。"
```

カレントディレクトリに `0.png`, `1.jpg` のような形式で画像が保存されます。

## 注意点

* **画像ディレクトリの準備が必要**：
  このライブラリはインターネット検索を行わないため、利用者自身が画像ファイルを用意する必要があります。
* **画像の重複は完全には防げない**：
  可能な限り回避されますが、候補画像が足りない場合は重複することがあります。

---

## Overview

`mood_img` is a Python library that helps you find the most fitting image based on a given description.
It is especially useful when creating slides, presentations, or videos and you want an image that matches a specific mood or sentence.

## Features

* **Text-to-image matching**:
  Example: `"I rush through breakfast every morning"` → Image of a breakfast
* **Uses local image directory**:
  Images are selected from a directory specified by the user
* **Avoids duplicate selections**:
  Within a single script run, it tries not to return the same image multiple times
* **Command-line usage available**:
  Can be used without writing any Python code

## Usage

### 1. Initial Setup

You must first specify the image directory containing your image files.

```python
import mood_img

mood_img.set_imgdir("path/to/imgs")
```

### 2. Retrieve images

Pass a description, and the path to the most relevant image will be returned.

```python
print(mood_img.get("I am a tanuki"))	# Example: ./imgs/tanuki01.png
print(mood_img.get("This one is a fox."))	# Example: ./imgs/fox_surprised.jpg
```

### 3. Command-line usage

```sh
mood_img "I am a tanuki" "This one is a fox."
```

This will generate `0.png`, `1.jpg`, etc., in the current working directory.

## Notes

* **You must prepare image files**:
  This tool does not fetch images from the internet. You need to provide a local image dataset.
* **Duplicate images may still appear**:
  While it tries to avoid showing the same image more than once, duplicates can occur if there are not enough available options.
