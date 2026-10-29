#!/usr/bin/env python3
import json
import re

DATA_PATH = "/Users/manishshaw/Downloads/stitch_cip_number_marketplace/data/numbers.json"
INDEX_PATH = "/Users/manishshaw/Downloads/stitch_cip_number_marketplace/index.html"
VIP_CLUB_PATH = "/Users/manishshaw/Downloads/stitch_cip_number_marketplace/vip-number-club.html"

with open(DATA_PATH) as f:
    records = json.load(f)

def format_num(n):
    return f"{n[:5]} {n[5:]}"

def format_time(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

cards_html_list = []
for r in records:
    num = r["number"]
    disp = format_num(num)
    price = r["price"]
    orig_price = r.get("originalPrice", int(price * 1.5))
    cat = r["category"]
    tag = r["tag"]
    tags = " ".join(r.get("tags", []))
    sec = r.get("seconds", 7200)
    timer_str = format_time(sec)
    
    # short badge label
    badge = "VIP NUMBER"
    if "70101" in num:
        badge = "70101 VIP" if "Mixed" not in cat else "70101 MIXED"
    elif "786" in num:
        badge = "786 VIP"
    elif "9 Series" in cat:
        badge = "9 SERIES"
    elif "8 Series" in cat:
        badge = "8 SERIES"
    elif "7 Series" in cat:
        badge = "7 SERIES"
    elif "6 Series" in cat:
        badge = "6 SERIES"
    elif "Penta" in cat:
        badge = "PENTA VIP"
    elif "Mirror" in cat:
        badge = "MIRROR VIP"

    card = f"""      <!-- Card {num} -->
      <article class="number-card bg-brand-gold text-black rounded-xl p-2.5 sm:p-3 md:p-3.5 flex flex-col justify-between shadow-sm card-touch-press border border-amber-400/40" data-number="{num}" data-price="{price}" data-original-price="{orig_price}" data-tag="{tag}" data-category="{cat}" data-tags="{tags}">
        <div>
          <div class="flex items-center justify-between text-[8px] font-bold pb-1.5 border-b border-black/10">
            <span class="tracking-tight flex items-center gap-0.5 uppercase truncate max-w-[95px] sm:max-w-[120px]" title="{cat}">
              <span>▾</span> {badge}
            </span>
            <span class="bg-black text-brand-gold px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase shrink-0 cursor-pointer hover:bg-neutral-800 transition-colors" onclick="handleBuyNow('{disp}', '{price}', '{orig_price}', '{cat}')">Book Now</span>
          </div>
          <div class="py-2.5 text-center flex flex-col items-center justify-center">
            <h4 class="vip-number-display tracking-tight text-neutral-950 font-mono">
              {disp}
            </h4>
            <div class="my-1.5 flex items-center justify-center">
              <div class="countdown-badge inline-flex items-center gap-1 bg-black/10 px-2 py-0.5 rounded-full border border-black/10" data-seconds="{sec}">
                <svg class="w-2.5 h-2.5 text-black shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                <span class="countdown-timer text-[9px] font-black text-neutral-950 tracking-tight font-mono">{timer_str}</span>
              </div>
            </div>
            <div class="mt-0.5 flex items-center justify-center gap-1.5">
              <span class="text-[10px] sm:text-[11px] text-neutral-700/80 line-through font-medium">₹{orig_price:,}</span>
              <span class="font-extrabold text-xs sm:text-sm text-neutral-950">₹{price:,}</span>
            </div>
          </div>
        </div>
        <div>
          <div class="bg-black/10 rounded-md py-0.5 px-1 mb-1.5 flex items-center justify-center gap-1 text-[8px] font-bold text-neutral-900 border border-black/10">
            <span class="text-[10px]">⏰</span> LIMITED TIME OFFER
          </div>
          <div class="grid grid-cols-2 gap-1 text-[9px] font-bold">
            <button class="bg-transparent border border-black text-black py-1 rounded hover:bg-black/10 transition-colors" onclick="handleEnquire('{disp}', '{price}')">Enquire →</button>
            <button class="bg-black text-brand-gold py-1 rounded hover:bg-neutral-900 transition-colors" onclick="handleBuyNow('{disp}', '{price}', '{orig_price}', '{cat}')">Buy Now</button>
          </div>
        </div>
      </article>"""
    cards_html_list.append(card)

generated_cards_block = "\n\n".join(cards_html_list)

chips_replacement = """    <!-- Category Horizontal Filter Scroll -->
    <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1" id="categoryChips">
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap bg-brand-gold text-black transition-colors" data-cat="all">
        All
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="70101-repeating">
        70101 Repeating
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="70101-mixed">
        70101 Mixed
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="9-series">
        9 Series
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="8-series">
        8 Series
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="7-series">
        7 Series
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="6-series">
        6 Series
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="penta">
        Penta Series
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="mirror">
        Mirror Numbers
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="786">
        786 Numbers
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="0000">
        0000 Ending
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="triple9">
        Triple 9
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="hexa">
        Hexa Numbers
      </button>
      <button class="category-chip px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap bg-neutral-900 border border-neutral-800 text-neutral-300 hover:border-brand-gold transition-colors" data-cat="vip">
        VIP Numbers
      </button>
    </div>"""

custom_styles = """
    /* Big and bold VIP phone number styling */
    .vip-number-display {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
      font-weight: 800 !important;
      font-size: 20px;
      line-height: 1.15;
      color: #000000 !important;
      letter-spacing: -0.035em;
      white-space: nowrap;
      display: block;
    }

    @media (min-width: 380px) and (max-width: 639px) {
      .vip-number-display {
        font-size: 21px;
        letter-spacing: -0.03em;
      }
    }

    @media (min-width: 640px) and (max-width: 1023px) {
      .vip-number-display {
        font-size: 23px;
        letter-spacing: -0.025em;
      }
    }

    @media (min-width: 1024px) {
      .vip-number-display {
        font-size: 25px;
        letter-spacing: -0.02em;
      }
    }
"""

js_filter_function = """    function filterCards(category, query) {
      let visibleCount = 0;
      const q = query ? query.toLowerCase().replace(/\\s+/g, '') : '';
      cards.forEach(card => {
        const num = card.getAttribute('data-number') || '';
        const tag = card.getAttribute('data-tag') || '';
        const cat = card.getAttribute('data-category') || '';
        const tags = (card.getAttribute('data-tags') || '').split(' ');

        let matchesCategory = false;
        if (category === 'all') {
          matchesCategory = true;
        } else if (tags.includes(category) || tag === category) {
          matchesCategory = true;
        } else if (category === '786' && num.includes('786')) {
          matchesCategory = true;
        } else if (category === 'triple9' && num.includes('999')) {
          matchesCategory = true;
        } else if (category === '0000' && num.includes('0000')) {
          matchesCategory = true;
        } else if (category === 'hexa' && (tag === 'hexa' || tags.includes('hexa'))) {
          matchesCategory = true;
        } else if (category === 'mirror' && (cat.toLowerCase().includes('mirror') || tags.includes('mirror'))) {
          matchesCategory = true;
        } else if (category === 'penta' && (cat.toLowerCase().includes('penta') || tags.includes('penta'))) {
          matchesCategory = true;
        } else if (category === 'vip' && (cat.toLowerCase().includes('vip') || tags.includes('vip'))) {
          matchesCategory = true;
        }

        const matchesSearch = !q || num.includes(q) || cat.toLowerCase().includes(q) || (card.dataset.price && card.dataset.price.includes(q));

        if (matchesCategory && matchesSearch) {
          card.classList.remove('hidden');
          visibleCount++;
        } else {
          card.classList.add('hidden');
        }
      });
      numberCount.innerHTML = `<strong class="text-neutral-200">${visibleCount}</strong> available numbers`;
    }"""

buy_now_js_function = """    function handleBuyNow(number, price, origPrice, category) {
      const cleanNum = String(number).replace(/\\s+/g, '');
      let cleanPrice = price ? String(price).replace(/[^\\d]/g, '') : '';
      let cleanOrig = origPrice ? String(origPrice).replace(/[^\\d]/g, '') : '';
      let cat = category || '';

      // Fallback: look up card in DOM if any field is missing
      const card = document.querySelector(`.number-card[data-number="${cleanNum}"]`);
      if (card) {
        if (!cleanPrice) cleanPrice = card.getAttribute('data-price') || '';
        if (!cleanOrig) cleanOrig = card.getAttribute('data-original-price') || '';
        if (!cat) cat = card.getAttribute('data-category') || '';
      }

      if (!cleanPrice) cleanPrice = '12250';
      if (!cleanOrig) cleanOrig = String(Math.round(Number(cleanPrice) * 1.5));
      if (!cat) cat = 'VIP Mobile Number';

      // Save to sessionStorage for state persistence across sessions/navigation
      try {
        sessionStorage.setItem('vipCheckoutData', JSON.stringify({
          number: cleanNum,
          displayNumber: number,
          price: Number(cleanPrice),
          originalPrice: Number(cleanOrig),
          category: cat
        }));
      } catch (e) {}

      // Navigate to checkout page with URL query parameters
      const params = new URLSearchParams({
        number: cleanNum,
        price: cleanPrice,
        orig: cleanOrig,
        cat: cat
      });

      window.location.href = `checkout.html?${params.toString()}`;
    }"""

def update_file(filepath):
    with open(filepath) as f:
        content = f.read()

    # 1. Update style if not present
    if ".vip-number-display" not in content:
        content = content.replace("</style>\n</head>", f"{custom_styles}\n  </style>\n</head>")

    # 2. Update category chips
    chips_pattern = r"<!-- Category Horizontal Filter Scroll -->\s*<div[^>]*id=\"categoryChips\"[^>]*>.*?</div>"
    content = re.sub(chips_pattern, chips_replacement.strip(), content, flags=re.DOTALL)

    # 3. Update inventory count
    count_pattern = r"<span id=\"numberCount\"><strong[^>]*>\d+</strong> available numbers</span>"
    new_count = f"<span id=\"numberCount\"><strong class=\"text-neutral-200\">{len(records)}</strong> available numbers</span>"
    content = re.sub(count_pattern, new_count, content)

    # 4. Update vipCardsContainer cards
    container_pattern = r"(<div class=\"grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2.5 md:gap-4\" id=\"vipCardsContainer\">).*?(</div>\s*</div>\s*</section>\s*<!-- END: VIP Numbers Grid -->)"
    content = re.sub(container_pattern, lambda m: f"{m.group(1)}\n{generated_cards_block}\n    {m.group(2)}", content, flags=re.DOTALL)

    # 5. Update filterCards function in JS
    old_filter_pattern = r"function filterCards\(category, query\) \{.*?\n    \}"
    content = re.sub(old_filter_pattern, lambda m: js_filter_function.strip(), content, flags=re.DOTALL)

    # 6. Update handleBuyNow function to navigate to checkout
    old_buynow_pattern = r"function handleBuyNow\(number, price\) \{.*?\n    \}"
    content = re.sub(old_buynow_pattern, lambda m: buy_now_js_function.strip(), content, flags=re.DOTALL)

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Successfully updated {filepath} with {len(records)} cards.")

update_file(INDEX_PATH)
update_file(VIP_CLUB_PATH)
