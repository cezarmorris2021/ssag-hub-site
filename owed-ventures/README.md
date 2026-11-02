# Independent Revenue Ventures — November 2, 2026
Two distinct customer-facing production applications built as separate Vercel projects, with a shared physically separate Neon database and strictly separated venture codes. This branch contains business documentation; deployment source remains in the owner-accessible Vercel deployments, not yet fully mirrored into this branch.

## Venture A — DROP DISTRICT Creator Studio
Public: https://drop-district-creator-studio.vercel.app/
Owner: https://drop-district-creator-studio.vercel.app/owner.html
Health: https://drop-district-creator-studio.vercel.app/api/health
Market: independent musicians, DJs, apparel drops, barbers and nightlife promoters.
Offers: First Drop $149; Release Mode $349; Full Takeover $699. Paid creative production is delivered after receipt, written scope and authorization of all creative assets.

## Venture B — STAYKEY Guest Experience Studio
Public: https://staykey-guest-experience-studio.vercel.app/
Owner: https://staykey-guest-experience-studio.vercel.app/owner.html
Health: https://staykey-guest-experience-studio.vercel.app/api/health
Market: STR hosts, boutique stays and smaller property managers.
Offers: Welcome Essential $179; Signature Stay $399; Host Portfolio $749.
Do not request property access codes or Wi-Fi passwords in the open public form. Collect approved instructions through the agreed secure handoff workflow.

## Payment (PayPal)
Customer intake creates an unpaid request; NO automatic checkout is implied. The owner reviews the scope, sends a real invoice through an independently authenticated PayPal Business account, and records PayPal's invoice or transaction reference when verified. The owner dashboard links to official PayPal Business Invoicing instructions. There is no PayPal API integration and payment confirmation is currently manual.

## Security, privacy, and control
Project-specific strong owner keys are stored as encrypted Vercel environment variables, never in GitHub. Keys are delivered separately to the owner. Do not publish or send them to customers.
Customer requests are stored persistently in the Neon project makeup-revenue-ventures-2026. There are separate venture codes and owner authentication boundaries.
The request endpoint rate limits and validates submissions. Customer receipts use signed private status links; do not share receipt links publicly.
Owner dashboard supports customer record review, invoice preparation and manual payment-reference/status updates. Test orders are excluded from normal owner lists.

## Verified QA on November 2, 2026
Both public sites returned HTTP 200 and both /api/health endpoints showed database connected.
Unauthenticated owner API GET returned HTTP 401.
Each accepted a tagged internal test order (HTTP 201), generated a signed receipt, supported owner-authorized list retrieval, accepted an owner status update, and returned the updated status using the customer receipt link.
No real sale, automatic email, automatic PayPal payment, or fulfillment has been verified. These are distinct functional sales-intake businesses, not revenue-generating claims.

## Launch checklist
1. Open each site's public URL; review public copy and fixed-price deliverables.
2. Open the owner console on your phone and use the private access key supplied separately.
3. For each new request, confirm customer ownership/rights, scope, delivery time, and final written invoice.
4. Create and send an invoice in PayPal Business; record its invoice ID. Pay status remains UNPAID until actual payment verified.
5. Deliver the scoped files manually using a customer-approved delivery method.
6. Update fulfillment status so the customer's private receipt reflects progress.
7. Protect project data, follow opt-outs and legal requirements, and keep a separate financial ledger for taxes and refunds.

Known remaining integrations: direct PayPal API/webhook verification; automatic owner notifications and outbound email; full verified source mirror to GitHub; monitoring and backups. These must be independently tested before being advertised as working.
