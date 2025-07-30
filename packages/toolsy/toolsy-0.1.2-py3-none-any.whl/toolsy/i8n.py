from typing import Dict


class I18N:
    def __init__(self, translations: Dict[str, Dict[str, str]] = None):
        """
        初始化国际化实例

        :param translations: 翻译字典，格式为 {'lang': {'key': 'translation'}}
        """
        self._language = 'en'  # 默认语言
        self._translations = translations or {'en': {}, 'zh': {}}

    @property
    def language(self) -> str:
        """获取当前语言"""
        return self._language

    @language.setter
    def language(self, lang: str):
        """设置当前语言"""
        if lang in self._translations:
            self._language = lang

    def t(self, key: str, **variables) -> str:
        """
        获取翻译文本

        :param key: 翻译键
        :param variables: 替换变量
        :return: 翻译后的文本
        """
        # 获取当前语言文本，如果不存在则尝试英文
        text = self._translations.get(self._language, {}).get(key, self._translations['en'].get(key, key))

        # 替换变量（兼容format语法）
        try:
            return text.format(**variables)
        except (KeyError, ValueError):
            return text
