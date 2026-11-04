# SSAG BidDesk Pro

**Product:** a local-first contractor estimate builder, customer proposal workstation, and manually evidenced opportunity tracker.

**Public offer:** https://ssag-biddesk-pro.vercel.app/  
**Working application:** https://ssag-biddesk-pro.vercel.app/app.html  
**SSAG Hub:** https://cezarmorris2021.github.io/ssag-hub-site/  
**Owner prospect queue:** https://docs.google.com/spreadsheets/d/1-AZV0e8WxusVytTphS3D30bLTIatc87ydqE03hnWHRc/edit#gid=913006

## Scope already delivered
- Responsive customer-facing product page with truthful scope and offer.
- Local quote editor: client, project, scope, itemized quantities and prices, discount, optional tax and deposit.
- Print/PDF-ready project estimate.
- Statused local pipeline, manually dated follow-ups, proof field required for sent/accepted/invoiced/paid stages.
- Email and follow-up **drafts only** through the user's installed mail client. No automatic send is claimed.
- CSV export, JSON backup/restore and company-level branding options.
- URL for a verified company PayPal link on the quote, when **customer supplies one**; no payment processing or PayPal verification by BidDesk.
- Product marketing page has a direct email contact fallback to SSAG.

## Product and services pricing
A proposed **$299 configured setup + optional $49/month** managed support offer. A quote or website visit is **not** revenue. Treat fee and support terms as a proposed commercial offer until agreed in writing. Do not imply a guaranteed sales or conversion outcome.

## Onboarding SOP — real customers
1. Receive a customer inquiry through SSAG email or the SSAG ClientFlow intake; confirm its actual receipt before marking contact.
2. Confirm contractor trade, default quote templates, business branding/contact information, terms/exclusions, tax handling and verified PayPal URL.
3. Confirm scope and send a written statement of work and the verified invoice/payment option through a real payment provider.
4. Verify the PayPal transaction using authoritative receipt evidence, **not** a click or manually edited status.
5. Configure company settings in the customer's browser, demonstrate a sample quote, and test print/save-to-PDF and email draft workflow.
6. Instruct customer to export encrypted backups regularly. Do not collect/store regulated personal information in browser localStorage.
7. If ongoing monthly support is purchased, record it separately as contracted MRR only after executed agreement and verified payment and actual support.

## Current blockers — must not claim as complete
- Browser quote pipeline is **not** centrally synchronized across devices, authenticated or tenant-isolated. This is a local-first application, not a multi-tenant SaaS subscription.
- Email drafts from the app **do not prove sending**, and public outreach needs CAN-SPAM compliant identification, sender postal address, reply-based opt-out handling, complaint management and suppression.
- SSAG ClientFlow PayPal links were **not configured** when audited. This product cannot automatically invoice/charge.
- No real customer for BidDesk Pro, paid invoice, conversion, delivered paid support or consented recurring billing has been evidenced.
- Source public contact emails must be rechecked before sending and unsubscribed/previously contacted companies suppressed.
- Prospect list lives in the existing SSAG AI Call Tracker tab `BidDesk Prospect Outreach`, with verified evidence states. Do not mark draft as contacted.

## Basic functionality checks
- Open the live product URL and the application URL.
- Company Settings: configure a fake test company name and terms **on a test device only**.
- Enter test client, project and two example line items, e.g. 2 units × $100 and 1 unit × $50, discount $10, tax 5%, deposit 25%.
- Expected subtotal $250, discounted taxable base $240, tax $12, total $252, deposit $63.
- Save a draft, open pipeline, reload and confirm test quote persisted locally; export JSON; print to PDF; verify exported values; delete test entries afterward.
- Confirm attempts to set `Sent` or `Paid — verified` without evidence are refused.
- Verify public page and app are reachable without Vercel Authentication, and contact mailto opens the email app.

## Privacy and legal
This software is offered as an estimating tool; it is not tax, legal, accounting or compliance advice. The user is responsible for job-site quote accuracy, license requirements, local tax rules and customer data security. For commercial email see FTC's CAN-SPAM guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business.

## Source control and hosting
GitHub: `cezarmorris2021/ssag-hub-site/biddesk-pro/`; Vercel project: `ssag-biddesk-pro` under the owner's existing team. An incident affecting customer info, quote accuracy or payment evidence must be tracked, never hidden.
