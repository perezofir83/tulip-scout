# Global Wine Importer OSINT Research - Country Priority List

## Total Eligible Countries: 166 (with Israel diplomatic/trade relations)

### Excluded (26 countries - No Israel recognition):
Algeria, Comoros, Djibouti, Iraq, Kuwait, Lebanon, Libya, Oman, Qatar, Saudi Arabia, Somalia, Syria, Tunisia, Yemen, Afghanistan, Bangladesh, Brunei, Indonesia, Iran, Malaysia, Maldives, Mali, Niger, Pakistan, Cuba, North Korea

---

## Priority Search Strategy (Top 50 Wine-Importing Countries)

### Tier 1: Major Wine Importers (Top 20) 🔴
1. **United States** 🇺🇸 - #1 wine importer globally
2. **United Kingdom** 🇬🇧 - FTA, #2 importer
3. **Germany** 🇩🇪 - EU, major importer
4. **France** 🇫🇷 - EU, producer but also imports
5. **Netherlands** 🇳🇱 - EU, logistics hub
6. **Canada** 🇨🇦 - FTA
7. **Japan** 🇯🇵 - Asia #1 importer
8. **Belgium** 🇧🇪 - EU
9. **China** 🇨🇳 - Fastest growing
10. **Switzerland** 🇨🇭 - EFTA, high per-capita
11. **Russia** 🇷🇺 (NOTE: Check sanctions status)
12. **Denmark** 🇩🇰 - EU
13. **South Korea** 🇰🇷 - FTA, strong growth
14. **Sweden** 🇸🇪 - EU
15. **Italy** 🇮🇹 - EU, producer+importer
16. **Spain** 🇪🇸 - EU, producer+importer
17. **Austria** 🇦🇹 - EU
18. **Australia** 🇦🇺 - Negotiating FTA
19. **Singapore** 🇸🇬 - Asia hub
20. **Hong Kong** 🇭🇰 - Asia trade hub

### Tier 2: Emerging Markets (21-40) 🟡
21. **Poland** 🇵🇱 - FTA ✅ SEARCHED
22. **Czech Republic** 🇨🇿 - FTA ✅ SEARCHED  
23. **Romania** 🇷🇴 - FTA ✅ SEARCHED
24. **Mexico** 🇲🇽 - FTA
25. **Brazil** 🇧🇷 - MERCOSUR
26. **Argentina** 🇦🇷 - MERCOSUR
27. **India** 🇮🇳 - Negotiating FTA
28. **Thailand** 🇹🇭
29. **Vietnam** 🇻🇳 - Negotiating FTA
30. **Philippines** 🇵🇭
31. **Taiwan** 🇹🇼
32. **Ireland** 🇮🇪 - EU
33. **Portugal** 🇵🇹 - EU
34. **Greece** 🇬🇷 - EU
35. **Finland** 🇫🇮 - EU
36. **Norway** 🇳🇴 - EFTA
37. **New Zealand** 🇳🇿
38. **South Africa** 🇿🇦
39. **Turkey** 🇹🇷 - FTA
40. **Ukraine** 🇺🇦 - FTA

### Tier 3: Abraham Accords + Strategic (41-50) 🟢
41. **UAE** 🇦🇪 - FTA (2022), Abraham Accords
42. **Bahrain** 🇧🇭 - Negotiating FTA, Abraham Accords
43. **Morocco** 🇲🇦 - Abraham Accords
44. **Egypt** 🇪🇬 - Peace treaty, trade relations
45. **Jordan** 🇯🇴 - Peace treaty, preferential trade
46. **Colombia** 🇨🇴 - FTA
47. **Panama** 🇵🇦 - FTA
48. **Guatemala** 🇬🇹 - FTA
49. **Hungary** 🇭🇺 - EU, FTA
50. **Slovakia** 🇸🇰 - EU, FTA

---

## Search Protocols Per Country

### Protocol 1: Direct Executive (LinkedIn Index)
`site:linkedin.com/in/ ("Wine Importer" OR "Distributor" OR "CEO") ("{COUNTRY}") -intitle:jobs`

### Protocol 2: Official Entity (Vivino Related)
`related:vivino.com "wine importer" "{COUNTRY}"`

### Protocol 3: Company Directory
`"wine importer" OR "wine distributor" site:.{TLD} -site:linkedin.com`

### Protocol 4: Portfolio Match (PDFs)
`filetype:pdf "wine portfolio" site:.{TLD}`

---

## Execution Plan

1. **Phase 1**: Search Tier 1 (Countries 1-20) - ~60 searches
2. **Phase 2**: Search Tier 2 (Countries 21-40) - ~60 searches  
3. **Phase 3**: Search Tier 3 (Countries 41-50) - ~30 searches
4. **Phase 4**: Verify all websites are live
5. **Phase 5**: Compile master JSON with complete data

**Total Searches**: ~150 OSINT queries
**Expected Leads**: 150-300 companies with verified websites

---

## Output Format (JSON)
```json
{
  "country": "Country Name",
  "country_code": "XX",
  "company_name": "Company Ltd",
  "website": "https://verified-url.com",
  "decision_maker": "Name",
  "decision_maker_title": "CEO",
  "protocol": "direct_executive",
  "relevance_score": "Why this is a good lead",
  "israel_trade_status": "FTA" | "Abraham Accords" | "Diplomatic" | "Negotiating FTA"
}
```
