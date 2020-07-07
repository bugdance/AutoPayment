# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""The simulator is use for verify some process."""
from PIL import Image
from pytesseract import pytesseract


class CorpSLSimulator:
	"""SL模拟器，模拟js生成cookie验证。"""
	
	def __init__(self):
		self.logger: any = None  # 日志记录器。
	
	def convert_to_image(self, image_path: str = "", threshold: float = 180) -> Image.Image:
		"""转换灰度图片
		:param image_path:  图片地址
		:param threshold:  临界值
		:return:  Image
		"""
		image = Image.open(image_path)
		image = image.convert('L')
		# # 自定义灰度界限，大于这个值为黑色，小于这个值为白色
		pixels = image.load()
		for x in range(image.width):
			for y in range(image.height):
				if pixels[x, y] > threshold:
					pixels[x, y] = 255
				else:
					pixels[x, y] = 0
		self.logger.info("转换灰度图片成功(*^__^*)【Image】")
		return image
	
	def reduce_to_noise(self, image: Image.Image = None, loop_count: int = 1, max_count: int = 0) -> Image.Image:
		"""八临域算法降噪
		:param image:  图片
		:param loop_count:  循环次数
		:param max_count:  循环最大次数
		:return:  Image
		"""
		pix_data = image.load()
		w, h = image.size
		for y in range(1, h - 1):
			for x in range(1, w - 1):
				count = 0
				if pix_data[x, y - 1] > 245:  # 上
					count += 1
				if pix_data[x, y + 1] > 245:  # 下
					count += 1
				if pix_data[x - 1, y] > 245:  # 左
					count += 1
				if pix_data[x + 1, y] > 245:  # 右
					count += 1
				if pix_data[x - 1, y - 1] > 245:  # 左上
					count += 1
				if pix_data[x - 1, y + 1] > 245:  # 左下
					count += 1
				if pix_data[x + 1, y - 1] > 245:  # 右上
					count += 1
				if pix_data[x + 1, y + 1] > 245:  # 右下
					count += 1
				if count > 4:
					pix_data[x, y] = 255
		if loop_count >= max_count:
			return image
		else:
			return self.reduce_to_noise(image, loop_count + 1, max_count)
	
	def recognize_to_captcha(self, image_path: str = "", source_data: bytes = b"") -> str:
		"""识别验证码
		:param image_path:  图片地址
		:param source_data:  图片流
		:return: str
		"""
		try:
			with open(image_path, "wb") as f:  # 保存打码图片
				f.write(source_data)
			gray_image = self.convert_to_image(image_path)
			final_image = self.reduce_to_noise(gray_image, max_count=1)
			code_string = pytesseract.image_to_string(final_image)
		except Exception as ex:
			self.logger.info(f"识别验证图片失败(*>﹏<*)【{image_path}】")
			self.logger.info(f"返回页面失败原因(*>﹏<*)【{ex}】")
			return ""
		else:
			self.logger.info(f"识别验证图片成功(*^__^*)【{code_string}】")
			return code_string
