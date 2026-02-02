import json
import requests

# Fetch hero data from OpenDota API
try:
    response = requests.get("https://api.opendota.com/api/heroes", timeout=10)
    response.raise_for_status()
    IdResponse = json.loads(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error fetching hero data: {e}")
    exit(1)

IdtoName = {}
NametoId = {}

for item in IdResponse:
    IdtoName[item['id']] = item['localized_name']
    NametoId[item['localized_name'].lower()] = item['id']

# Take input of Names
print("Enter 4 enemy hero names:")
a = input("Enter first hero: ").strip()
b = input("Enter second hero: ").strip()
c = input("Enter third hero: ").strip()
d = input("Enter fourth hero: ").strip()

# Convert names to id numbers from opendota
def get_hero_id(hero_name):
    hero_id = NametoId.get(hero_name.lower())
    if hero_id is None:
        print(f"Error: Hero '{hero_name}' not found!")
        exit(1)
    return hero_id

id1 = get_hero_id(a)
id2 = get_hero_id(b)
id3 = get_hero_id(c)
id4 = get_hero_id(d)

# Function to get matchup data for a hero
def get_matchup_data(hero_id, winpercent_key, exclude_ids):
    """Fetch matchup data for a hero and calculate win percentages"""
    try:
        matchup_url = f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
        response = requests.get(matchup_url, timeout=10)
        response.raise_for_status()
        matchup_data = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching matchup data for hero {hero_id}: {e}")
        exit(1)
    
    # Calculate win percentages and filter out excluded heroes
    processed_matchups = []
    for item in matchup_data:
        if item['hero_id'] not in exclude_ids:
            games = int(item['games_played'])
            if games > 0:
                winpercent = (int(item['wins']) / games) * 100
                processed_matchups.append({
                    'hero_id': item['hero_id'],
                    winpercent_key: winpercent
                })
    
    return sorted(processed_matchups, key=lambda x: x['hero_id'])

# Get matchup data for all 4 heroes
enemy_ids = [id1, id2, id3, id4]
print("\nFetching matchup data...")

SortedMatchup1 = get_matchup_data(id1, 'winpercent1', enemy_ids)
SortedMatchup2 = get_matchup_data(id2, 'winpercent2', enemy_ids)
SortedMatchup3 = get_matchup_data(id3, 'winpercent3', enemy_ids)
SortedMatchup4 = get_matchup_data(id4, 'winpercent4', enemy_ids)

# Merge all matchup data into a single dictionary
# Create a dict for efficient lookups
matchup_dict = {}

for item in SortedMatchup1:
    hero_id = item['hero_id']
    matchup_dict[hero_id] = {'hero_id': hero_id, 'winpercent1': item['winpercent1']}

for item in SortedMatchup2:
    hero_id = item['hero_id']
    if hero_id in matchup_dict:
        matchup_dict[hero_id]['winpercent2'] = item['winpercent2']

for item in SortedMatchup3:
    hero_id = item['hero_id']
    if hero_id in matchup_dict:
        matchup_dict[hero_id]['winpercent3'] = item['winpercent3']

for item in SortedMatchup4:
    hero_id = item['hero_id']
    if hero_id in matchup_dict:
        matchup_dict[hero_id]['winpercent4'] = item['winpercent4']

# Only include heroes that have data for all 4 matchups
SortedMatchup = [
    data for data in matchup_dict.values()
    if all(key in data for key in ['winpercent1', 'winpercent2', 'winpercent3', 'winpercent4'])
]

# Calculate geometric mean (balanced measure of effectiveness against all 4 enemies)
for i in SortedMatchup:
    i['geo_mean'] = (i['winpercent1'] * i['winpercent2'] * i['winpercent3'] * i['winpercent4']) ** 0.25
    i['avg_winrate'] = (i['winpercent1'] + i['winpercent2'] + i['winpercent3'] + i['winpercent4']) / 4

# Sort by geometric mean (descending - best counters first)
SortedWinproducts = sorted(SortedMatchup, key=lambda x: x['geo_mean'], reverse=True)

# Display results
print("\n" + "="*60)
print("BEST HERO COUNTERS (against your enemy team)")
print("="*60)

for rank, hero in enumerate(SortedWinproducts[:15], 1):
    hero_name = IdtoName[hero['hero_id']]
    geo_mean = hero['geo_mean']
    avg_wr = hero['avg_winrate']
    print(f"{rank:2}. {hero_name:25} - Geo Mean: {geo_mean:.1f}% (Avg: {avg_wr:.1f}%)")
    print(f"    vs {a}: {hero['winpercent1']:.1f}% | vs {b}: {hero['winpercent2']:.1f}% | "
          f"vs {c}: {hero['winpercent3']:.1f}% | vs {d}: {hero['winpercent4']:.1f}%")
    print()

