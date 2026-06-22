import streamlit as st
import json
import os
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Swiss Beauty AI",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Dark theme base ── */
.stApp { background: #0e0e0e; }

/* Force all default Streamlit text to light */
.stApp, .stApp p, .stApp li, .stApp span, .stApp label,
.stMarkdown, .stMarkdown p { color: #e8e8e8 !important; }

/* Sidebar & main block */
[data-testid="stSidebar"] { background: #141414; }
.block-container { background: #0e0e0e; }

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #1e1e1e !important;
    color: #f0f0f0 !important;
    border: 1.5px solid #333 !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #666 !important; }
[data-testid="stChatInput"] { background: #0e0e0e !important; }

/* Buttons (suggestion chips + follow-up) */
.stButton > button {
    background: #1e1e1e !important;
    color: #e8e8e8 !important;
    border: 1.5px solid #2e2e2e !important;
    border-radius: 24px !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    border-color: #ff2d7a !important;
    color: #ff2d7a !important;
    background: #1e0d15 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}

/* Horizontal rule */
hr { border-color: #2a2a2a !important; }

/* Header banner */
.sb-header {
    background: linear-gradient(135deg, #8b0030 0%, #c0392b 50%, #8b4513 100%);
    border-radius: 0 0 24px 24px;
    padding: 28px 40px 24px;
    margin-bottom: 8px;
    text-align: center;
    border-bottom: 1px solid #ff2d7a33;
}
.sb-header h1 {
    color: #fff;
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 6px;
    letter-spacing: -0.5px;
}
.sb-header p {
    color: rgba(255,255,255,0.75);
    font-size: 15px;
    margin: 0;
}

/* Product card */
.product-card {
    background: #181818;
    border: 1.5px solid #2a2a2a;
    border-radius: 16px;
    padding: 20px;
    height: 100%;
    box-shadow: 0 2px 16px rgba(0,0,0,0.4);
    transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s;
}
.product-card:hover {
    box-shadow: 0 6px 28px rgba(255,45,122,0.18);
    border-color: #ff2d7a55;
    transform: translateY(-2px);
}
.product-emoji { font-size: 36px; margin-bottom: 10px; }
.product-category {
    font-size: 11px;
    font-weight: 600;
    color: #ff2d7a;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}
.product-name {
    font-size: 15px;
    font-weight: 700;
    color: #f0f0f0;
    margin-bottom: 6px;
    line-height: 1.3;
}
.product-price {
    font-size: 22px;
    font-weight: 800;
    color: #ff2d7a;
    margin-bottom: 10px;
}
.product-desc {
    font-size: 12.5px;
    color: #aaa;
    line-height: 1.55;
    margin-bottom: 12px;
}
.shades-label {
    font-size: 10.5px;
    font-weight: 700;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 5px;
}
.shades-row { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.shade-pill {
    background: #250d17;
    color: #ff2d7a;
    border: 1px solid #4a1a30;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
}
.why-box {
    background: #200d16;
    border-left: 3px solid #ff2d7a;
    border-radius: 0 8px 8px 0;
    padding: 10px 12px;
}
.why-label {
    font-size: 10px;
    font-weight: 700;
    color: #ff2d7a;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 3px;
}
.why-text { font-size: 12.5px; color: #bbb; line-height: 1.5; }

/* Kit summary box */
.kit-box {
    background: #181018;
    border: 1.5px solid #4a1a30;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.kit-name { font-size: 18px; font-weight: 700; color: #f0f0f0; margin-bottom: 4px; }
.kit-desc { font-size: 13px; color: #888; margin-bottom: 12px; }
.kit-total-label { font-size: 12px; font-weight: 600; color: #ff2d7a; text-transform: uppercase; letter-spacing: 0.5px; }
.kit-total-amount { font-size: 32px; font-weight: 800; color: #ff2d7a; }
.kit-savings {
    display: inline-block;
    background: #0d2b14;
    color: #4ade80;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 4px;
}

/* Comparison table */
.comp-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 12px;
    overflow: hidden;
    font-size: 13.5px;
    margin: 12px 0;
    box-shadow: 0 2px 16px rgba(0,0,0,0.4);
}
.comp-table thead tr th {
    background: linear-gradient(135deg, #8b0030, #6b21a8);
    color: white;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
}
.comp-table thead tr th:first-child { min-width: 140px; }
.comp-table tbody tr td {
    padding: 11px 16px;
    border-bottom: 1px solid #2a2a2a;
    color: #ccc;
    vertical-align: top;
    background: #181818;
}
.comp-table tbody tr:nth-child(even) td { background: #141414; }
.comp-table tbody tr:last-child td { border-bottom: none; }
.aspect-label { font-weight: 600; color: #888; }

/* Follow-up question chips */
.followup-section { margin-top: 14px; }
.followup-label { font-size: 12px; font-weight: 600; color: #666; margin-bottom: 8px; }

/* Section headings inside AI response */
.response-section-title {
    font-size: 13px;
    font-weight: 700;
    color: #ff2d7a;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin: 14px 0 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Shopify → our schema ───────────────────────────────────────────────────────

CATEGORY_EMOJI = {
    "lipstick": "💄", "lip gloss": "✨", "lip liner": "✏️", "lip": "💄",
    "foundation": "🏺", "concealer": "🎭", "bb cream": "🧴", "cc cream": "🧴",
    "eyeshadow": "👁️", "eyeliner": "✒️", "kajal": "✏️", "mascara": "👁️",
    "eyebrow": "✏️", "eye": "👁️",
    "blush": "🌸", "bronzer": "☀️", "highlighter": "✨", "contour": "🎨",
    "primer": "🧴", "setting spray": "💨", "setting powder": "🌬️",
    "powder": "💠", "compact": "💠",
    "face": "✨", "skin": "🧴",
}

SKIN_TYPE_KEYWORDS = {"oily", "dry", "combination", "normal", "sensitive", "all"}
FINISH_KEYWORDS = {"matte", "glossy", "satin", "dewy", "shimmer", "glitter", "natural", "luminous"}

def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:200]  # keep compact — 422 products, watch token count

def _get_emoji(product_type: str, title: str) -> str:
    combined = (product_type + " " + title).lower()
    for keyword, emoji in CATEGORY_EMOJI.items():
        if keyword in combined:
            return emoji
    return "✨"

def _extract_shades(shopify_product: dict) -> list:
    # Shopify stores shades as variant options — option name contains "color"/"shade"
    for option in shopify_product.get("options", []):
        name = option["name"].lower()
        if "color" in name or "colour" in name or "shade" in name or name == "finish":
            vals = option.get("values", [])
            return [v for v in vals if v.lower() not in ("default title", "default")]
    # Fallback: variant titles
    titles = [v["title"] for v in shopify_product.get("variants", [])
              if v.get("title", "").lower() not in ("default title", "default")]
    return titles[:12]

def _extract_from_tags(tags_str: str):
    tags = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
    skin_type = [t for t in tags if t in SKIN_TYPE_KEYWORDS] or ["all"]
    finish = next((t.title() for t in tags if t in FINISH_KEYWORDS), None)
    return tags, skin_type, finish

def _min_price(shopify_product: dict) -> float:
    prices = []
    for v in shopify_product.get("variants", []):
        try:
            prices.append(float(v["price"]))
        except (KeyError, ValueError):
            pass
    return min(prices) if prices else 0.0

def map_shopify_product(sp: dict) -> dict:
    tags_str = sp.get("tags", "")
    tags, skin_type, finish_from_tags = _extract_from_tags(tags_str)
    product_type = sp.get("product_type", "Beauty").strip() or "Beauty"
    price = _min_price(sp)
    shades = _extract_shades(sp)

    return {
        "id": f"shopify-{sp['id']}",
        "name": sp.get("title", ""),
        "category": product_type,
        "subcategory": product_type,
        "price": int(price),
        "description": _strip_html(sp.get("body_html", "")),
        "shades": shades,
        "skin_type": skin_type,
        "finish": finish_from_tags,
        "coverage": None,
        "wear_time": None,
        "tags": tags,
        "ideal_for": [],
        "emoji": _get_emoji(product_type, sp.get("title", "")),
        "shopify_handle": sp.get("handle", ""),
    }


def fetch_shopify_products(shop_url: str, token: str) -> list:
    """Paginate through all Shopify products and return mapped list."""
    shop_url = shop_url.rstrip("/")
    base = f"https://{shop_url}/admin/api/2024-01/products.json"
    headers = {"X-Shopify-Access-Token": token}
    products = []
    params = {"limit": 250, "status": "active", "fields":
              "id,title,body_html,product_type,tags,variants,options,handle"}
    page = 1

    while True:
        resp = requests.get(base, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            st.warning(f"Shopify API error {resp.status_code}: {resp.text[:200]}")
            break
        data = resp.json().get("products", [])
        if not data:
            break
        products.extend(data)
        # Shopify uses Link header for cursor-based pagination
        link = resp.headers.get("Link", "")
        if 'rel="next"' not in link:
            break
        # Extract the page_info cursor from the Link header
        next_url = re.search(r'<([^>]+)>;\s*rel="next"', link)
        if not next_url:
            break
        import urllib.parse as urlparse
        qs = urlparse.parse_qs(urlparse.urlparse(next_url.group(1)).query)
        params = {"limit": 250, "page_info": qs.get("page_info", [""])[0]}
        page += 1

    return [map_shopify_product(p) for p in products if p.get("title")]


# ── Load Products (Shopify-first, JSON fallback) ───────────────────────────────
@st.cache_data(ttl=3600)  # refresh from Shopify every hour
def load_products():
    shop_url = os.getenv("SHOPIFY_SHOP_URL", "").strip()
    token = os.getenv("SHOPIFY_ACCESS_TOKEN", "").strip()

    if shop_url and token:
        with st.spinner("Loading your live product catalog from Shopify…"):
            products = fetch_shopify_products(shop_url, token)
        if products:
            return products, "shopify"

    # Fallback to local products.json
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)["products"], "json"

_products, _source = load_products()
ALL_PRODUCTS = _products
PRODUCTS_BY_ID = {p["id"]: p for p in ALL_PRODUCTS}

if _source == "shopify":
    st.sidebar.success(f"✓ Live catalog: {len(ALL_PRODUCTS)} products from Shopify")
else:
    st.sidebar.info(f"📦 Local catalog: {len(ALL_PRODUCTS)} products (products.json)")


def build_catalog_text(products: list) -> str:
    # Compact single-line format — keeps token count manageable for 400+ products
    lines = ["=== SWISS BEAUTY PRODUCT CATALOG (use exact IDs) ==="]
    for p in products:
        shades = ", ".join(p.get("shades", [])[:6])
        skin = ", ".join(p.get("skin_type", [])) or "all"
        tags = ", ".join(p.get("tags", [])[:6])
        desc = (p.get("description") or "")[:120].replace("\n", " ")
        lines.append(
            f"ID:{p['id']} | {p['name']} | {p['category']} | ₹{p['price']}"
            f" | {desc}"
            + (f" | shades: {shades}" if shades else "")
            + f" | skin: {skin}"
            + (f" | tags: {tags}" if tags else "")
        )
    return "\n".join(lines)


CATALOG_TEXT = build_catalog_text(ALL_PRODUCTS)

SYSTEM_PROMPT = f"""You are Swiss Beauty's AI Shopping Assistant — a warm, expert beauty advisor helping Indian customers discover the perfect makeup products.

{CATALOG_TEXT}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ONLY recommend products whose ID appears in the catalog above. Never hallucinate product names.
2. For budget queries: sum of ALL recommended product prices must be ≤ budget.
3. Use exact product IDs (e.g. "sb-lip-001") — no typos.
4. If the user's question lacks key info (skin type, budget, coverage preference), ask via follow_up_questions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT — always return valid JSON, exactly this schema:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{
  "response_type": "recommendation" | "kit" | "comparison" | "followup" | "general",
  "conversational_text": "Warm, helpful opening. Markdown ok. Max 3 sentences.",
  "product_recommendations": [
    {{
      "product_id": "sb-lip-001",
      "why_recommended": "Specific reason this fits the user's need"
    }}
  ],
  "kit": {{
    "name": "Bridal Glow Kit",
    "description": "A complete bridal makeup kit under ₹2000",
    "total_cost": 1897,
    "products": ["sb-lip-004", "sb-found-002", "sb-setting-001"]
  }},
  "comparison": {{
    "products": ["sb-lip-001", "sb-lip-004"],
    "aspects": ["Price", "Finish", "Wear Time", "Coverage", "Best For", "Skin Type"]
  }},
  "follow_up_questions": ["What is your skin type?", "What is your budget?", "Do you prefer matte or glossy?"],
  "sections": [
    {{"heading": "Pro Tip", "content": "Apply with a lip brush for extra precision."}}
  ]
}}

Rules for fields:
- "product_recommendations": always include IDs even for kit/comparison types
- For "kit": also populate product_recommendations with the same kit products
- For "comparison": populate product_recommendations with the products being compared
- For "followup": product_recommendations = [], sections = []
- Unused fields → null or []

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STYLE & EXPERTISE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Oily skin → matte finish, oil-control, primer + setting spray combo
• Dry skin → hydrating/satin/dewy finish, illuminating primer
• Beginners → BB cream, kajal, gloss — easy and forgiving products
• Bridal → transfer-proof liquid matte lip, setting spray, full-coverage foundation
• Natural look → BB cream, blush, gloss, mascara, eyebrow pencil
• Be specific: mention price, finish, wear time, and the one key benefit that matches the user's ask
• Proactively mention complementary products (e.g. suggest lip liner with lipstick)
• Keep conversational_text concise — the cards do the heavy lifting
"""

# ── OpenAI Client ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found. Create a .env file with your key.")
        st.stop()
    return OpenAI(api_key=api_key)

client = get_openai_client()


def call_llm(history: list) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "response_type": "general",
            "conversational_text": raw,
            "product_recommendations": [],
            "kit": None,
            "comparison": None,
            "follow_up_questions": [],
            "sections": [],
        }


# ── Render Helpers ─────────────────────────────────────────────────────────────

def render_product_card(product: dict, why: str = "") -> str:
    shades = product.get("shades", [])[:6]
    shade_pills = "".join(f'<span class="shade-pill">{s}</span>' for s in shades)
    why_html = (
        f'<div class="why-box"><div class="why-label">✦ Why this?</div>'
        f'<div class="why-text">{why}</div></div>'
        if why else ""
    )
    return f"""
<div class="product-card">
  <div class="product-emoji">{product.get('emoji', '💄')}</div>
  <div class="product-category">{product['category']}</div>
  <div class="product-name">{product['name']}</div>
  <div class="product-price">₹{product['price']}</div>
  <div class="product-desc">{product['description']}</div>
  {"" if not shades else f'<div class="shades-label">Available Shades</div><div class="shades-row">{shade_pills}</div>'}
  {why_html}
</div>
"""


def render_comparison_table(comparison: dict) -> str:
    product_ids = comparison.get("products", [])
    aspects = comparison.get("aspects", ["Price", "Finish", "Wear Time", "Coverage", "Best For"])
    products = [PRODUCTS_BY_ID[pid] for pid in product_ids if pid in PRODUCTS_BY_ID]

    if not products:
        return ""

    header_cells = "".join(f"<th>{p['name']}</th>" for p in products)
    header = f"<tr><th>Feature</th>{header_cells}</tr>"

    def get_value(p: dict, aspect: str) -> str:
        aspect_lower = aspect.lower()
        if "price" in aspect_lower:
            return f"₹{p['price']}"
        if "finish" in aspect_lower:
            return p.get("finish") or "—"
        if "wear" in aspect_lower or "time" in aspect_lower:
            return p.get("wear_time") or "—"
        if "coverage" in aspect_lower:
            return p.get("coverage") or "—"
        if "skin" in aspect_lower:
            return ", ".join(p.get("skin_type", [])) or "All"
        if "best" in aspect_lower or "ideal" in aspect_lower:
            return ", ".join(p.get("ideal_for", [])[:2]) or "—"
        if "category" in aspect_lower:
            return p.get("category", "—")
        return "—"

    body_rows = ""
    for asp in aspects:
        cells = "".join(f"<td>{get_value(p, asp)}</td>" for p in products)
        body_rows += f"<tr><td class='aspect-label'>{asp}</td>{cells}</tr>"

    return f"""
<table class="comp-table">
  <thead>{header}</thead>
  <tbody>{body_rows}</tbody>
</table>
"""


def render_kit_box(kit: dict) -> str:
    return f"""
<div class="kit-box">
  <div class="kit-name">🎁 {kit['name']}</div>
  <div class="kit-desc">{kit.get('description', '')}</div>
  <div class="kit-total-label">Kit Total</div>
  <div class="kit-total-amount">₹{kit['total_cost']}</div>
</div>
"""


def render_ai_response(parsed: dict, msg_idx: int = 0):
    text = parsed.get("conversational_text", "")
    if text:
        st.markdown(text)

    sections = parsed.get("sections") or []
    for sec in sections:
        if sec.get("heading"):
            st.markdown(
                f'<div class="response-section-title">{sec["heading"]}</div>',
                unsafe_allow_html=True,
            )
        if sec.get("content"):
            st.markdown(sec["content"])

    rtype = parsed.get("response_type", "general")

    # Kit summary banner
    kit = parsed.get("kit")
    if rtype == "kit" and kit:
        st.markdown(render_kit_box(kit), unsafe_allow_html=True)

    # Product cards grid
    recs = parsed.get("product_recommendations") or []
    valid_recs = [(r, PRODUCTS_BY_ID[r["product_id"]]) for r in recs if r.get("product_id") in PRODUCTS_BY_ID]

    if valid_recs:
        cols_per_row = min(3, len(valid_recs))
        for row_start in range(0, len(valid_recs), cols_per_row):
            row = valid_recs[row_start : row_start + cols_per_row]
            cols = st.columns(len(row))
            for col, (rec, product) in zip(cols, row):
                with col:
                    st.markdown(
                        render_product_card(product, rec.get("why_recommended", "")),
                        unsafe_allow_html=True,
                    )

    # Comparison table
    comparison = parsed.get("comparison")
    if rtype == "comparison" and comparison:
        st.markdown("**Side-by-side comparison:**")
        st.markdown(render_comparison_table(comparison), unsafe_allow_html=True)

    # Follow-up questions
    follow_ups = parsed.get("follow_up_questions") or []
    if follow_ups:
        st.markdown('<div class="followup-label">To help me recommend better, could you tell me:</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(follow_ups), 3))
        for i, q in enumerate(follow_ups):
            with cols[i % len(cols)]:
                if st.button(q, key=f"followup_{msg_idx}_{i}_{hash(q)}"):
                    st.session_state.pending_input = q
                    st.rerun()


# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []       # [{role, content, parsed}]
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sb-header">
  <h1>💄 Swiss Beauty AI</h1>
  <p>Your personal beauty advisor — discover the perfect look for you</p>
</div>
""", unsafe_allow_html=True)


# ── Suggestion chips (only on empty chat) ─────────────────────────────────────
SUGGESTIONS = [
    "Recommend a lipstick under ₹400",
    "Build a bridal kit under ₹2000",
    "Suggest products for oily skin",
    "Compare matte and liquid matte lipsticks",
    "Recommend a beginner makeup kit",
    "What foundation suits dry skin?",
]

if not st.session_state.messages:
    st.markdown("#### Try asking:")
    cols = st.columns(3)
    for i, s in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(s, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_input = s
                st.rerun()
    st.markdown("---")


# ── Chat History ───────────────────────────────────────────────────────────────
for msg_idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="💄"):
            parsed = msg.get("parsed")
            if parsed:
                render_ai_response(parsed, msg_idx=msg_idx)
            else:
                st.markdown(msg["content"])


# ── Input Handling ─────────────────────────────────────────────────────────────
def handle_input(user_text: str):
    user_text = user_text.strip()
    if not user_text:
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Build history for LLM (role + content only)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Call LLM
    with st.spinner("Finding the perfect products for you…"):
        parsed = call_llm(history)

    # Compose a plain-text content for history continuity
    plain_content = parsed.get("conversational_text", "")
    if parsed.get("product_recommendations"):
        names = [
            PRODUCTS_BY_ID[r["product_id"]]["name"]
            for r in parsed["product_recommendations"]
            if r.get("product_id") in PRODUCTS_BY_ID
        ]
        plain_content += "\n\nRecommended: " + ", ".join(names)

    st.session_state.messages.append({
        "role": "assistant",
        "content": plain_content,
        "parsed": parsed,
    })


# Handle follow-up chip click
if st.session_state.pending_input:
    inp = st.session_state.pending_input
    st.session_state.pending_input = None
    handle_input(inp)
    st.rerun()

# Native Streamlit chat input (sticks to bottom)
user_input = st.chat_input("Ask about products, kits, routines, or comparisons…")
if user_input:
    handle_input(user_input)
    st.rerun()
