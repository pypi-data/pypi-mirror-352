# 雰囲気画像提示ツール [mood-img]
# 【動作確認 / 使用例】

import sys
import fies
import ezpip
from tqdm import tqdm
mood_img = ezpip.load_develop("mood_img", "../", develop_flag = True)

# 画像ディレクトリの設定 (インストール後1回のみの実行でOK) [mood-img]
mood_img.set_imgdir("C:/develop/data/mood_img/grouped_imgs")

for i, text in enumerate(tqdm(fies["input_sample.yml"])):
	# queryに合った画像を選定 [mood-img]
	img_path = mood_img.get(text)
	# 画像のコピー・設置
	ext = img_path.split(".")[-1]
	fies[f"./output/{i}_{text}.{ext}", "b"] = fies[img_path, "b"]
