#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import gettext
import os
from pathlib import Path
from typing import Optional, Callable


def get_translator(lang: Optional[str] = None) -> Callable[[str], str]:
    """
    Return a gettext-like function '_' for the requested language.
    Uses fallback=True so it never crashes if translations are missing.
    """
    lang = (lang or os.environ.get("fchart3lang") or "").strip() or None
    localedir = Path(__file__).resolve().parent / "locale"

    trans = gettext.translation(
        "messages",
        localedir=str(localedir),
        languages=[lang] if lang else None,
        fallback=True,
    )
    return trans.gettext


def install_translator(lang: Optional[str] = None):
    """
    Install '_' into builtins for convenience across modules.
    """
    _ = get_translator(lang)
    gettext.install("messages")  # optional, but not enough alone for custom localedir
    # Better: actually install the translation object
    lang = (lang or os.environ.get("fchart3lang") or "").strip() or None
    localedir = Path(__file__).resolve().parent / "locale"
    trans = gettext.translation("messages", localedir=str(localedir),
                                languages=[lang] if lang else None,
                                fallback=True)
    trans.install()
    return trans.gettext