from big_thing_py.utils.common_util import get_project_root

import gettext
import os

_translation_cache = {}


def translate(text: str, language: str = 'ko') -> str:
    global _translation_cache

    locales_dir = os.path.join(get_project_root(), 'locales')
    cache_key = f"{language}_device_category"

    if cache_key not in _translation_cache:
        translation = gettext.translation('device_category', locales_dir, languages=[language])
        _translation_cache[cache_key] = translation

    translation: gettext = _translation_cache[cache_key]
    return translation.gettext(text)
