"""
The stock universe and our starting hypothesis.

THE THESIS (state it BEFORE looking at data -- this is what makes it research
and not data-mining):

    When global shipping / freight costs spike, retailers that import most of
    their goods (cheap products sourced from Asia) eat higher landed costs they
    can't fully pass on to shoppers. Their margins get squeezed. The market is
    slow to reprice this lag. So: SHORT the high-import names, LONG the
    low-import (domestic / services-heavy) names, and hold a market-neutral
    long-short basket.

Each ticker gets an "import_exposure" score from 0.0 (domestic/services, barely
touched by freight) to 1.0 (heavy importer, very exposed). These are hand-set
starting estimates based on business model -- exactly the kind of judgement your
supply-chain background lets you defend in an interview. Refine them later.
"""

# ticker: (import_exposure_score, one-line why)
UNIVERSE = {
    # --- HIGH import exposure (short candidates when freight spikes) ---
    "FIVE": (0.95, "Five Below - cheap discretionary goods, heavily China-sourced"),
    "DLTR": (0.90, "Dollar Tree - low-cost imported goods, thin margins"),
    "BBY":  (0.85, "Best Buy - imported consumer electronics"),
    "WSM":  (0.80, "Williams-Sonoma - imported home furnishings"),
    "RH":   (0.80, "RH - imported furniture, long shipping lead times"),
    "ETSY": (0.70, "Etsy - marketplace with heavy cross-border shipping"),
    "NKE":  (0.75, "Nike - Asia-manufactured footwear/apparel"),
    "TGT":  (0.70, "Target - broad imported general merchandise"),

    # --- MID exposure (neutral-ish) ---
    "WMT":  (0.55, "Walmart - imports a lot but huge pricing power / scale"),
    "COST": (0.45, "Costco - membership model cushions margin"),

    # --- LOW import exposure (long candidates -- domestic / services) ---
    "TJX":  (0.35, "TJX - off-price, opportunistic domestic sourcing"),
    "ORLY": (0.20, "O'Reilly - auto parts, largely domestic distribution"),
    "AZO":  (0.20, "AutoZone - domestic auto-parts retail"),
    "ULTA": (0.30, "Ulta - beauty, mix of services + domestic brands"),
    "CMG":  (0.10, "Chipotle - restaurant, domestic food supply, no import goods"),
    "SBUX": (0.15, "Starbucks - services/food, freight-light on merchandise"),
    "COTY": (0.30, "Coty - cosmetics, mixed sourcing"),
    "KR":   (0.15, "Kroger - grocery, mostly domestic/perishable"),
}

BENCHMARK = "SPY"  # what we compare our long-short strategy against

# How far back to pull data
START_DATE = "2015-01-01"
END_DATE = None  # None = up to today
