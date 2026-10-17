from typing import Any, Dict, Optional


STAR_LABELS = {
    "alp": "α",
    "bet": "β",
    "gam": "γ",
    "del": "δ",
    "eps": "ε",
    "zet": "ζ",
    "eta": "η",
    "the": "θ",
    "iot": "ι",
    "kap": "κ",
    "lam": "λ",
    "mu": "μ",
    "nu": "ν",
    "xi": "ξ",
    "omi": "ο",
    "pi": "π",
    "rho": "ρ",
    "sig": "σ/ς",
    "tau": "τ",
    "ups": "υ",
    "phi": "φ",
    "chi": "χ",
    "psi": "ψ",
    "ome": "ω",
}

STAR_LABEL_KIND_NAME = 0
STAR_LABEL_KIND_BAYER = 1
STAR_LABEL_KIND_FLAMSTEED = 2


def resolve_star_label_metadata(
    bsc_star_or_string: Any,
    show_flamsteed: bool,
    flamsteed_numbers_only: bool,
) -> Optional[Dict[str, Any]]:
    if bsc_star_or_string is None:
        return None

    if isinstance(bsc_star_or_string, str):
        label = bsc_star_or_string.strip()
        if not label:
            return None
        return {
            "text": label,
            "full_text": label,
            "kind": STAR_LABEL_KIND_NAME,
            "constellation": "",
            "picker_suffix": label,
        }

    greek = getattr(bsc_star_or_string, "greek", "") or ""
    greek_no = getattr(bsc_star_or_string, "greek_no", "") or ""
    constellation = (getattr(bsc_star_or_string, "constellation", "") or "").strip()

    if greek:
        greek_text = STAR_LABELS.get(greek)
        if greek_text:
            label = greek_text + greek_no
            full_text = label + (" " + constellation.capitalize() if constellation else "")
            picker_suffix = full_text
            return {
                "text": label,
                "full_text": full_text,
                "kind": STAR_LABEL_KIND_BAYER,
                "constellation": constellation,
                "picker_suffix": picker_suffix,
            }

    if show_flamsteed:
        flamsteed = (getattr(bsc_star_or_string, "flamsteed", "") or "").strip()
        if flamsteed:
            label = flamsteed.split()[0] if flamsteed_numbers_only else flamsteed
            return {
                "text": label,
                "full_text": flamsteed,
                "kind": STAR_LABEL_KIND_FLAMSTEED,
                "constellation": constellation,
                "picker_suffix": flamsteed,
            }

    hd = getattr(bsc_star_or_string, "HD", None)
    if hd is not None:
        return {
            "text": "",
            "full_text": "HD" + str(hd),
            "kind": STAR_LABEL_KIND_NAME,
            "constellation": constellation,
            "picker_suffix": "HD" + str(hd),
        }

    return None
