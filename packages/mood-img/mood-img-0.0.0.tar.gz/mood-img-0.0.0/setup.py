
from setuptools import setup
# 公開用パッケージの作成 [ezpip]
import ezpip

# 公開用パッケージの作成 [ezpip]
with ezpip.packager(develop_dir = "./_develop_mood_img/") as p:
	setup(
		name = "mood-img",
		version = "0.0.0",
		description = "A tool for presenting images that match the description.",
		author = "bib_inf",
		author_email = "contact.bibinf@gmail.com",
		url = "https://github.co.jp/",
		packages = p.packages,
		install_requires = ["ezpip", "fies>=1.5.0", "LLM00", "tqdm", "indent_template>=0.0.2", "relpath>=3.0.5"],
		long_description = p.long_description,
		long_description_content_type = "text/markdown",
		license = "CC0 v1.0",
		classifiers = [
			"Programming Language :: Python :: 3",
			"Topic :: Software Development :: Libraries",
			"License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication"
		],
		# entry_points = """
		# 	[console_scripts]
		# 	py6 = py6:console_command
		# """
		entry_points = {
			'console_scripts': [
				'mood_img = mood_img:cmd_func',
			],
		}
	)
