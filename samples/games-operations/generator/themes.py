"""Naming themes for the synthetic Games operations sample.

The data model is identical in every theme; only display text changes.
- ``ioc``     : IOC workshop wording (Olympic Winter Games, National Olympic Committee).
- ``neutral`` : customer-neutral wording for the public kit (multi-sport winter games).
"""

DISCLAIMER = (
    "Synthetic content generated for demonstration purposes. "
    "Names, figures, people and findings are fictional and are not official data."
)

THEMES = {
    "ioc": {
        "games_name": "Olympic Winter Games Valmont (synthetic)",
        "games_short": "Valmont Winter Games",
        "organiser": "Valmont Organising Committee (synthetic)",
        "noc_label": "National Olympic Committee",
        "noc_short": "NOC",
        "authority": "IOC Games Operations (synthetic)",
    },
    "neutral": {
        "games_name": "Valmont Winter Games (synthetic multi-sport event)",
        "games_short": "Valmont Winter Games",
        "organiser": "Valmont Organising Committee (synthetic)",
        "noc_label": "National Committee",
        "noc_short": "NC",
        "authority": "Games Operations Authority (synthetic)",
    },
}


def get_theme(name: str) -> dict:
    if name not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Choose one of: {', '.join(THEMES)}")
    return THEMES[name]
