# Global Wine Importer Search - 5-Day Phased Plan

## Strategy
- **10 countries per day** (A-Z order)
- **3 OSINT searches per country** = 30 searches/day
- **Google Maps verification** for every company found
- **No missed leads** - comprehensive coverage

---

## Day 1: Countries A-J (Argentina → China)
1. 🇦🇷 **Argentina** - MERCOSUR
2. 🇦🇺 **Australia** - Negotiating FTA
3. 🇦🇹 **Austria** - EU/FTA
4. 🇧🇭 **Bahrain** - Abraham Accords
5. 🇧🇪 **Belgium** - EU/FTA
6. 🇧🇷 **Brazil** - MERCOSUR
7. 🇧🇬 **Bulgaria** - EU/FTA
8. 🇨🇦 **Canada** - FTA
9. 🇨🇱 **Chile** - FTA (via MERCOSUR)
10. 🇨🇳 **China** - Negotiating FTA

**Status:** ⏳ IN PROGRESS

---

## Day 2: Countries C-G (Colombia → Greece)
11. 🇨🇴 **Colombia** - FTA
12. 🇭🇷 **Croatia** - EU/FTA
13. 🇨🇾 **Cyprus** - EU/FTA
14. 🇨🇿 **Czech Republic** - EU/FTA ✅ ALREADY DONE
15. 🇩🇰 **Denmark** - EU/FTA
16. 🇪🇬 **Egypt** - Peace Treaty
17. 🇫🇮 **Finland** - EU/FTA
18. 🇫🇷 **France** - EU/FTA
19. 🇬🇪 **Georgia** - Diplomatic
20. 🇩🇪 **Germany** - EU/FTA

**Status:** 📅 SCHEDULED

---

## Day 3: Countries G-J (Greece → Jordan)
21. 🇬🇷 **Greece** - EU/FTA
22. 🇬🇹 **Guatemala** - FTA
23. 🇭🇰 **Hong Kong** - Diplomatic
24. 🇭🇺 **Hungary** - EU/FTA
25. 🇮🇳 **India** - Negotiating FTA
26. 🇮🇪 **Ireland** - EU/FTA
27. 🇮🇹 **Italy** - EU/FTA
28. 🇯🇵 **Japan** - Diplomatic ✅ ALREADY DONE
29. 🇯🇴 **Jordan** - Peace Treaty
30. (Backup: Luxembourg)

**Status:** 📅 SCHEDULED

---

## Day 4: Countries M-P (Mexico → Portugal)
31. 🇲🇽 **Mexico** - FTA
32. 🇲🇦 **Morocco** - Abraham Accords
33. 🇳🇱 **Netherlands** - EU/FTA
34. 🇳🇿 **New Zealand** - Diplomatic
35. 🇳🇴 **Norway** - EFTA
36. 🇵🇦 **Panama** - FTA
37. 🇵🇭 **Philippines** - Diplomatic
38. 🇵🇱 **Poland** - EU/FTA ✅ ALREADY DONE
39. 🇵🇹 **Portugal** - EU/FTA
40. (Backup: Peru)

**Status:** 📅 SCHEDULED

---

## Day 5: Countries R-Z (Romania → Vietnam)
41. 🇷🇴 **Romania** - EU/FTA ✅ ALREADY DONE
42. 🇸🇬 **Singapore** - Diplomatic
43. 🇸🇰 **Slovakia** - EU/FTA
44. 🇸🇮 **Slovenia** - EU/FTA
45. 🇿🇦 **South Africa** - Diplomatic
46. 🇰🇷 **South Korea** - FTA ✅ ALREADY DONE
47. 🇪🇸 **Spain** - EU/FTA
48. 🇸🇪 **Sweden** - EU/FTA
49. 🇨🇭 **Switzerland** - EFTA
50. 🇹🇭 **Thailand** - Diplomatic
51. 🇹🇷 **Turkey** - FTA
52. 🇦🇪 **UAE** - FTA/Abraham Accords
53. 🇺🇦 **Ukraine** - FTA
54. 🇬🇧 **United Kingdom** - FTA ✅ PARTIAL
55. 🇺🇸 **United States** - FTA ✅ PARTIAL
56. 🇻🇳 **Vietnam** - Negotiating FTA

**Status:** 📅 SCHEDULED

---

## Search Protocols Per Country

### 1. Direct Executive (LinkedIn via Google)
`site:linkedin.com/in/ ("Wine Importer" OR "Distributor" OR "CEO") ("{COUNTRY}") -intitle:jobs`

### 2. Vivino Related (Official Distributors)
`related:vivino.com "wine importer" "{COUNTRY}"`

### 3. Google Maps Address Verification
`"{COMPANY_NAME}" wine importer "{COUNTRY}" address`

---

## Output Format (Enhanced with Maps)
```json
{
  "country": "Country Name",
  "company_name": "Company Ltd",
  "website": "https://verified-url.com",
  "google_maps_address": "123 Wine St, City, Country",
  "decision_maker": "Name",
  "decision_maker_title": "CEO",
  "relevance_score": "Why this is a good lead",
  "israel_trade_status": "FTA",
  "search_date": "2026-02-04"
}
```

---

## Progress Tracker
- ✅ **Already Completed:** Czech Republic, Japan, Poland, Romania, South Korea
- ⏳ **Day 1 (Today):** 10 countries, 30 searches
- 📅 **Days 2-5:** 40 countries remaining
- 🎯 **Total:** 50+ countries, ~150 searches, 200-400 verified companies
