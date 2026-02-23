import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
import random
import math


# COLOUR palette
COLOUR_MAIN_BG = "#1A1A1A"
COLOUR_PANEL_BG = "#2D2D2D"
COLOUR_THREAT_HIGHLIGHT = "#FF4C4C"
COLOUR_TOOL_HIGHLIGHT = "#4C8BFF"
COLOUR_SHOP_SECTION = "#3B3B3B"
COLOUR_TEXT_PRIMARY = "#FFFFFF"
COLOUR_TEXT_SECONDARY = "#C7C7C7"
COLOUR_HP_BAR = "#00FF00"
COLOUR_BUTTON_SCAN = "#0066CC"
COLOUR_BUTTON_USE_TOOL = "#CC6600"
COLOUR_BUTTON_NEXT_TURN = "#006600"
COLOUR_BUTTON_SAVE = "#660066"
COLOUR_BUTTON_LOAD = "#666600"
COLOUR_BUTTON_HS = "#CC0066"


class ThreatType:
    VIRUS = "Virus"
    WORM = "Worm"
    TROJAN = "Trojan"
    RANSOMWARE = "Ransomware"
    DDOS = "DDoS Attack"
    SPYWARE = "Spyware"
    ZERO_DAY = "Zero-Day Exploit"
    BOTNET = "Botnet"
    PHISHING = "Phishing Attack"
    MALWARE_DROPPER = "Malware Dropper"
    DATA_BREACH = "Data Breach"
    BRUTE_FORCE = "Brute Force Attack"
    MITM = "MITM"
    SOCIAL_ENGINEERING = "Social Engineering Attack"
    SQL_INJECTION = "SQL Injection Attack"
    KEYLOGGER = "Keylogger"
    BOT_COMMANDER = "Bot Commander"


class ToolType:
    BASIC_FIREWALL = "Basic Firewall"
    ADVANCED_FIREWALL = "Advanced Firewall"
    ANTIVIRUS_SCANNER = "Antivirus Scanner"
    HEURISTIC_ANTIVIRUS = "Heuristic Antivirus"
    BACKUP_SYSTEM = "Backup System"
    IDS = "IDS"
    IPS = "IPS"
    ENCRYPTION_MODULE = "Encryption Module"
    EMAIL_FILTER = "Email Filter"
    SANDBOX_ENVIRONMENT = "Sandbox Environment"
    HONEYPOT = "Honeypot"
    BEHAVIOURAL_MONITORING = "Behavioural Monitoring"
    ANTI_BOTNET_TOOL = "Anti-Botnet Tool"
    PORT_SCANNER = "Port Scanner"
    VPN_SECURITY_LAYER = "VPN Security Layer"
    CLOUD_SHIELD = "Cloud Shield"


class Threat:
    def __init__(self, threat_type, hp, max_hp, attack, special_active=False, turns_alive=0, detection_chance=1.0):
        self.type = threat_type
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.special_active = special_active
        self.turns_alive = turns_alive
        self.detection_chance = detection_chance


class Tool:
    def __init__(self, tool_type, effectiveness, cost, owned=False):
        self.type = tool_type
        self.effectiveness = effectiveness
        self.cost = cost
        self.owned = owned


class GameState:
    def __init__(self):
        self.server_hp = 100
        self.max_server_hp = 100
        self.points = 50
        self.score = 0
        self.turn = 1
        self.active_threats = []
        self.owned_tools = []
        self.game_over = False
        self.points_multiplier = 1.0
        self.tool_effectiveness_multiplier = 1.0
        self.shop_price_multiplier = 1.0
        self.botnet_buff = 0
        self.scans_this_turn = 0
        self.tools_used_this_turn = 0
        self.purchases_this_turn = 0


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('cybersecurity_game.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS game_saves
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           save_name
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           game_data
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS high_scores
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           player_name
                           TEXT
                           NOT
                           NULL,
                           score
                           INTEGER
                           NOT
                           NULL,
                           turns_survived
                           INTEGER
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        self.conn.commit()

    def save_game(self, save_name, game_state):
        cursor = self.conn.cursor()
        game_data = {
            'server_hp': game_state.server_hp,
            'max_server_hp': game_state.max_server_hp,
            'points': game_state.points,
            'score': game_state.score,
            'turn': game_state.turn,
            'active_threats': [self.threat_to_dict(threat) for threat in game_state.active_threats],
            'owned_tools': game_state.owned_tools,
            'game_over': game_state.game_over,
            'points_multiplier': game_state.points_multiplier,
            'tool_effectiveness_multiplier': game_state.tool_effectiveness_multiplier,
            'shop_price_multiplier': game_state.shop_price_multiplier,
            'botnet_buff': game_state.botnet_buff
        }

        cursor.execute('''
            INSERT OR REPLACE INTO game_saves (save_name, game_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (save_name, json.dumps(game_data)))
        self.conn.commit()
        return True

    def threat_to_dict(self, threat):
        return {
            'type': threat.type,
            'hp': threat.hp,
            'max_hp': threat.max_hp,
            'attack': threat.attack,
            'special_active': threat.special_active,
            'turns_alive': threat.turns_alive,
            'detection_chance': threat.detection_chance
        }

    def load_game(self, save_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT game_data FROM game_saves WHERE save_name = ?', (save_name,))
        result = cursor.fetchone()

        if result:
            game_data = json.loads(result[0])
            game_state = GameState()
            game_state.server_hp = game_data['server_hp']
            game_state.max_server_hp = game_data['max_server_hp']
            game_state.points = game_data['points']
            game_state.score = game_data['score']
            game_state.turn = game_data['turn']
            game_state.game_over = game_data['game_over']
            game_state.points_multiplier = game_data.get('points_multiplier', 1.0)
            game_state.tool_effectiveness_multiplier = game_data.get('tool_effectiveness_multiplier', 1.0)
            game_state.shop_price_multiplier = game_data.get('shop_price_multiplier', 1.0)
            game_state.botnet_buff = game_data.get('botnet_buff', 0)

            # Reconstruct threats
            for threat_data in game_data['active_threats']:
                threat = Threat(
                    threat_data['type'],
                    threat_data['hp'],
                    threat_data['max_hp'],
                    threat_data['attack'],
                    threat_data.get('special_active', False),
                    threat_data.get('turns_alive', 0),
                    threat_data.get('detection_chance', 1.0)
                )
                game_state.active_threats.append(threat)

            # Reconstruct owned tools
            game_state.owned_tools = game_data['owned_tools']

            return game_state
        return None

    def get_save_names(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT save_name FROM game_saves ORDER BY updated_at DESC')
        return [row[0] for row in cursor.fetchall()]

    def save_high_score(self, player_name, score, turns):
        cursor = self.conn.cursor()
        cursor.execute('''
                       INSERT INTO high_scores (player_name, score, turns_survived)
                       VALUES (?, ?, ?)
                       ''', (player_name, score, turns))
        self.conn.commit()

    def get_high_scores(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('''
                       SELECT player_name, score, turns_survived, created_at
                       FROM high_scores
                       ORDER BY score DESC LIMIT ?
                       ''', (limit,))
        return cursor.fetchall()


class Game:
    def __init__(self):
        self.db = DatabaseManager()
        self.game_state = GameState()
        self.tools_data = self.initialise_tools()
        self.threat_weights = self.initialise_threat_weights()

    def initialise_tools(self):
        tools = {}

        # Basic Firewall
        tools[ToolType.BASIC_FIREWALL] = Tool(
            ToolType.BASIC_FIREWALL,
            {ThreatType.VIRUS: 0.5, ThreatType.WORM: 0.2, ThreatType.DDOS: 1.0},
            10
        )

        # Advanced Firewall
        tools[ToolType.ADVANCED_FIREWALL] = Tool(
            ToolType.ADVANCED_FIREWALL,
            {ThreatType.VIRUS: 0.8, ThreatType.WORM: 0.4, ThreatType.DDOS: 1.2},
            20
        )

        # Antivirus Scanner
        tools[ToolType.ANTIVIRUS_SCANNER] = Tool(
            ToolType.ANTIVIRUS_SCANNER,
            {ThreatType.VIRUS: 1.0, ThreatType.TROJAN: 1.0, ThreatType.WORM: 0.6},
            15
        )

        # Heuristic Antivirus
        tools[ToolType.HEURISTIC_ANTIVIRUS] = Tool(
            ToolType.HEURISTIC_ANTIVIRUS,
            {ThreatType.VIRUS: 1.2, ThreatType.TROJAN: 0.8, ThreatType.WORM: 0.8, ThreatType.ZERO_DAY: 0.4},
            25
        )

        # Backup System
        tools[ToolType.BACKUP_SYSTEM] = Tool(
            ToolType.BACKUP_SYSTEM,
            {ThreatType.RANSOMWARE: 1.2, ThreatType.TROJAN: 0.5, ThreatType.VIRUS: 0.3},
            20
        )

        # Intrusion Detection System
        all_threats = [ThreatType.VIRUS, ThreatType.WORM, ThreatType.TROJAN, ThreatType.RANSOMWARE,
                       ThreatType.DDOS, ThreatType.SPYWARE, ThreatType.ZERO_DAY, ThreatType.BOTNET,
                       ThreatType.PHISHING, ThreatType.MALWARE_DROPPER, ThreatType.DATA_BREACH,
                       ThreatType.BRUTE_FORCE, ThreatType.MITM, ThreatType.SOCIAL_ENGINEERING,
                       ThreatType.SQL_INJECTION, ThreatType.KEYLOGGER, ThreatType.BOT_COMMANDER]

        ids_effectiveness = {}
        for threat in all_threats:
            ids_effectiveness[threat] = 0.3

        tools[ToolType.IDS] = Tool(
            ToolType.IDS,
            ids_effectiveness,
            15
        )

        # Intrusion Prevention System
        tools[ToolType.IPS] = Tool(
            ToolType.IPS,
            {ThreatType.DDOS: 1.3, ThreatType.BRUTE_FORCE: 1.0, ThreatType.WORM: 0.6},
            30
        )

        # Encryption Module
        tools[ToolType.ENCRYPTION_MODULE] = Tool(
            ToolType.ENCRYPTION_MODULE,
            {ThreatType.DATA_BREACH: 1.2, ThreatType.SPYWARE: 1.0},
            20
        )

        # Email Filter
        tools[ToolType.EMAIL_FILTER] = Tool(
            ToolType.EMAIL_FILTER,
            {ThreatType.PHISHING: 1.3, ThreatType.TROJAN: 0.3},
            12
        )

        # Sandbox Environment
        tools[ToolType.SANDBOX_ENVIRONMENT] = Tool(
            ToolType.SANDBOX_ENVIRONMENT,
            {ThreatType.ZERO_DAY: 1.0, ThreatType.VIRUS: 0.5},
            30
        )

        # Honeypot
        tools[ToolType.HONEYPOT] = Tool(
            ToolType.HONEYPOT,
            {ThreatType.RANSOMWARE: 0.5, ThreatType.WORM: 1.0, ThreatType.BOTNET: 0.7},
            18
        )

        # Behavioural Monitoring
        tools[ToolType.BEHAVIOURAL_MONITORING] = Tool(
            ToolType.BEHAVIOURAL_MONITORING,
            {ThreatType.SPYWARE: 1.3, ThreatType.TROJAN: 0.8},
            18
        )

        # Anti-Botnet Tool
        tools[ToolType.ANTI_BOTNET_TOOL] = Tool(
            ToolType.ANTI_BOTNET_TOOL,
            {ThreatType.BOTNET: 1.4, ThreatType.DDOS: 0.8},
            25
        )

        # Port Scanner
        tools[ToolType.PORT_SCANNER] = Tool(
            ToolType.PORT_SCANNER,
            {ThreatType.BRUTE_FORCE: 0.9, ThreatType.WORM: 0.4},
            10
        )

        # VPN Security Layer
        tools[ToolType.VPN_SECURITY_LAYER] = Tool(
            ToolType.VPN_SECURITY_LAYER,
            {ThreatType.DATA_BREACH: 0.9, ThreatType.MITM: 1.2},
            25
        )

        # Cloud Shield
        tools[ToolType.CLOUD_SHIELD] = Tool(
            ToolType.CLOUD_SHIELD,
            {ThreatType.DDOS: 1.4, ThreatType.BOTNET: 1.0},
            30
        )

        return tools

    def initialise_threat_weights(self):
        return {
            ThreatType.VIRUS: 1.0,
            ThreatType.WORM: 0.8,
            ThreatType.TROJAN: 0.9,
            ThreatType.RANSOMWARE: 0.6,
            ThreatType.DDOS: 0.7,
            ThreatType.SPYWARE: 0.8,
            ThreatType.ZERO_DAY: 0.3,
            ThreatType.BOTNET: 0.5,
            ThreatType.PHISHING: 0.9,
            ThreatType.MALWARE_DROPPER: 0.6,
            ThreatType.DATA_BREACH: 0.4,
            ThreatType.BRUTE_FORCE: 0.7,
            ThreatType.MITM: 0.5,
            ThreatType.SOCIAL_ENGINEERING: 0.4,
            ThreatType.SQL_INJECTION: 0.6,
            ThreatType.KEYLOGGER: 0.7,
            ThreatType.BOT_COMMANDER: 0.2
        }

    def generate_threats(self):
        threat_count = min(1 + self.game_state.turn // 3, 4)
        threats = []

        for i in range(threat_count):
            # Weighted random selection
            threat_types = list(self.threat_weights.keys())
            weights = list(self.threat_weights.values())
            threat_type = self.weighted_choice(threat_types, weights)

            base_hp = 15 + (self.game_state.turn * 2)
            base_attack = 5 + self.game_state.turn

            # Apply botnet buff if applicable
            if threat_type == ThreatType.BOTNET:
                base_hp += self.game_state.botnet_buff * 5
                base_attack += self.game_state.botnet_buff * 2

            threat = Threat(
                threat_type,
                base_hp,
                base_hp,
                base_attack
            )

            # Special properties
            if threat_type == ThreatType.TROJAN:
                threat.detection_chance = 0.7

            threats.append(threat)

        return threats

    def weighted_choice(self, choices, weights):
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in zip(choices, weights):
            if upto + weight >= r:
                return choice
            upto += weight
        return choices[-1]

    def use_tool(self, tool_type, target_threat):
        if tool_type not in self.game_state.owned_tools:
            return {"error": "Tool not owned"}

        tool = self.tools_data[tool_type]
        effectiveness = tool.effectiveness.get(target_threat.type, 0.1)
        effectiveness *= self.game_state.tool_effectiveness_multiplier

        # Calculate damage
        base_damage = 20
        damage = int(base_damage * effectiveness)

        # Apply damage
        target_threat.hp = max(0, target_threat.hp - damage)

        result = {
            "damage": damage,
            "threat_defeated": target_threat.hp <= 0,
            "effectiveness": effectiveness
        }

        return result

    def process_threat_specials(self):
        """Process special abilities of threats"""
        new_threats = []

        for threat in self.game_state.active_threats[:]:
            threat.turns_alive += 1

            # Virus: Splits into 2 if ignored for 3 turns
            if (threat.type == ThreatType.VIRUS and
                    threat.turns_alive >= 3 and not threat.special_active):
                new_virus = Threat(ThreatType.VIRUS, threat.hp // 2, threat.max_hp // 2, threat.attack // 2)
                new_threats.append(new_virus)
                threat.special_active = True

            # Brute Force: Damage increases over time
            elif threat.type == ThreatType.BRUTE_FORCE:
                threat.attack += 2

            # Ransomware: Doubles damage if not stopped within 2 turns
            elif (threat.type == ThreatType.RANSOMWARE and
                  threat.turns_alive >= 2 and not threat.special_active):
                threat.attack *= 2
                threat.special_active = True

        self.game_state.active_threats.extend(new_threats)

    def process_threat_attacks(self):
        """Process threat attacks and special effects"""
        total_damage = 0

        for threat in self.game_state.active_threats:
            if threat.type == ThreatType.WORM:
                # Attacks twice
                total_damage += threat.attack * 2
            elif threat.type == ThreatType.DDOS:
                # Ignores weak firewalls (simplified: just does full damage)
                total_damage += threat.attack
            else:
                total_damage += threat.attack

            # Special effects
            if threat.type == ThreatType.SPYWARE:
                self.game_state.points_multiplier *= 0.95
            elif threat.type == ThreatType.DATA_BREACH:
                self.game_state.max_server_hp = max(10, self.game_state.max_server_hp - 2)
            elif threat.type == ThreatType.MITM:
                self.game_state.tool_effectiveness_multiplier *= 0.98
            elif threat.type == ThreatType.SOCIAL_ENGINEERING:
                self.game_state.shop_price_multiplier *= 1.02
            elif threat.type == ThreatType.KEYLOGGER:
                self.game_state.points_multiplier *= 0.97
            elif threat.type == ThreatType.BOT_COMMANDER:
                self.game_state.botnet_buff += 1

        self.game_state.server_hp = max(0, self.game_state.server_hp - total_damage)

        if self.game_state.server_hp <= 0:
            self.game_state.game_over = True

    def process_defeated_threats(self):
        """Process effects when threats are defeated"""
        points_earned = 0
        new_threats = []

        for threat in self.game_state.active_threats[:]:
            if threat.hp <= 0:
                # Base points for defeating threat
                base_points = 10 + (self.game_state.turn * 2)
                points_earned += int(base_points * self.game_state.points_multiplier)

                # Special death effects
                if threat.type == ThreatType.MALWARE_DROPPER:
                    # Spawns another threat
                    threat_types = list(self.threat_weights.keys())
                    new_threat_type = random.choice(threat_types)
                    new_threat = Threat(
                        new_threat_type,
                        10,
                        10,
                        5
                    )
                    new_threats.append(new_threat)

                self.game_state.active_threats.remove(threat)

        self.game_state.active_threats.extend(new_threats)
        self.game_state.points += points_earned
        self.game_state.score += points_earned

        return points_earned

    def buy_tool(self, tool_type):
        tool = self.tools_data[tool_type]
        cost = int(tool.cost * self.game_state.shop_price_multiplier)

        if self.game_state.points >= cost and tool_type not in self.game_state.owned_tools:
            self.game_state.points -= cost
            self.game_state.owned_tools.append(tool_type)
            return True
        return False

    def next_turn(self):
        self.game_state.turn += 1
        self.game_state.scans_this_turn = 0
        self.game_state.tools_used_this_turn = 0
        self.process_threat_specials()


class GameGUI:
    def __init__(self, username):
        self.username = username  # store username
        self.game = Game()
        self.root = tk.Tk()
        self.root.title(f"Cybersecurity Defence Game - {self.username}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')

        self.selected_tool = None
        self.selected_threat = None

        self.setup_ui()
        self.update_display()

    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
    import sqlite3
    import json
    import random
    import math

    # COLOUR palette
    COLOUR_MAIN_BG = "#1A1A1A"
    COLOUR_PANEL_BG = "#2D2D2D"
    COLOUR_THREAT_HIGHLIGHT = "#FF4C4C"
    COLOUR_TOOL_HIGHLIGHT = "#4C8BFF"
    COLOUR_SHOP_SECTION = "#3B3B3B"
    COLOUR_TEXT_PRIMARY = "#FFFFFF"
    COLOUR_TEXT_SECONDARY = "#C7C7C7"
    COLOUR_HP_BAR = "#00FF00"
    COLOUR_BUTTON_SCAN = "#0066CC"
    COLOUR_BUTTON_USE_TOOL = "#CC6600"
    COLOUR_BUTTON_NEXT_TURN = "#006600"
    COLOUR_BUTTON_SAVE = "#660066"
    COLOUR_BUTTON_LOAD = "#666600"
    COLOUR_BUTTON_HS = "#CC0066"

    class ThreatType:
        VIRUS = "Virus"
        WORM = "Worm"
        TROJAN = "Trojan"
        RANSOMWARE = "Ransomware"
        DDOS = "DDoS Attack"
        SPYWARE = "Spyware"
        ZERO_DAY = "Zero-Day Exploit"
        BOTNET = "Botnet"
        PHISHING = "Phishing Attack"
        MALWARE_DROPPER = "Malware Dropper"
        DATA_BREACH = "Data Breach"
        BRUTE_FORCE = "Brute Force Attack"
        MITM = "MITM"
        SOCIAL_ENGINEERING = "Social Engineering Attack"
        SQL_INJECTION = "SQL Injection Attack"
        KEYLOGGER = "Keylogger"
        BOT_COMMANDER = "Bot Commander"

    class ToolType:
        BASIC_FIREWALL = "Basic Firewall"
        ADVANCED_FIREWALL = "Advanced Firewall"
        ANTIVIRUS_SCANNER = "Antivirus Scanner"
        HEURISTIC_ANTIVIRUS = "Heuristic Antivirus"
        BACKUP_SYSTEM = "Backup System"
        IDS = "IDS"
        IPS = "IPS"
        ENCRYPTION_MODULE = "Encryption Module"
        EMAIL_FILTER = "Email Filter"
        SANDBOX_ENVIRONMENT = "Sandbox Environment"
        HONEYPOT = "Honeypot"
        BEHAVIOURAL_MONITORING = "Behavioural Monitoring"
        ANTI_BOTNET_TOOL = "Anti-Botnet Tool"
        PORT_SCANNER = "Port Scanner"
        VPN_SECURITY_LAYER = "VPN Security Layer"
        CLOUD_SHIELD = "Cloud Shield"

    class Threat:
        def __init__(self, threat_type, hp, max_hp, attack, special_active=False, turns_alive=0, detection_chance=1.0):
            self.type = threat_type
            self.hp = hp
            self.max_hp = max_hp
            self.attack = attack
            self.special_active = special_active
            self.turns_alive = turns_alive
            self.detection_chance = detection_chance

    class Tool:
        def __init__(self, tool_type, effectiveness, cost, owned=False):
            self.type = tool_type
            self.effectiveness = effectiveness
            self.cost = cost
            self.owned = owned

    class GameState:
        def __init__(self):
            self.server_hp = 100
            self.max_server_hp = 100
            self.points = 50
            self.score = 0
            self.turn = 1
            self.active_threats = []
            self.owned_tools = []
            self.game_over = False
            self.points_multiplier = 1.0
            self.tool_effectiveness_multiplier = 1.0
            self.shop_price_multiplier = 1.0
            self.botnet_buff = 0
            self.scans_this_turn = 0
            self.tools_used_this_turn = 0
            self.purchases_this_turn = 0

    class DatabaseManager:
        def __init__(self):
            self.conn = sqlite3.connect('cybersecurity_game.db')
            self.create_tables()

        def create_tables(self):
            cursor = self.conn.cursor()
            cursor.execute('''...''')  # same as original

            cursor.execute('''...''')  # same as original
            self.conn.commit()

        def save_game(self, save_name, game_state):
            cursor = self.conn.cursor()
            game_data = {
                'server_hp': game_state.server_hp,
                'max_server_hp': game_state.max_server_hp,
                'points': game_state.points,
                'score': game_state.score,
                'turn': game_state.turn,
                'active_threats': [self.threat_to_dict(threat) for threat in game_state.active_threats],
                'owned_tools': game_state.owned_tools,
                'game_over': game_state.game_over,
                'points_multiplier': game_state.points_multiplier,
                'tool_effectiveness_multiplier': game_state.tool_effectiveness_multiplier,
                'shop_price_multiplier': game_state.shop_price_multiplier,
                'botnet_buff': game_state.botnet_buff
            }

            cursor.execute('''...''')  # same as original
            self.conn.commit()
            return True

        def threat_to_dict(self, threat):
            return {...}  # same as original

        def load_game(self, save_name):
            ...  # same as original

        def get_save_names(self):
            ...  # same as original

        def save_high_score(self, player_name, score, turns):
            ...  # same as original

        def get_high_scores(self, limit=10):
            ...  # same as original

    class Game:
        ...  # same as original, no color changes here

    class GameGUI:
        def __init__(self, username):
            self.username = username  # store username
            self.game = Game()
            self.root = tk.Tk()
            self.root.title(f"Cybersecurity Defence Game - {self.username}")
            self.root.geometry("1200x800")
            self.root.configure(bg=COLOUR_MAIN_BG)

            self.selected_tool = None
            self.selected_threat = None

            self.setup_ui()
            self.update_display()

        def setup_ui(self):
            main_frame = tk.Frame(self.root, bg=COLOUR_MAIN_BG)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            top_frame = tk.Frame(main_frame, bg=COLOUR_MAIN_BG, relief=tk.RAISED, bd=2)
            top_frame.pack(fill=tk.X, pady=(0, 10))

            self.status_label = tk.Label(
                top_frame,
                text="",
                font=('Arial', 12, 'bold'),
                bg=COLOUR_PANEL_BG,
                fg=COLOUR_HP_BAR
            )
            self.status_label.pack(pady=10)

            hp_frame = tk.Frame(top_frame, bg=COLOUR_PANEL_BG)
            hp_frame.pack(pady=5)

            tk.Label(hp_frame, text="Server HP:", bg=COLOUR_PANEL_BG, fg=COLOUR_TEXT_PRIMARY).pack(side=tk.LEFT)
            self.hp_bar = ttk.Progressbar(hp_frame, length=300, mode='determinate')
            self.hp_bar.pack(side=tk.LEFT, padx=10)
            self.hp_label = tk.Label(hp_frame, text="", bg=COLOUR_PANEL_BG, fg=COLOUR_TEXT_PRIMARY)
            self.hp_label.pack(side=tk.LEFT)

            middle_frame = tk.Frame(main_frame, bg=COLOUR_MAIN_BG)
            middle_frame.pack(fill=tk.BOTH, expand=True)

            threats_frame = tk.LabelFrame(
                middle_frame,
                text="Active Threats",
                bg=COLOUR_PANEL_BG,
                fg=COLOUR_THREAT_HIGHLIGHT,
                font=('Arial', 10, 'bold')
            )
            threats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

            self.threats_listbox = tk.Listbox(
                threats_frame,
                bg=COLOUR_MAIN_BG,
                fg=COLOUR_TEXT_PRIMARY,
                selectbackground=COLOUR_THREAT_HIGHLIGHT,
                font=('Courier', 9)
            )
            self.threats_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.threats_listbox.bind('<<ListboxSelect>>', self.on_threat_select)

            tools_frame = tk.LabelFrame(
                middle_frame,
                text="Owned Tools",
                bg=COLOUR_PANEL_BG,
                fg=COLOUR_TOOL_HIGHLIGHT,
                font=('Arial', 10, 'bold')
            )
            tools_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            self.tools_listbox = tk.Listbox(
                tools_frame,
                bg=COLOUR_MAIN_BG,
                fg=COLOUR_TEXT_PRIMARY,
                selectbackground=COLOUR_TOOL_HIGHLIGHT,
                font=('Courier', 9)
            )
            self.tools_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.tools_listbox.bind('<<ListboxSelect>>', self.on_tool_select)

            shop_frame = tk.LabelFrame(
                middle_frame,
                text="Tool Shop",
                bg=COLOUR_PANEL_BG,
                fg=COLOUR_SHOP_SECTION,
                font=('Arial', 10, 'bold')
            )
            shop_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

            self.shop_listbox = tk.Listbox(
                shop_frame,
                bg=COLOUR_MAIN_BG,
                fg=COLOUR_TEXT_PRIMARY,
                selectbackground=COLOUR_SHOP_SECTION,
                font=('Courier', 9)
            )
            self.shop_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.shop_listbox.bind('<Double-Button-1>', self.buy_tool)

            controls_frame = tk.Frame(main_frame, bg=COLOUR_PANEL_BG, relief=tk.RAISED, bd=2)
            controls_frame.pack(fill=tk.X, pady=(10, 0))

            button_frame = tk.Frame(controls_frame, bg=COLOUR_PANEL_BG)
            button_frame.pack(pady=10)

            tk.Button(button_frame, text="Scan for Threats", command=self.scan_threats,
                      bg=COLOUR_BUTTON_SCAN,
                      fg=COLOUR_TEXT_PRIMARY,
                      font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

            tk.Button(button_frame, text="Use Tool", command=self.use_tool,
                      bg=COLOUR_BUTTON_USE_TOOL,
                      fg=COLOUR_TEXT_PRIMARY,
                      font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

            tk.Button(button_frame, text="Next Turn", command=self.next_turn,
                      bg=COLOUR_BUTTON_NEXT_TURN,
                      fg=COLOUR_TEXT_PRIMARY,
                      font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

            tk.Button(button_frame, text="Save Game", command=self.save_game,
                      bg=COLOUR_BUTTON_SAVE,
                      fg=COLOUR_TEXT_PRIMARY,
                      font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

            tk.Button(button_frame, text="Load Game", command=self.load_game,
                      bg=COLOUR_BUTTON_LOAD,
                      fg=COLOUR_TEXT_PRIMARY,
                      font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

            tk.Button(button_frame, text="High Scores", command=self.show_high_scores,
                      bg=COLOUR_BUTTON_HS,
                      fg=COLOUR_TEXT_PRIMARY,
                      font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

            self.game.game_state.owned_tools = [ToolType.BASIC_FIREWALL, ToolType.ANTIVIRUS_SCANNER]


    def update_display(self):
        # Update status
        status_text = "Turn: " + str(self.game.game_state.turn) + " | Points: " + str(
            self.game.game_state.points) + " | Score: " + str(self.game.game_state.score)
        self.status_label.config(text=status_text)

        # Update HP bar
        hp_percent = (self.game.game_state.server_hp / self.game.game_state.max_server_hp) * 100
        self.hp_bar['value'] = hp_percent
        hp_text = str(self.game.game_state.server_hp) + "/" + str(self.game.game_state.max_server_hp)
        self.hp_label.config(text=hp_text)

        # Update threats list
        self.threats_listbox.delete(0, tk.END)
        for i, threat in enumerate(self.game.game_state.active_threats):
            hp_bar = "█" * (threat.hp * 10 // threat.max_hp) + "░" * (10 - threat.hp * 10 // threat.max_hp)
            threat_text = threat.type + " HP:" + str(threat.hp) + "/" + str(
                threat.max_hp) + " [" + hp_bar + "] ATK:" + str(threat.attack)
            if threat.detection_chance < 1.0:
                threat_text += " [HIDDEN]"
            self.threats_listbox.insert(tk.END, threat_text)

        # Update tools list
        self.tools_listbox.delete(0, tk.END)
        for tool_type in self.game.game_state.owned_tools:
            self.tools_listbox.insert(tk.END, tool_type)

        # Update shop
        self.shop_listbox.delete(0, tk.END)
        for tool_type, tool in self.game.tools_data.items():
            if tool_type not in self.game.game_state.owned_tools:
                cost = int(tool.cost * self.game.game_state.shop_price_multiplier)
                affordable = "✓" if self.game.game_state.points >= cost else "✗"
                shop_text = affordable + " " + tool_type + " Cost: " + str(cost)
                self.shop_listbox.insert(tk.END, shop_text)

        # Check game over
        if self.game.game_state.game_over:
            self.game_over()

    def on_threat_select(self, event):
        selection = self.threats_listbox.curselection()
        if selection:
            self.selected_threat = selection[0]

    def on_tool_select(self, event):
        selection = self.tools_listbox.curselection()
        if selection:
            self.selected_tool = selection[0]

    def scan_threats(self):
        if self.game.game_state.scans_this_turn >= 2:
            messagebox.showwarning("Limit Reached", "You can only scan twice per turn.")
            return

        new_threats = self.game.generate_threats()

        # Apply detection chances
        detected_threats = []
        for threat in new_threats:
            if random.random() < threat.detection_chance:
                detected_threats.append(threat)

        self.game.game_state.active_threats.extend(detected_threats)

        messagebox.showinfo(
            "Scan Results",
            "Scan complete!\nFound " + str(len(detected_threats)) + " threats."
        )
        self.update_display()
        self.game.game_state.scans_this_turn += 1

    def use_tool(self):
        if self.selected_tool is None or self.selected_threat is None:
            messagebox.showwarning("Selection Error", "Please select both a tool and a threat!")
            return

        if self.selected_threat >= len(self.game.game_state.active_threats):
            messagebox.showwarning("Invalid Target", "Selected threat no longer exists!")
            return

        tool_type = self.game.game_state.owned_tools[self.selected_tool]
        target_threat = self.game.game_state.active_threats[self.selected_threat]

        result = self.game.use_tool(tool_type, target_threat)

        if "error" in result:
            messagebox.showerror("Error", result["error"])
            return

        message = "Used " + tool_type + "\n"
        message += "Damage: " + str(result['damage']) + "\n"
        message += "Effectiveness: " + str(round(result['effectiveness'], 1)) + "x\n"

        if result["threat_defeated"]:
            message += "Threat defeated!"

        messagebox.showinfo("Attack Result", message)

        # Process defeated threats
        points_earned = self.game.process_defeated_threats()
        if points_earned > 0:
            messagebox.showinfo("Points Earned", "Earned " + str(points_earned) + " points!")

        self.update_display()

    def buy_tool(self, event):
        selection = self.shop_listbox.curselection()
        if not selection:
            return

        # Get the tool type from the shop list
        available_tools = []
        for tool_type in self.game.tools_data.keys():
            if tool_type not in self.game.game_state.owned_tools:
                available_tools.append(tool_type)

        if selection[0] >= len(available_tools):
            return

        tool_type = available_tools[selection[0]]

        if self.game.buy_tool(tool_type):
            messagebox.showinfo("Purchase Successful", "Bought " + tool_type + "!")
            self.update_display()
        else:
            messagebox.showwarning("Purchase Failed", "Not enough points or tool already owned!")

    def next_turn(self):
        # Process threat attacks
        self.game.process_threat_attacks()

        if not self.game.game_state.game_over:
            self.game.next_turn()
            messagebox.showinfo("Turn Complete", "Turn " + str(self.game.game_state.turn) + " begins!")
            self.update_display()


    def save_game(self):
        save_name = simpledialog.askstring("Save Game", "Enter save name:")
        if save_name:
            if self.game.db.save_game(save_name, self.game.game_state):
                messagebox.showinfo("Save Successful", "Game saved as '" + save_name + "'!")
            else:
                messagebox.showerror("Save Failed", "Failed to save game!")

    def load_game(self):
        save_names = self.game.db.get_save_names()
        if not save_names:
            messagebox.showinfo("No Saves", "No saved games found!")
            return

        # Create selection dialogue
        dialogue = tk.Toplevel(self.root)
        dialogue.title("Load Game")
        dialogue.geometry("300x400")
        dialogue.configure(bg='#2d2d2d')

        tk.Label(dialogue, text="Select save to load:", bg='#2d2d2d', fg='white').pack(pady=10)

        listbox = tk.Listbox(dialogue, bg='#1a1a1a', fg='white')
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for save_name in save_names:
            listbox.insert(tk.END, save_name)

        def load_selected():
            selection = listbox.curselection()
            if selection:
                save_name = save_names[selection[0]]
                loaded_state = self.game.db.load_game(save_name)
                if loaded_state:
                    self.game.game_state = loaded_state
                    messagebox.showinfo("Load Successful", "Loaded '" + save_name + "'!")
                    self.update_display()
                    dialogue.destroy()
                else:
                    messagebox.showerror("Load Failed", "Failed to load game!")

        tk.Button(dialogue, text="Load", command=load_selected, bg='#006600', fg='white').pack(pady=10)
        tk.Button(dialogue, text="Cancel", command=dialogue.destroy, bg='#660000', fg='white').pack()

    def quit_game(self):

        quit()

    def show_high_scores(self):
        scores = self.game.db.get_high_scores()

        dialogue = tk.Toplevel(self.root)
        dialogue.title("High Scores")
        dialogue.geometry("500x400")
        dialogue.configure(bg='#2d2d2d')

        tk.Label(dialogue, text="High Scores", font=('Arial', 16, 'bold'), bg='#2d2d2d', fg='#00ff00').pack(pady=10)

        # Create treeview for scores
        columns = ('Rank', 'Player', 'Score', 'Turns', 'Date')
        tree = ttk.Treeview(dialogue, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        for i, score_data in enumerate(scores, 1):
            player, score, turns, date = score_data
            tree.insert('', 'end', values=(i, player, score, turns, date[:10]))

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(dialogue, text="Close", command=dialogue.destroy, bg='#660000', fg='white').pack(pady=10)

    def game_over(self):
        player_name = self.username or simpledialog.askstring("Game Over", "Enter your name for high score:")
        if player_name:
            self.game.db.save_high_score(player_name, self.game.game_state.score, self.game.game_state.turn)

        message = "Game Over!\n\nFinal Score: " + str(self.game.game_state.score) + "\n"
        message += "Turns Survived: " + str(self.game.game_state.turn) + "\n\n"
        message += "Would you like to start a new game?"

        if messagebox.askyesno("Game Over", message):
            self.game.game_state = GameState()
            self.game.game_state.owned_tools = [ToolType.BASIC_FIREWALL, ToolType.ANTIVIRUS_SCANNER]
            self.update_display()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = GameGUI()
    game.run()
