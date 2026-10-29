"""Build DRAFTS-BATCH4.md from the 20 verified targets.

Every address below was published by the company itself (own contact page,
own footer, or own PDF) and every domain passed an MX lookup on 30 October
2026. No address here was guessed from an email-format pattern.

Run: python3 gen_batch4.py
"""

TARGETS = [
    ("unloop", "hello@unloop.com", "cost history"),
    ("fusioncpa", "info@fusiontaxes.com", "in transit"),
    ("theecommerceaccountants", "info@theecommerceaccountants.com", "cost per unit"),
    ("irvine", "support@irvinebookkeeping.com", "AP with no PO"),
    ("encore", "info@encore3pl.com", "expected inbounds"),
    ("shipcalm", "help@shipcalm.com", "onboarding blind"),
    ("shiphype", "support@shiphype.com", "48 hour receiving"),
    ("ledgergurus", "contact@ledgergurus.com", "agencies and platforms"),
    ("outserve", "info@outserve.co.uk", "the gap you sell into"),
    ("upcounting", "hello@upcounting.com", "a wall at 300 SKUs"),
    ("ecommerceaccountingllc", "admin@ecommerceaccountingllc.com", "three spreadsheets"),
    ("bookkeeper360", "info@bookkeeper360.com", "the re-order promise"),
    ("aissolutions", "info@aissolutions.ca", "clean COGS"),
    ("redstag", "info@redstagfulfillment.com", "dock to stock"),
    ("phasev", "info@phasev.com", "a wrong inbound notice"),
    ("shipfusion", "hello@shipfusion.com", "what the brand declares"),
    ("sbo", "info@sbo.financial", "stock on the balance sheet"),
    ("3plusallc", "admin@3plusallc.com", "a pallet with no PO"),
    ("speedcommerce", "info@speedcommerce.com", "paperwork that never arrives"),
    ("kellypartners", "info@kellypartners.com.au", "a stock problem wearing a tax problem"),
]

BODIES = {
"unloop": """Your site says Unloop is the only accounting firm serving inventory businesses in the US and Canada. Cost history is the one input you cannot produce for a client right now. Stocky held it, stopped on 31 August, and suppliers never had an export in the first place.

Who is rebuilding that history for your Shopify clients?""",
"fusioncpa": """Your ecommerce page lists what needs tracking: stock at Amazon, in transit from suppliers, at 3PLs, returns. In transit is the hard one, because it needs a purchase order to point at, and those left with Stocky on 31 August.

Where does that number come from for your clients now?""",
"theecommerceaccountants": """Clean books for a Shopify brand start one level below the ledger, at a cost per unit. Most of the brands you would take on kept that number in Stocky, which stopped on 31 August, and it never lived in Shopify's own inventory tools.

How are your clients costing inventory now?""",
"irvine": """You offer accounts payable to ecommerce clients. Without a purchase order, approving a supplier invoice is a payment, not a control, and the purchase order history behind it left Stocky on 31 August.

Do your Shopify clients still have that history anywhere?""",
"encore": """Your site describes receiving well. UPC scan at inbound, then a check against expected inbounds. That check is only as good as what the brand declares, and since 31 August a lot of brands have been declaring guesses.

What do you do when the inbound notice does not match the pallet?""",
"shipcalm": """Onboarding a Shopify brand means asking for SKU counts and expected inbounds. For brands that ran Stocky, the purchase history behind those numbers stopped on 31 August and never moved into Shopify.

How do you set receiving expectations when the brand cannot produce the history?""",
"shiphype": """You publish a 48 hour receiving SLA. That promise depends on clean inbound data arriving with the pallet, and the purchase order history that used to supply it left Stocky on 31 August.

How often does an inbound turn up with no record behind it?""",
"ledgergurus": """Your contact page invites agencies and software platforms in the ecommerce ecosystem, so this is aimed there. Stocky held cost and purchase order history for Shopify brands, stopped on 31 August, and suppliers were never exportable.

Who rebuilds that history when one of your partners cannot produce it?""",
"outserve": """You sit on Unleashed, Xero and Shopify at once, so you meet the gap between stock and the ledger before your clients do. Since 31 August that gap has no purchase order history behind it, only invoices to guess from.

Which client is that biting first?""",
"upcounting": """DTC brands hit a wall past a few hundred SKUs, and it is usually a cost per unit nobody can substantiate. Most kept that number in Stocky, which stopped on 31 August, and it never lived in Shopify's own tools.

What are you using to rebuild it for new clients?""",
"ecommerceaccountingllc": """You work only with online sellers, so you have met the client whose purchase order history is three spreadsheets and a Shopify export. Since 31 August there is no system of record left for it at all.

How are you rebuilding supplier lead times now?""",
"bookkeeper360": """Your ecommerce page promises a streamlined re-order process. A re-order point needs lead time per supplier, and since 31 August the purchase order history that supplied it has no home in Shopify.

What is standing in for it on your clients' side?""",
"aissolutions": """Cloud bookkeeping for Canadian ecommerce means clean sales tax and clean COGS. COGS needs landed cost per unit, and the purchase order history behind it left Stocky on 31 August, taking supplier lead times with it.

Is that history still available for your Shopify clients?""",
"redstag": """You guarantee receiving and publish a two business day dock to stock. Both depend on the brand knowing what it shipped, and since 31 August most brands have been guessing at inbound.

How often does a pallet arrive with no paperwork behind it?""",
"phasev": """Thirty five years of receiving means you have seen what a missing purchase order does to a dock schedule. Shopify brands lost theirs when Stocky stopped on 31 August, and nothing native replaced it.

What happens on your dock when the inbound notice is wrong?""",
"shipfusion": """Your receiving team verifies incoming inventory against what the brand says it shipped. Since 31 August, what the brand says has been less reliable, because the purchase order history behind it left Stocky.

Who rebuilds that record when a client cannot produce it?""",
"sbo": """Stock is usually the largest line on an ecommerce balance sheet and the hardest to cost. For most brands the purchase order history behind landed cost sat in Stocky or a spreadsheet, and never in Shopify.

What do you use when a new client cannot produce it?""",
"3plusallc": """You run Shopify fulfilment on Dynamics 365, so inventory accuracy is the whole promise. Half of accuracy is receiving against a purchase order, and Shopify brands lost that history when Stocky stopped on 31 August.

How does your dock reconcile a pallet with no purchase order?""",
"speedcommerce": """Speed Commerce publishes a receiving process across a US network. It holds when the inbound matches the purchase order, and since 31 August most Shopify brands have had nothing left to match against.

What does your team do when the paperwork does not arrive?""",
"kellypartners": """Your ecommerce clients have a stock problem that shows up as a tax problem, in the shape of COGS nobody can substantiate. The purchase order history behind it left Stocky on 31 August and suppliers never had an export.

Is that landing on your desks yet?""",
}

CLOSING = """Galeka
Small Signal Studio, Surabaya, Indonesia
Not interested? Reply "no thanks" and I won't email again."""

HEAD = """# Batch 4, 20 first emails, written to the Harvey gate

Generated 30 October 2026 by `gen_batch4.py`. Every draft is unique in its opening
line and its question. The footer carries the physical address, which the 20 sends
of 28 October lacked.
"""


def main() -> None:
    out = [HEAD]
    for label, email, subject in TARGETS:
        body = BODIES[label]
        out.append(f"\n---\n\n## {label} | email1\nSubject: {subject}\n\n{body}\n\n{CLOSING}\n")
    open("DRAFTS-BATCH4.md", "w").write("".join(out))
    print(f"wrote DRAFTS-BATCH4.md with {len(TARGETS)} drafts")


if __name__ == "__main__":
    main()
