"""The 31 stories of Sunday 22 November 2026.

Each entry was first reported on 2026-11-22.  Fields:
  n        printed number, 1..31, unique
  region   one of REGIONS (seven, as in the legend)
  lat/lon  exact map-dot coordinates
  place    dateline tag drawn into the illustration
  kicker   coloured strip on an illustrated card
  headline big card type / list type
  body     two short lines on an illustrated card
  source   outlet named beside the story
  status   CONFIRMED / OFFICIAL / REPORTED / CLAIM
  size     main (3), small (8) or brief (20)
  scene    vignette key used by render.py
  brief    one-line index entry
"""

DAY = "2026-11-22"

STORIES = [
    # ---- 3 lead stories ----------------------------------------------------
    dict(n=1, region="World", place="ANTALYA, TÜRKIYE", lat=36.90, lon=30.71,
         kicker="COP31 · FOSSIL DEAL REJECTED", headline="COP31 ends with no climate deal",
         body="EU rejects draft after 44 hours of overtime.",
         source="Reuters / RFI", status="CONFIRMED", size="main", scene="cop",
         brief="Antalya: COP31 collapses as EU rejects fossil-free draft"),

    dict(n=2, region="Middle East", place="STRAIT OF HORMUZ", lat=26.57, lon=56.25,
         kicker="IRAN STRIKES 3 TANKERS", headline="Iran strikes three tankers as blockade bites",
         body="Tehran calls US siege an act of war.",
         source="AP / Al Jazeera", status="CONFIRMED", size="main", scene="hormuz",
         brief="Hormuz: Iran hits 3 tankers, vows to break US blockade"),

    dict(n=3, region="Europe", place="DYMER, KYIV REGION", lat=50.75, lon=30.50,
         kicker="RUSSIAN DRONE · 14 MISSING", headline="Drone strike collapses apartment block",
         body="Two children missing; US pressed on Patriots.",
         source="Politico / AP", status="CONFIRMED", size="main", scene="dymer",
         brief="Dymer: 14 missing after drone hits apartment block"),

    # ---- 8 illustrated stories ---------------------------------------------
    dict(n=4, region="Europe", place="GULF OF FINLAND", lat=59.80, lon=26.50,
         kicker="DRONE HITS RUSSIAN SHIP", headline="Cargo ship struck off Finland",
         body="Blast on Russian vessel fuels fears of war spreading to the Baltic.",
         source="Reuters / SBS", status="REPORTED", size="small", scene="shipdrone",
         brief="Finland: Russian cargo ship hit by drones off the coast"),

    dict(n=5, region="Europe", place="POLAND", lat=52.20, lon=21.00,
         kicker="MISSILE + DRONE IN POLAND", headline="Missile and drone hit Poland",
         body="Debris recovered as allies demand answers from Moscow.",
         source="Reuters / AP", status="REPORTED", size="small", scene="poland",
         brief="Poland: Russian missile and drone found on NATO soil"),

    dict(n=6, region="Middle East", place="WEST BANK", lat=32.00, lon=35.30,
         kicker="SETTLERS HIT 4 VILLAGES", headline="Four villages hit in settler attacks",
         body="Activists blame Israeli settlers; vehicles and property set alight.",
         source="CBS / Yahoo", status="REPORTED", size="small", scene="westbank",
         brief="West Bank: four villages targeted in suspected settler attacks"),

    dict(n=7, region="Africa", place="BENGHAZI, LIBYA", lat=32.12, lon=20.07,
         kicker="DRONE BLAST ON RUSSIAN SHIP", headline="Blast rocks Russian ship at Benghazi",
         body="Eastern government says a drone caused the blast at the naval base.",
         source="BBC / DDCN", status="REPORTED", size="small", scene="benghazi",
         brief="Benghazi: explosion on Russian ship blamed on drone"),

    dict(n=8, region="Americas", place="SEATTLE, USA", lat=47.45, lon=-122.31,
         kicker="ICE ARRESTS AT SEA-TAC", headline="Agents arrest pair on airport jetway",
         body="Washington's governor calls the operation 'out of control'.",
         source="The Independent", status="CONFIRMED", size="small", scene="ice",
         brief="Seattle: ICE arrests on jetway draw governor's condemnation"),

    dict(n=9, region="Americas", place="WASHINGTON, USA", lat=38.90, lon=-77.04,
         kicker="US EASES CANADA TARIFFS", headline="Trump eases some Canada tariffs",
         body="The move comes days before midterms as trade talks resume.",
         source="DW", status="REPORTED", size="small", scene="tariff",
         brief="Washington: Trump softens some tariffs on Canada"),

    dict(n=10, region="Americas", place="LAS VEGAS, USA", lat=36.17, lon=-115.14,
         kicker="VERSTAPPEN WINS VEGAS", headline="Verstappen wins Vegas Grand Prix",
         body="He holds off Russell, Antonelli and Norris for a third Vegas win.",
         source="Formula 1 / The Hindu", status="CONFIRMED", size="small", scene="f1",
         brief="Las Vegas: Verstappen wins third Vegas GP in four years"),

    dict(n=11, region="Asia", place="TOKYO / NEW DELHI", lat=35.68, lon=139.69,
         kicker="JAPAN-INDIA DEFENCE PACT", headline="Japan, India deepen defence ties",
         body="Leaders agree to widen military and defence-industry cooperation.",
         source="AP", status="CONFIRMED", size="small", scene="flags_jp_in",
         brief="Tokyo: Japan and India agree wider defence cooperation"),

    # ---- 20 brief stories: 10 left (Europe/Africa/Americas) -----------------
    dict(n=12, region="Europe", place="UKRAINE", lat=49.00, lon=31.40,
         kicker="SCHOOLS", headline="City shifts to remote learning",
         body="Strikes disrupt heat, power and water supplies.",
         source="Washington Post", status="CONFIRMED", size="brief", scene="pin",
         brief="Ukraine: city moves to remote learning after utility strikes"),

    dict(n=13, region="Europe", place="RUDNINKAI, LITHUANIA", lat=54.16, lon=24.86,
         kicker="DRILLS · LITHUANIA", headline="German army tests kamikaze drones",
         body="First tactical trials held near the Belarus border.",
         source="Reuters", status="CONFIRMED", size="brief", scene="pin",
         brief="Lithuania: German army tests kamikaze drones, AI targeting"),

    dict(n=14, region="Africa", place="OYO, CONGO", lat=-1.88, lon=15.01,
         kicker="SUMMIT", headline="Ruto arrives for four-party talks",
         body="Leaders of Congo, DRC and Togo join the quadripartite summit.",
         source="Dawan Africa", status="CONFIRMED", size="brief", scene="pin",
         brief="Congo: Ruto lands in Oyo for quadripartite summit"),

    dict(n=15, region="Africa", place="MASERU, LESOTHO", lat=-29.31, lon=27.48,
         kicker="FOOD AID", headline="1,200 tonnes of Chinese grain arrive",
         body="Delivery follows a national food-insecurity declaration.",
         source="Govt of Lesotho", status="OFFICIAL", size="brief", scene="pin",
         brief="Lesotho: receives 1,200 tonnes of Chinese food aid"),

    dict(n=16, region="Africa", place="PRETORIA, SOUTH AFRICA", lat=-25.75, lon=28.23,
         kicker="AI FUND", headline="Ramaphosa unveils R100m startup fund",
         body="New money is aimed at South African AI companies.",
         source="Presidency ZA", status="OFFICIAL", size="brief", scene="pin",
         brief="South Africa: R100m AI fund for startups announced"),

    dict(n=17, region="Africa", place="NAIROBI, KENYA", lat=-1.29, lon=36.82,
         kicker="FOOTBALL", headline="FKF denies selection interference",
         body="Federation rejects claims over Harambee Stars squad rows.",
         source="Dawan Africa", status="REPORTED", size="brief", scene="pin",
         brief="Kenya: FKF denies interfering in national-team selection"),

    dict(n=18, region="Americas", place="NEW YORK, USA", lat=40.71, lon=-74.01,
         kicker="MARKETS", headline="Wall Street slides into correction",
         body="S&P 500 drops 3.7% in a seventh straight losing session.",
         source="US News", status="CONFIRMED", size="brief", scene="pin",
         brief="New York: stocks enter correction, S&P off 3.7%"),

    dict(n=19, region="Americas", place="WASHINGTON, USA", lat=38.89, lon=-77.02,
         kicker="POLITICS", headline="Trump: 'very hard' with Schumer",
         body="President predicts the Senate minority leader will fail again.",
         source="USA Today", status="REPORTED", size="brief", scene="pin",
         brief="Washington: Trump says working with Schumer will be hard"),

    dict(n=20, region="Americas", place="WASHINGTON, USA", lat=38.88, lon=-77.05,
         kicker="DEFENCE · MEMO", headline="Hegseth curbs US-Canada defence ties",
         body="A classified memo limits joint military work.",
         source="WaPo / JPost", status="REPORTED", size="brief", scene="pin",
         brief="Washington: Hegseth tightens US-Canada defence partnership"),

    dict(n=21, region="Americas", place="VANDENBERG, USA", lat=34.63, lon=-120.60,
         kicker="SPACE", headline="Spy satellites launch on record turnaround",
         body="Falcon 9 flies NROL-136 just 32 hours after the previous pad launch.",
         source="Spaceflight Now", status="CONFIRMED", size="brief", scene="pin",
         brief="California: NROL-136 launch sets 32-hour pad record"),

    # ---- 20 brief stories: 10 right (Middle East/Asia/Oceania) --------------
    dict(n=22, region="Middle East", place="DOHA, QATAR", lat=25.29, lon=51.53,
         kicker="MEDIATION", headline="Iran holds talks with Qatari mediators",
         body="Tehran urges Washington to accept its conditions.",
         source="Al Jazeera", status="REPORTED", size="brief", scene="pin",
         brief="Doha: Iran talks to mediators, urges US to accept terms"),

    dict(n=23, region="Middle East", place="TEHRAN, IRAN", lat=35.69, lon=51.39,
         kicker="HORMUZ", headline="Reopening strait 'not difficult'",
         body="Iranian minister says a deal with the US is within reach.",
         source="Al Jazeera", status="REPORTED", size="brief", scene="pin",
         brief="Tehran: says reopening Hormuz is not difficult if US agrees"),

    dict(n=24, region="Middle East", place="KHARG ISLAND, IRAN", lat=29.23, lon=50.32,
         kicker="SHIPPING", headline="Tanker convoy stages near Kharg",
         body="More than 14 vessels gather under naval guard.",
         source="Euronews / AP", status="CLAIM", size="brief", scene="pin",
         brief="Kharg Island: tanker convoy gathers as blockade tightens"),

    dict(n=25, region="Asia", place="ARUNACHAL PRADESH, INDIA", lat=28.20, lon=94.70,
         kicker="BORDER", headline="India, China hold 10 days of LAC talks",
         body="New round aims to ease tensions along the disputed frontier.",
         source="The Hindu", status="CONFIRMED", size="brief", scene="pin",
         brief="Arunachal: India and China hold 10-day border talks"),

    dict(n=26, region="Asia", place="BEIJING, CHINA", lat=39.90, lon=116.41,
         kicker="TAIWAN", headline="China urges Japan to retract remarks",
         body="Military media renew pressure over Takaichi's comments.",
         source="AFP", status="OFFICIAL", size="brief", scene="pin",
         brief="Beijing: urges Tokyo to retract Taiwan remarks"),

    dict(n=27, region="Asia", place="TOKYO, JAPAN", lat=35.69, lon=139.70,
         kicker="APEC", headline="Takaichi and Putin hold talks",
         body="Leaders meet on the sidelines of the China summit.",
         source="TBS", status="OFFICIAL", size="brief", scene="pin",
         brief="Tokyo: PM Takaichi and Putin hold APEC talks"),

    dict(n=28, region="Asia", place="NEW DELHI, INDIA", lat=28.61, lon=77.21,
         kicker="SCO", headline="Pakistan minister visits India",
         body="First senior Pakistani visit since 2023, under SCO banner.",
         source="The Hindu", status="CONFIRMED", size="brief", scene="pin",
         brief="Delhi: first senior Pakistani minister visit since 2023"),

    dict(n=29, region="Asia", place="CHENNAI, INDIA", lat=13.08, lon=80.27,
         kicker="COURT", headline="Tamil Nadu files review plea",
         body="State challenges a Supreme Court lamp-lighting order.",
         source="The Hindu", status="CONFIRMED", size="brief", scene="pin",
         brief="Chennai: Tamil Nadu files review plea over lamp order"),

    dict(n=30, region="Oceania", place="AUSTRALIA", lat=-25.27, lon=133.78,
         kicker="BOWLS", headline="Oceania Challenge day four wrapped",
         body="Australia closes out the regional competition.",
         source="Bowls Australia", status="CONFIRMED", size="brief", scene="pin",
         brief="Australia: Oceania Challenge bowls event reaches day four"),

    dict(n=31, region="Oceania", place="WELLINGTON, NZ", lat=-41.29, lon=174.78,
         kicker="CRICKET", headline="India 720/9; NZ bat on day four",
         body="Jurel's 78 anchors India's huge first-Test total.",
         source="The Hindu", status="CONFIRMED", size="brief", scene="pin",
         brief="Wellington: India post 720/9 in first Test against NZ"),
]

# Line 2 of the DATE CHECK box: excluded stories and the reason, compactly.
DATE_CHECK = (
    "Left out, wrong date: Trump-Xi-Putin summit (19 Nov) · UK-EU deal (20 Nov) · "
    "Alaska Senate flip (18 Nov) · Peru quake (21 Nov)."
)

SOURCES_LINE = (
    "Sources named beside each story · Original drawings · HOW WE CHECKED: CONFIRMED = two or "
    "more outlets · OFFICIAL = on the record · REPORTED = one outlet · CLAIM = one side's account."
)

REGIONS = ["Europe", "Middle East", "Africa", "Asia", "Americas", "Oceania", "World"]

REGION_COLORS = {
    "Europe": "#2E5FA3",
    "Middle East": "#C25B1B",
    "Africa": "#2E7D45",
    "Asia": "#B22A2A",
    "Americas": "#6A3D96",
    "Oceania": "#158A87",
    "World": "#6E6E6E",
}
