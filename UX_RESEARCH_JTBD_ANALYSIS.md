# UX Research: JTBD Analysis for NexSupply "Analyze / Step 1 – Describe" Input Page

## 1. Brief JTBD Recap

**When I'm evaluating a new product idea or comparing suppliers...**
- I want to quickly understand if the numbers work (will I make money at my target retail price?)
- So I can decide whether to request samples, negotiate with suppliers, or move on to the next product idea.

**When I've already found a supplier and have a quote...**
- I want to know the true total cost (not just FOB price) including shipping, duties, Amazon fees, and all hidden costs
- So I can set the right retail price and understand my actual profit margin before I commit to inventory.

**When I'm comparing multiple product options or suppliers...**
- I want a fast way to compare scenarios (different quantities, shipping methods, or sales channels)
- So I can optimize my sourcing decisions and maximize profitability.

---

## 2. UI Element Interpretation & Risk Analysis

| UI Element / Label | How a Typical User Might Interpret It | Risk or Confusion |
|-------------------|--------------------------------------|-------------------|
| **"What do you want to ship?"** | "What product am I selling?" - Clear enough, but might feel too casual for B2B context. | Low risk - straightforward, but could be slightly more professional ("Product description" or "Shipment details"). |
| **"Once this one sentence is filled in, Step 1 is complete."** | "Great, I only need to type something here and I can move on." - Reassuring! | Low risk - this is actually well-done and reduces anxiety. |
| **"See your profit potential – Free analysis"** | "This will show me if I can make money." - Clear value prop. | Low risk - "profit potential" is user language. |
| **"Fine-tune assumptions (optional)"** | "These are guesses or estimates I'm making" - "Assumptions" might sound uncertain or unprofessional. | **Medium risk** - "assumptions" has a negative connotation. Users might think "why would I want to input assumptions?" Better: "Adjust details (optional)" or "Refine your estimate (optional)". |
| **"Where are you shipping to?"** | "What country is my customer in?" or "Where is the final destination?" | Low risk - clear for most users. |
| **"Roughly how many units?"** | "How many do I plan to order?" - "Roughly" implies it doesn't need to be exact, which is good. | Low risk - the word "roughly" reduces pressure. |
| **"Target selling price"** | "What price will I sell this at?" - Clear for sellers. | **Medium risk** - new importers might not have a target price yet. Could add: "If you don't know, we'll estimate a retail price range." |
| **"Where will you sell this?"** | "Amazon? Shopify? My own store?" - Clear. | Low risk - straightforward. |
| **"Advanced inputs – for power users"** | "I'm not a power user, so I should skip this" or "Do I need this to get accurate results?" | **Medium risk** - "power users" can intimidate first-time users. Better: "Additional details (optional)" or "For more precise estimates (optional)". |
| **"Add Amazon fulfillment costs"** | "Should I include FBA fees?" - Clear for Amazon sellers. | Low risk - Amazon sellers know what this means. |
| **"Target shipping month (optional)"** | "When do I plan to ship?" - Clear intent. | Low risk - but could add context: "We adjust freight rates and lead times based on season (peak season is more expensive)." |
| **"Then we'll calculate: All-in landed cost per unit"** | "What's 'landed cost'? Is that different from FOB?" | **High risk** - "landed cost" is industry jargon. New importers might not know this term. Better: "Total cost per unit (product + shipping + duties + fees)" or add a tooltip explaining "landed cost = everything you pay to get it to your warehouse". |
| **"HS code (if you know it)"** | "What's an HS code? Do I need this?" | **Medium risk** - "if you know it" is good, but no explanation of what it is. Could add: "HS code = product classification code used for customs. We'll estimate it if you don't know." |
| **Example chips** | "Can I use these exact examples?" - Examples are specific (gummy candy, yoga mats). | **Medium risk** - Very specific product examples might make users think "this tool is only for food/toys/accessories". Could add more diverse examples or clarify: "These are examples – works for any product category." |

---

## 3. Five Concrete Copy Changes

### Change 1: Replace "Fine-tune assumptions" with "Adjust details (optional)"
**Current:** "Fine-tune assumptions (optional)"  
**Proposed:** "Adjust details (optional)"  
**Rationale:** "Assumptions" sounds uncertain and unprofessional. "Details" is neutral and suggests refinement rather than guessing.

---

### Change 2: Clarify "landed cost" in outcome preview
**Current:** "All-in landed cost per unit (product, freight, duties and fees)."  
**Proposed:** "Total cost per unit — everything you pay to get it to your warehouse (product price, shipping, customs duties, and all fees)."  
**Rationale:** Many first-time importers don't know the term "landed cost." Plain language reduces cognitive load.

---

### Change 3: Add reassurance for "Target selling price" when empty
**Current:** "Target selling price" with helper "Optional – we use this to calculate net margin %. You can refine it after you see results."  
**Proposed:** Add above the input: "What price will you sell this at? (If you don't know yet, leave blank and we'll suggest a price range based on your cost.)"  
**Rationale:** New importers often don't have a target price yet. Explicit permission to skip reduces friction.

---

### Change 4: Replace "Advanced inputs – for power users" with "Additional details (optional)"
**Current:** "Advanced inputs – for power users (optional)"  
**Proposed:** "Additional details (optional)"  
**Rationale:** "Power users" creates unnecessary hierarchy and can intimidate first-time users. "Additional details" is neutral and clearly optional.

---

### Change 5: Expand example chip diversity or add clarification
**Current:** Three examples: "5,000 gummy candy units to US Amazon FBA", "1,000 yoga mats to US FBA", "500 phone cases by air to the US"  
**Proposed:** Either:
- Add 1-2 more diverse examples (electronics, home goods, or B2B wholesale)
- Or add text above examples: "Examples (works for any product category):"

**Rationale:** Current examples skew toward consumer goods. B2B sellers or electronics importers might not relate. Clarifying that it works for "any product" expands perceived applicability.

---

## Additional Observations

**What's Working Well:**
- "Once this one sentence is filled in, Step 1 is complete" is excellent reassurance
- "Roughly how many units?" - the word "roughly" reduces pressure
- "Skip this for now if you're in a hurry" language is user-friendly
- Step 1 → Step 2 → Step 3 progression is clear

**Potential Confusion Points:**
- "Planning estimates only" at top might make some users think results are unreliable
- Multiple "optional" sections might make users second-guess: "Should I fill these out anyway?"
- No mention of how results will be presented (charts? tables? downloadable?)

**Language Tone:**
- Overall tone is professional but friendly — good for B2B context
- Could benefit from slightly more direct, action-oriented language that matches how sourcing managers speak ("What's my margin?" vs "Calculate net margin %")

