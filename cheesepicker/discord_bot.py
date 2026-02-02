import discord
from discord import app_commands
import json
import requests
import os
from typing import List, Dict
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Cache hero data to avoid repeated API calls
hero_data = {}
IdtoName = {}
NametoId = {}
HeroRoles = {}  # Store hero roles
HeroPositions = {}  # Store which positions (1-5) each hero can play

# Hero position/role mappings (can be extended)
HERO_POSITIONS = {
    1: ['carry', 'pos1', 'position 1', 'pos 1', 'safelane', 'safe'],
    2: ['mid', 'pos2', 'position 2', 'pos 2', 'midlane'],
    3: ['offlane', 'pos3', 'position 3', 'pos 3', 'offlaner'],
    4: ['support', 'pos4', 'position 4', 'pos 4', 'soft support', 'roamer'],
    5: ['hard support', 'pos5', 'position 5', 'pos 5', 'hardsupport']
}

# Common hero nicknames and abbreviations
HERO_NICKNAMES = {
    # Common abbreviations
    'am': 'anti-mage',
    'qop': 'queen of pain',
    'wr': 'windranger',
    'wk': 'wraith king',
    'pa': 'phantom assassin',
    'pl': 'phantom lancer',
    'ta': 'templar assassin',
    'sf': 'shadow fiend',
    'lc': 'legion commander',
    'ck': 'chaos knight',
    'dk': 'dragon knight',
    'od': 'outworld destroyer',
    'np': "nature's prophet",
    'kotl': 'keeper of the light',
    'sb': 'spirit breaker',
    'cm': 'crystal maiden',
    'es': 'earth spirit',
    'ss': 'shadow shaman',
    'wd': 'witch doctor',
    'sk': 'sand king',
    
    # Old/lore names
    'furion': "nature's prophet",
    'naix': 'lifestealer',
    'barathrum': 'spirit breaker',
    'bara': 'spirit breaker',
    'leoric': 'skeleton king',
    'skeleton king': 'wraith king',
    'windrunner': 'windranger',
    'wisp': 'io',
    'necrolyte': 'necrophos',
    'obsidian destroyer': 'outworld destroyer',
    'outworld devourer': 'outworld destroyer',
    'outhouse decorator': 'outworld destroyer',
    'azwraith': 'phantom lancer',
    'lanaya': 'templar assassin',
    'mortred': 'phantom assassin',
    'mireska': 'dark willow',
    'yurnero': 'juggernaut',
    'mangix': 'brewmaster',
    'rigwarl': 'bristleback',
    'razzil': 'alchemist',
    'kaldr': 'ancient apparition',
    'kaolin': 'earth spirit',
    'xin': 'ember spirit',
    'raijin': 'storm spirit',
    'boush': 'tinker',
    'kardel': 'sniper',
    'kunkka': 'kunkka',
    'gondar': 'bounty hunter',
    'traxex': 'drow ranger',
    'aiushtha': 'enchantress',
    'nerif': 'oracle',
    'nortrom': 'silencer',
    'krobelus': 'death prophet',
    'mercurial': 'spectre',
    'rhasta': 'shadow shaman',
    'banehallow': 'lycanthrope',
    'lycan': 'lycanthrope',
    'atropos': 'bane',
    'ethreain': 'lich',
    'demnok': 'warlock',
    'zharvakko': 'witch doctor',
    'aggron': 'ogre magi',
    
    # Common nicknames
    'potm': 'mirana',
    'necro': 'necrophos',
    'shaker': 'earthshaker',
    'medu': 'medusa',
    'dusa': 'medusa',
    'slark': 'slark',
    'sven': 'sven',
    'tiny': 'tiny',
    'tide': 'tidehunter',
    'timber': 'timbersaw',
    'treant': 'treant protector',
    'troll': 'troll warlord',
    'void': 'faceless void',
    'fv': 'faceless void',
    'vs': 'vengeful spirit',
    'venge': 'vengeful spirit',
    'maiden': 'crystal maiden',
    'axe': 'axe',
    'bat': 'batrider',
    'brew': 'brewmaster',
    'bristle': 'bristleback',
    'cent': 'centaur warrunner',
    'clock': 'clockwerk',
    'doom': 'doom',
    'ember': 'ember spirit',
    'storm': 'storm spirit',
    'morph': 'morphling',
    'naga': 'naga siren',
    'puck': 'puck',
    'pudge': 'pudge',
    'razor': 'razor',
    'riki': 'riki',
    'rubick': 'rubick',
    'sand': 'sand king',
    'shaman': 'shadow shaman',
    'sniper': 'sniper',
    'spectre': 'spectre',
    'slardar': 'slardar',
    'snapfire': 'snapfire',
    'lion': 'lion',
    'lina': 'lina',
    'dazzle': 'dazzle',
    'disruptor': 'disruptor',
    'ench': 'enchantress',
    'jakiro': 'jakiro',
    'lich': 'lich',
    'ogre': 'ogre magi',
    'oracle': 'oracle',
    'silencer': 'silencer',
    'sky': 'skywrath mage',
    'warlock': 'warlock',
    'doctor': 'witch doctor',
    'invoker': 'invoker',
    'zeus': 'zeus',
    'bh': 'bounty hunter',
    'gondar': 'bounty hunter',
    'clinkz': 'clinkz',
    'weaver': 'weaver',
    'brood': 'broodmother',
    'ns': 'night stalker',
    'bane': 'bane',
    'aa': 'ancient apparition',
    'appa': 'ancient apparition',
    'chen': 'chen',
    'ds': 'dark seer',
    'dp': 'death prophet',
    'krobe': 'death prophet',
    'earthspirit': 'earth spirit',
    'emberspirit': 'ember spirit',
    'stormspirit': 'storm spirit',
    'voidspirit': 'void spirit',
    'enigma': 'enigma',
    'gyro': 'gyrocopter',
    'hoodwink': 'hoodwink',
    'huskar': 'huskar',
    'jugg': 'juggernaut',
    'juggernaut': 'juggernaut',
    'lesh': 'leshrac',
    'leshrac': 'leshrac',
    'luna': 'luna',
    'magnus': 'magnus',
    'mag': 'magnus',
    'marci': 'marci',
    'mars': 'mars',
    'medusa': 'medusa',
    'meepo': 'meepo',
    'mirana': 'mirana',
    'mk': 'monkey king',
    'monkey': 'monkey king',
    'morphling': 'morphling',
    'muerta': 'muerta',
    'nyx': 'nyx assassin',
    'phoenix': 'phoenix',
    'primal': 'primal beast',
    'beast': 'primal beast',
    'pango': 'pangolier',
    'tb': 'terrorblade',
    'terror': 'terrorblade',
    'arc': 'arc warden',
    'warden': 'arc warden',
    'zet': 'arc warden',
    'willow': 'dark willow',
    'grimstroke': 'grimstroke',
    'grim': 'grimstroke',
    'io': 'io',
    'kez': 'kez',
    'largo': 'largo',
    'mars': 'mars',
    'snapfire': 'snapfire',
    'snap': 'snapfire',
    'void spirit': 'void spirit',
    'vs': 'void spirit',
}

def fetch_hero_data():
    """Fetch and cache hero data from OpenDota API including position stats"""
    global hero_data, IdtoName, NametoId, HeroRoles, HeroPositions
    
    # Cache file path
    cache_file = 'hero_positions_cache.json'
    cache_duration = timedelta(days=7)  # Cache for 1 week
    
    try:
        # Fetch basic hero data
        response = requests.get("https://api.opendota.com/api/heroes", timeout=10)
        response.raise_for_status()
        hero_data = json.loads(response.text)
        
        for item in hero_data:
            IdtoName[item['id']] = item['localized_name']
            NametoId[item['localized_name'].lower()] = item['id']
            # Store roles - OpenDota provides role info
            if 'roles' in item:
                HeroRoles[item['id']] = [role.lower() for role in item['roles']]
        
        print(f"Loaded {len(hero_data)} heroes: {len(IdtoName)} in IdtoName, {len(NametoId)} in NametoId")
        
        # Check if cached position data exists and is fresh
        use_cache = False
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    cache_source = cache_data.get('source', 'Unknown')
                    
                    if datetime.now() - cache_time < cache_duration:
                        # Cache is fresh, use it
                        HeroPositions = {int(k): v for k, v in cache_data['positions'].items()}
                        use_cache = True
                        days_old = (datetime.now() - cache_time).days
                        print(f"Using cached position data: {cache_source} ({days_old} days old, {len([h for h in HeroPositions.values() if h])} heroes)")
            except Exception as e:
                print(f"Cache read error: {e}, will fetch fresh data")
        
        if not use_cache:
            # Fetch fresh position data
            print("Fetching fresh position data from Stratz API...")
            fetch_position_data_from_api(cache_file)
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error fetching hero data: {e}")
        return False

def fetch_position_data_from_api(cache_file):
    """Fetch position data from Stratz API and cache it"""
    global HeroPositions
    
    # Fetch hero stats to get position information from Stratz API
    # Use correct schema from introspection: HeroStatsQuery.stats returns HeroPositionTimeDetailType
    try:
        # Stratz GraphQL API - query each position separately using positionIds filter
        stratz_query = """
        {
          pos1: heroStats {
            stats(bracketBasicIds: [DIVINE_IMMORTAL], positionIds: [POSITION_1]) {
              heroId
              matchCount
            }
          }
          pos2: heroStats {
            stats(bracketBasicIds: [DIVINE_IMMORTAL], positionIds: [POSITION_2]) {
              heroId
              matchCount
            }
          }
          pos3: heroStats {
            stats(bracketBasicIds: [DIVINE_IMMORTAL], positionIds: [POSITION_3]) {
              heroId
              matchCount
            }
          }
          pos4: heroStats {
            stats(bracketBasicIds: [DIVINE_IMMORTAL], positionIds: [POSITION_4]) {
              heroId
              matchCount
            }
          }
          pos5: heroStats {
            stats(bracketBasicIds: [DIVINE_IMMORTAL], positionIds: [POSITION_5]) {
              heroId
              matchCount
            }
          }
        }
        """
        
        stratz_response = requests.post(
            "https://api.stratz.com/graphql",
            json={"query": stratz_query},
            headers={
                "User-Agent": "STRATZ_API",
                "Authorization": f"Bearer {os.getenv('STRATZ_API_TOKEN')}"
            },
            timeout=15
        )
        
        if stratz_response.status_code == 200:
            stratz_data = stratz_response.json()
            
            # Debug: print response to see structure
            if 'errors' in stratz_data:
                print(f"Stratz API errors: {stratz_data['errors']}")
        if stratz_response.status_code == 200:
            stratz_data = stratz_response.json()
            
            # Debug: print response to see structure
            if 'errors' in stratz_data:
                print(f"Stratz API errors: {stratz_data['errors']}")
                raise Exception(f"Stratz API returned errors")
            
            # Debug: Print first part of response to understand structure  
            print(f"Stratz response keys: {stratz_data.get('data', {}).keys()}")
            
            if 'data' in stratz_data:
                # Process each position's data
                hero_positions_map = {}
                
                for pos_num in range(1, 6):
                    pos_key = f'pos{pos_num}'
                    if pos_key in stratz_data['data'] and 'stats' in stratz_data['data'][pos_key]:
                        for stat in stratz_data['data'][pos_key]['stats']:
                            hero_id = stat.get('heroId')
                            match_count = stat.get('matchCount', 0)
                            
                            if hero_id and match_count > 0:
                                if hero_id not in hero_positions_map:
                                    hero_positions_map[hero_id] = {}
                                hero_positions_map[hero_id][pos_num] = match_count
                
                print(f"Found position data for {len(hero_positions_map)} heroes")
                
                # Process each hero's positions
                for hero_id, positions_data in hero_positions_map.items():
                    # Calculate position percentages
                    total_matches = sum(positions_data.values())
                    
                    if total_matches > 100:  # Minimum matches threshold
                        position_percentages = []
                        for pos, matches in positions_data.items():
                            percentage = matches / total_matches
                            position_percentages.append((pos, percentage, matches))
                        
                        # Sort by percentage descending
                        position_percentages.sort(key=lambda x: x[1], reverse=True)
                        
                        viable_positions = []
                        for i, (pos, percentage, matches) in enumerate(position_percentages):
                            if percentage >= 0.20 or (i < 2 and percentage >= 0.10):
                                viable_positions.append(pos)
                        
                        HeroPositions[hero_id] = sorted(viable_positions)
                # Save to cache
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Stratz API (Divine+)',
                    'positions': {str(k): v for k, v in HeroPositions.items()}
                }
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                
                print(f"Loaded Stratz position data for {len([h for h in HeroPositions.values() if h])} heroes (Divine+ MMR)")
                print(f"Position data cached to {cache_file}")
            else:
                raise Exception("Unexpected Stratz API response format")
        else:
            error_text = stratz_response.text[:500]  # First 500 chars of error
            print(f"Stratz API HTTP {stratz_response.status_code}: {error_text}")
            raise Exception(f"Stratz API returned status {stratz_response.status_code}")
    
    except Exception as e:
        print(f"Warning: Could not fetch Stratz position data: {e}")
        print("Falling back to OpenDota heroStats...")
        
        # Fallback to OpenDota if Stratz fails
        try:
            stats_response = requests.get("https://api.opendota.com/api/heroStats", timeout=10)
            stats_response.raise_for_status()
            hero_stats = json.loads(stats_response.text)
        
            for hero in hero_stats:
                hero_id = hero['id']
                
                # OpenDota heroStats provides position data in '1_pick', '2_pick', etc.
                # Calculate which positions this hero is most picked for
                position_picks = {}
                for pos in range(1, 6):
                    pick_key = f'{pos}_pick'
                    if pick_key in hero:
                        position_picks[pos] = hero[pick_key]
                
                # Only include positions where hero has significant picks
                # Sort positions by pick count and only keep top positions
                if position_picks:
                    total_picks = sum(position_picks.values())
                    if total_picks > 0:
                        # Calculate percentage for each position
                        position_percentages = [(pos, picks / total_picks) for pos, picks in position_picks.items()]
                        # Sort by percentage descending
                        position_percentages.sort(key=lambda x: x[1], reverse=True)
                        
                        # Only keep positions with at least 20% of picks OR in top 2 positions
                        viable_positions = []
                        for i, (pos, percentage) in enumerate(position_percentages):
                            if percentage >= 0.20 or (i < 2 and percentage >= 0.10):
                                viable_positions.append(pos)
                        
                        # Store only the most viable positions, sorted by position number
                        HeroPositions[hero_id] = sorted(viable_positions)
                    else:
                        HeroPositions[hero_id] = []
                else:
                    HeroPositions[hero_id] = []
            
            # Save fallback data to cache
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'OpenDota API',
                'positions': {str(k): v for k, v in HeroPositions.items()}
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"Loaded position data for {len([h for h in HeroPositions.values() if h])} heroes (OpenDota)")
        
        except Exception as e:
            print(f"Warning: Could not fetch OpenDota data: {e}")
            # Final fallback: derive positions from roles
            for hero_id, roles in HeroRoles.items():
                positions = []
                if 'carry' in roles:
                    positions.append(1)
                if any(r in roles for r in ['nuker', 'disabler']):
                    positions.append(2)
                if any(r in roles for r in ['durable', 'initiator']):
                    positions.append(3)
                if 'support' in roles:
                    positions.extend([4, 5])
                HeroPositions[hero_id] = positions if positions else [1, 2, 3, 4, 5]
            
            # Save fallback data to cache
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'Role-based fallback',
                'positions': {str(k): v for k, v in HeroPositions.items()}
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"Loaded position data for {len([h for h in HeroPositions.values() if h])} heroes (role-based fallback)")

def get_hero_id(hero_name: str) -> int:
    """Convert hero name to ID with fuzzy matching and nickname support"""
    hero_lower = hero_name.lower().strip()
    
    # Check if it's a known nickname
    if hero_lower in HERO_NICKNAMES:
        hero_lower = HERO_NICKNAMES[hero_lower]
    
    # Try exact match first
    if hero_lower in NametoId:
        return NametoId[hero_lower]
    
    # Auto-generate abbreviations for multi-word heroes
    # e.g., "spirit breaker" → "sb", "phantom assassin" → "pa"
    if len(hero_lower) <= 4:  # Only for short inputs (likely abbreviations)
        for full_name, hero_id in NametoId.items():
            words = full_name.split()
            
            # Multi-word: Check first letter abbreviation (e.g., "sb" for "spirit breaker")
            if len(words) > 1:
                abbreviation = ''.join(word[0] for word in words)
                if hero_lower == abbreviation:
                    return hero_id
            
            # Single word: Check first N letters (e.g., "ring" for "ringmaster")
            if len(words) == 1:
                if len(hero_lower) >= 2 and full_name.startswith(hero_lower):
                    return hero_id
    
    # Try partial match - if input matches start of hero name
    for full_name, hero_id in NametoId.items():
        if full_name.startswith(hero_lower):
            return hero_id
    
    # Try if hero name contains the input (for short names)
    for full_name, hero_id in NametoId.items():
        if hero_lower in full_name:
            return hero_id
    
    return None

def get_matchup_data(hero_id: int, winpercent_key: str, exclude_ids: List[int]) -> List[Dict]:
    """Fetch matchup data for a hero and calculate win percentages"""
    try:
        matchup_url = f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
        response = requests.get(matchup_url, timeout=10)
        response.raise_for_status()
        matchup_data = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        return []
    
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

def filter_heroes_by_position(heroes_data: List[Dict], position: int = None) -> List[Dict]:
    """Filter counter heroes by position/role using OpenDota position data"""
    if position is None:
        return heroes_data
    
    filtered = []
    for hero in heroes_data:
        hero_id = hero['hero_id']
        viable_positions = HeroPositions.get(hero_id, [])
        
        # Only include heroes that can play the requested position
        if position in viable_positions:
            filtered.append(hero)
    
    return filtered
    return filtered

def parse_position_from_text(text: str) -> int:
    """Extract position number from text"""
    text_lower = text.lower()
    for pos, keywords in HERO_POSITIONS.items():
        if any(keyword in text_lower for keyword in keywords):
            return pos
    return None

def calculate_counters(hero_names: List[str]) -> tuple:
    """Calculate best counter heroes for given enemy team"""
    # Validate all hero names
    hero_ids = []
    for name in hero_names:
        hero_id = get_hero_id(name)
        if hero_id is None:
            return None, f"Hero '{name}' not found!"
        hero_ids.append(hero_id)
    
    # Get matchup data for all heroes
    matchup_lists = []
    for i, hero_id in enumerate(hero_ids, 1):
        matchups = get_matchup_data(hero_id, f'winpercent{i}', hero_ids)
        if not matchups:
            return None, f"Failed to fetch matchup data for {hero_names[i-1]}"
        matchup_lists.append(matchups)
    
    # Merge all matchup data
    matchup_dict = {}
    
    for i, matchups in enumerate(matchup_lists, 1):
        for item in matchups:
            hero_id = item['hero_id']
            if hero_id not in matchup_dict:
                matchup_dict[hero_id] = {'hero_id': hero_id}
            matchup_dict[hero_id][f'winpercent{i}'] = item[f'winpercent{i}']
    
    # Only include heroes with data for all matchups
    complete_matchups = [
        data for data in matchup_dict.values()
        if all(f'winpercent{i}' in data for i in range(1, len(hero_ids) + 1))
    ]
    
    # Calculate geometric mean (balanced effectiveness measure)
    for hero in complete_matchups:
        winrates = [hero[f'winpercent{i}'] for i in range(1, len(hero_ids) + 1)]
        # Geometric mean: nth root of product
        product = 1
        for wr in winrates:
            product *= wr
        hero['geo_mean'] = product ** (1.0 / len(winrates))
        hero['avg_winrate'] = sum(winrates) / len(winrates)
        hero['winrates'] = winrates
    
    # Sort by geometric mean (descending)
    sorted_counters = sorted(complete_matchups, key=lambda x: x['geo_mean'], reverse=True)
    
    return sorted_counters, None

@bot.event
async def on_ready():
    """Called when bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    if fetch_hero_data():
        print(f'✓ Successfully loaded all hero data')
        print(f'✓ Total heroes: {len(hero_data)}')
        print(f'✓ Heroes with position data: {len([h for h in HeroPositions.values() if h])}')
    else:
        print('Warning: Failed to load hero data')
    
    # Sync slash commands
    try:
        guild_id = os.getenv('GUILD_ID')
        if guild_id:
            # Sync to specific guild for instant update
            guild = discord.Object(id=int(guild_id))
            tree.copy_global_to(guild=guild)
            synced = await tree.sync(guild=guild)
            print(f'Synced {len(synced)} slash commands to guild {guild_id}')
        else:
            # Sync globally (takes up to 1 hour)
            synced = await tree.sync()
            print(f'Synced {len(synced)} slash commands globally')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    """Listen for keywords in messages"""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    content = message.content.lower()
    
    # Check if message contains "cheesepick" - just reply "yep"
    if 'cheesepick' in content:
        await message.reply("yep")
        return
    
    # Debug command via text
    if content.startswith('debug '):
        hero_name = message.content[6:].strip()  # Get text after "debug "
        hero_id = get_hero_id(hero_name)
        
        if hero_id:
            positions = HeroPositions.get(hero_id, [])
            roles = HeroRoles.get(hero_id, [])
            full_name = IdtoName.get(hero_id)
            
            result = f"**{full_name}**\n"
            result += f"**Viable positions:** {positions if positions else 'None loaded'}\n"
            result += f"**Roles:** {', '.join(roles) if roles else 'None'}"
            await message.reply(result)
        else:
            await message.reply(f"❌ Could not find hero: `{hero_name}`")
        return
    
    # Check for other counter keywords
    if any(keyword in content for keyword in ['counter pick', 'counter', 'best pick']):
        # Check for position filter
        position = parse_position_from_text(content)
        
        # Try to extract hero names from the message
        # Remove common words that aren't heroes
        stop_words = ['counter', 'pick', 'best', 'against', 'vs', 'versus', 'the', 'a', 'an', 'for', 
                     'position', 'pos', 'role', 'carry', 'mid', 'offlane', 'support', 'hard', 'soft',
                     'safelane', 'safe', 'lane', 'midlane', 'roamer']
        
        # First try quoted strings
        quoted_pattern = r'"([^"]+)"'
        quoted_heroes = re.findall(quoted_pattern, content)
        
        # Then get remaining words
        remaining_text = re.sub(quoted_pattern, '', content)
        words = remaining_text.split()
        
        # Combine quoted heroes and individual words
        potential_names = quoted_heroes + [w.strip('.,!?:;') for w in words if w.lower() not in stop_words]
        
        # Find valid heroes with fuzzy matching
        heroes = []
        matched_names = []
        for name in potential_names:
            name = name.strip()
            if len(name) < 2:  # Skip single letters only
                continue
            hero_id = get_hero_id(name)
            if hero_id and hero_id not in [get_hero_id(h) for h in heroes]:  # Avoid duplicates
                # Get the full hero name for display
                full_name = IdtoName[hero_id]
                heroes.append(full_name)
                matched_names.append(f"{name} → {full_name}")
        
        # If we found 4 heroes, process the counter request
        if len(heroes) == 4:
            await message.add_reaction('🔍')
            
            counters, error = calculate_counters(heroes)
            
            if error:
                await message.reply(f"❌ {error}")
                return
            
            # Apply position filter if specified
            if position:
                counters = filter_heroes_by_position(counters, position)
                if not counters:
                    await message.reply(f"❌ No position {position} heroes found as counters!")
                    return
            
            # Build response embed
            position_text = f" (Position {position})" if position else ""
            embed = discord.Embed(
                title=f"🎯 Best Counter Heroes{position_text}",
                description=f"Against: **{', '.join(heroes)}**",
                color=discord.Color.blue()
            )
            
            # Add top 10 counters
            for rank, hero in enumerate(counters[:10], 1):
                hero_name = IdtoName[hero['hero_id']]
                geo_mean = hero['geo_mean']
                avg_wr = hero['avg_winrate']
                
                # Create winrate breakdown
                wr_text = " | ".join([f"{wr:.1f}%" for wr in hero['winrates']])
                
                # Add role info
                roles = HeroRoles.get(hero['hero_id'], [])
                role_text = f" ({', '.join(roles[:3])})" if roles else ""
                
                embed.add_field(
                    name=f"{rank}. {hero_name}{role_text}",
                    value=f"📊 GM: **{geo_mean:.1f}%** (Avg: {avg_wr:.1f}%)\n`{wr_text}`",
                    inline=False
                )
            
            embed.set_footer(text="Data from OpenDota API")
            
            await message.reply(embed=embed)
        elif len(heroes) > 0:
            matched_info = "\n".join(f"• {m}" for m in matched_names)
            position_info = f"\n**Position filter:** {position}" if position else ""
            await message.reply(f"🤔 I found {len(heroes)} hero(s), but I need exactly 4 heroes to find counters!\n\n"
                               f"**Matched:**\n{matched_info}{position_info}\n\n"
                               f"Try: `counter \"Anti-Mage\" Invoker Pudge \"Crystal Maiden\"`")
        else:
            # No heroes found - show help
            await message.reply(f"🎮 **Counter Pick Help**\n\n"
                               f"Please provide 4 enemy heroes.\n\n"
                               f"**Examples:**\n"
                               f"• `counter anti-mage invoker pudge crystal maiden`\n"
                               f"• `counter am qop pa sf`\n"
                               f"• `counter pos1 anti-mage invoker pudge cm` (filter by position)\n\n"
                               f"Use quotes for multi-word heroes: `counter \"Anti-Mage\" Invoker Pudge \"Crystal Maiden\"`")

@tree.command(name='counter', description='Find best counter heroes against enemy team')
@app_commands.describe(
    hero1='First enemy hero',
    hero2='Second enemy hero',
    hero3='Third enemy hero',
    hero4='Fourth enemy hero',
    position='Filter by position (1=Carry, 2=Mid, 3=Offlane, 4=Soft Support, 5=Hard Support)'
)
async def counter(interaction: discord.Interaction, hero1: str, hero2: str, hero3: str, hero4: str, position: int = None):
    """Slash command to find counter heroes"""
    await interaction.response.defer()
    
    heroes = [hero1, hero2, hero3, hero4]
    
    # Validate position
    if position and (position < 1 or position > 5):
        await interaction.followup.send("❌ Position must be between 1 and 5!")
        return
    
    # Calculate counters
    counters, error = calculate_counters(heroes)
    
    if error:
        await interaction.followup.send(f"❌ {error}")
        return
    
    # Apply position filter if specified
    if position:
        counters = filter_heroes_by_position(counters, position)
        if not counters:
            await interaction.followup.send(f"❌ No position {position} heroes found as counters!")
            return
    
    # Build response embed
    position_text = f" (Position {position})" if position else ""
    embed = discord.Embed(
        title=f"🎯 Best Counter Heroes{position_text}",
        description=f"Against: **{', '.join(heroes)}**",
        color=discord.Color.blue()
    )
    
    # Add top 10 counters
    for rank, hero in enumerate(counters[:10], 1):
        hero_name = IdtoName[hero['hero_id']]
        geo_mean = hero['geo_mean']
        avg_wr = hero['avg_winrate']
        
        # Create winrate breakdown
        wr_text = " | ".join([f"{wr:.1f}%" for wr in hero['winrates']])
        
        # Add role info
        roles = HeroRoles.get(hero['hero_id'], [])
        role_text = f" ({', '.join(roles[:3])})" if roles else ""
        
        embed.add_field(
            name=f"{rank}. {hero_name}{role_text}",
            value=f"📊 GM: **{geo_mean:.1f}%** (Avg: {avg_wr:.1f}%)\n`{wr_text}`",
            inline=False
        )
    
    embed.set_footer(text="Data from OpenDota API")
    
    await interaction.followup.send(embed=embed)

@tree.command(name='heroes', description='List all available heroes or search for specific ones')
@app_commands.describe(search='Search term to filter heroes (optional)')
async def heroes(interaction: discord.Interaction, search: str = None):
    """Slash command to list heroes"""
    if not IdtoName:
        await interaction.response.send_message("❌ Hero data not loaded yet. Please try again.")
        return
    
    hero_list = list(IdtoName.values())
    
    if search:
        hero_list = [h for h in hero_list if search.lower() in h.lower()]
        if not hero_list:
            await interaction.response.send_message(f"❌ No heroes found matching '{search}'")
            return
    
    # Show first 50 heroes
    display_list = sorted(hero_list)[:50]
    
    embed = discord.Embed(
        title=f"🦸 Dota 2 Heroes ({len(hero_list)} total)",
        description=", ".join(display_list),
        color=discord.Color.green()
    )
    
    if len(hero_list) > 50:
        embed.set_footer(text=f"Showing first 50 of {len(hero_list)} heroes")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name='debug', description='Debug hero name lookup and positions')
@app_commands.describe(search='Hero name to search for')
async def debug(interaction: discord.Interaction, search: str):
    """Debug command to see how hero names are stored and their positions"""
    search_lower = search.lower()
    
    # Check nickname
    nickname_result = HERO_NICKNAMES.get(search_lower, "Not in nicknames")
    
    # Check if in NametoId
    exact_match = NametoId.get(search_lower)
    
    # Find partial matches
    partial_matches = [name for name in NametoId.keys() if search_lower in name][:5]
    
    # Get position info
    hero_id = get_hero_id(search)
    positions = HeroPositions.get(hero_id, []) if hero_id else []
    roles = HeroRoles.get(hero_id, []) if hero_id else []
    
    result = f"**Search:** `{search}`\n\n"
    result += f"**Nickname lookup:** {nickname_result}\n\n"
    result += f"**Exact match:** {IdtoName.get(exact_match, 'None')}\n\n"
    result += f"**Partial matches:** {', '.join(partial_matches) if partial_matches else 'None'}\n\n"
    result += f"**get_hero_id result:** {IdtoName.get(hero_id, 'None')}\n\n"
    result += f"**Viable positions:** {positions if positions else 'None'}\n"
    result += f"**Roles:** {', '.join(roles) if roles else 'None'}"
    
    await interaction.response.send_message(result)

@tree.command(name='ping', description='Check bot latency and status')
async def ping(interaction: discord.Interaction):
    """Slash command to check bot status"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

@tree.command(name='help', description='Show bot usage instructions')
async def help_command(interaction: discord.Interaction):
    """Show detailed bot usage instructions"""
    embed = discord.Embed(
        title="🧀 Cheesepicker Bot Help",
        description="Find the best Dota 2 hero counters against enemy teams!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="📌 /counter",
        value="Find best counters against 4 enemy heroes\n"
              "**Usage:** `/counter hero1 hero2 hero3 hero4`\n"
              "**Example:** `/counter hero1:Anti-Mage hero2:Invoker hero3:Pudge hero4:Crystal Maiden`",
        inline=False
    )
    
    embed.add_field(
        name="📌 /heroes",
        value="List all available heroes or search\n"
              "**Usage:** `/heroes [search:term]`\n"
              "**Example:** `/heroes search:spirit`",
        inline=False
    )
    
    embed.add_field(
        name="📌 /ping",
        value="Check bot responsiveness",
        inline=False
    )
    
    embed.add_field(
        name="💬 Natural Language",
        value="Just mention keywords like 'cheesepick' or 'counter' with hero names!\n"
              "**Example:** `cheesepick against \"Anti-Mage\" Invoker Pudge \"Crystal Maiden\"`",
        inline=False
    )
    
    embed.set_footer(text="Data provided by OpenDota API")
    
    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    # Get token from environment variable
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please set your bot token in .env file")
        exit(1)
    
    bot.run(TOKEN)
