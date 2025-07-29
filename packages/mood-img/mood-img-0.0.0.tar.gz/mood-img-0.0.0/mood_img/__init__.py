# 雰囲気画像提示ツール [mood-img]

import os
import sys
import fies
import LLM00
import random
from tqdm import tqdm
from sout import sout
import indent_template
from relpath import rel2abs
# プロンプト [prompt.py]
from .parts import prompt

# 重複回避のための履歴
history = []

# 画像ディレクトリの設定 (インストール後1回のみの実行でOK) [mood-img]
def set_imgdir(path):
	abspath = os.path.abspath(path)
	fies[rel2abs("./settings.yml")] = {"imgdir": abspath}

# 画像ディレクトリの取得 [mood-img]
def get_imgdir():
	err = Exception("[mood-img error] `imgdir` is not set. Please run `mood_img.set_imgdir(path)` first.")
	setting_path = rel2abs("./settings.yml")
	if setting_path not in fies: raise err
	settings = fies[setting_path]
	if "imgdir" not in settings: raise err
	return settings["imgdir"]

# 最近の画像との重複を回避
def avoid_recent(
	img_ls,	# 回避前の画像リスト
	min_n	# 回避後の最低確保枚数
):
	ret_ls = list(img_ls)	# シャローコピー
	# 歴史を逆順に確認
	for target in history[::-1]:
		# 最低確保枚数の確認
		if len(ret_ls) <= min_n: break
		# 履歴と一致してしまっている画像を除外
		ret_ls = [e for e in ret_ls if e != target]
	return ret_ls

# AIに聞いてgroup_idxの特定
def get_idx(filled_prompt, group_n):
	for _ in range(5):	# 再試行ループ
		raw_res = LLM00(filled_prompt)
		for i in range(group_n):
			if f"<{i}>" in raw_res: return i
	raise Exception("[mood_img error] AIの返答の形式が不正です。")

# AIによる適した分類の選定
def ai_grouping(query, groups):
	random.shuffle(groups)
	groups_str = "\n".join([
		f"<{i}> {e}" for i, e
		in enumerate(groups)
	])
	filled_prompt = indent_template.replace(
		prompt.group_selector,	# グループ選定プロンプト [prompt.py]
		{"[[query]]": query, "[[ジャンル数]]": len(groups), "[[ジャンル一覧]]": groups_str}
	)
	g_idx = get_idx(filled_prompt, len(groups))	# AIに聞いてgroup_idxの特定
	return groups[g_idx]

# queryに合った画像を選定 [mood-img]
def get(query):
	# 画像ディレクトリの取得 [mood-img]
	img_dir = get_imgdir()
	# まずジャンル分け
	groups = list(fies[img_dir])
	group_name = ai_grouping(query, groups)	# AIによる適した分類の選定
	# 画像の選定
	img_ls = list(fies[img_dir][group_name])
	img_ls = avoid_recent(img_ls, 10)	# 最近の画像との重複を回避
	img_name = ai_grouping(query, img_ls)	# AIによる適した分類の選定
	# 履歴蓄積
	history.append(img_name)
	return os.path.join(img_dir, group_name, img_name)

# queryに合った画像を選定 [mood-img]
def cmd_func():
	for i, text in enumerate(tqdm(sys.argv[1:])):
		img_path = get(text)
		ext = img_path.split(".")[-1]
		fies[f"./{i}.{ext}", "bin"] = fies[img_path, "bin"]	# 設置
