# SSAG Arizona Website Opportunity Engine

Internal SSAG acquisition tool for finding Arizona businesses whose public OpenStreetMap record includes a phone number but no website URL, verifying the opportunity, generating a tailored website concept, producing a brief sales script, and tracking the lead through a lightweight local CRM.

## Operating flow

1. Search statewide, by city/town, or by ZIP.
2. Review opportunity score and business details.
3. Use **Verify Website** before claiming the business has no website.
4. Mark verified opportunities.
5. Select **Build Preview** to generate a mobile-first website concept.
6. Copy the shareable preview link or download the generated HTML.
7. Select **Call Script** for the personalized pitch and phone number.
8. Move the lead through Called → Interested → Follow Up → Sold.
9. Export CSV or create a JSON backup.

## Data and accuracy

- Business discovery uses public OpenStreetMap data through Overpass.
- City/ZIP geocoding uses Nominatim only on user request and caches lookups for 30 days.
- A missing website field is only a lead signal, not proof that no website exists.
- The website generator does not invent reviews, licensing, years in business, or unverified business claims.
- Before public launch, the owner must confirm services, hours, contact information, business claims, and branding.

## Production scaling

Public OSM services are suitable for light/small-project use and can be incomplete. At higher sales volume, replace the discovery/geocoding adapters with a licensed commercial business-data provider or self-hosted OSM/Overpass/Nominatim infrastructure. Keep the verification step even after upgrading data sources.

## Default offer

- Setup: $799
- Monthly management: $89

Both values are editable in the tool and stored locally on the device.

## Storage

Pipeline data is stored in browser localStorage. Use **Backup** regularly and **Export CSV** for the operating record.
