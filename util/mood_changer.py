import datetime

# --------data----------
MAX_MOOD = 120
MIN_MOOD = 0
REQ_BONUS_INCREMENT_MINUTES = 30
REQ_BONUS_MAX_AMOUNT = 80
REQ_BONUS_PER_INCREMENT = 5
# ---------------------

class MoodSystem:

    current_mood = 100
    def __init__(self):
        self.known_users = {}  # {user id: last activity timestamp}
        
    def get_mood (self) -> int:
        return self.current_mood
    
    def get_mood_level(self) -> int:
        """Calculates mood level (1-5) based on the current mood value."""
        # 5 mood levels, mood level = mood/20
        raw_lvl = int(self.current_mood / 20)
        return max(1, min(raw_lvl, 5))

    def reset_mood(self) -> None:
        self.current_mood = 100
        self.known_users = {}
        return
    # =========================================================================
    #                      PRE INPUT UDATE
    # =========================================================================
    def pre_input_update(self, last_activity_time, user_id: int):
        now = datetime.datetime.now()
        
        # --- 1. new user ---
        # if user not in map; mood +40
        if user_id not in self.known_users:
            self.current_mood += 40
            self.known_users[user_id] = now
        else:
            self.known_users[user_id] = now
        
        # --- 2. time based bonus---
        # for mood < 60
        if self.current_mood < 60:
            # if current time > previous; mood + 5 each for each 30 min passed (max 60)
            time_elapsed = now - last_activity_time
            
            minutes_elapsed = time_elapsed.total_seconds() / 60
            intervals_passed = int(minutes_elapsed // REQ_BONUS_INCREMENT_MINUTES)
            
            if intervals_passed > 0:
                time_bonus = intervals_passed * REQ_BONUS_PER_INCREMENT
                # apply the maximum cap (60)
                if self.current_mood + time_bonus > 60:
                    self.current_mood = 60
                else:
                    self.current_mood +=time_bonus
        
        # apply mood cap
        self.current_mood = max(MIN_MOOD, min(self.current_mood, MAX_MOOD))

        
        return


    # =========================================================================
    #                              POST-OUTPUT UPDATE
    # =========================================================================
    def post_output_update(self, message_output: str):
        #based of bot's output

        # --- 1. short output gets rewarded / long gets punished ---
        
        # if output > 100 char; mood -20
        if len(message_output) > 100:
            self.current_mood -= 20

        # if "?" in output; mood -10
        if '?' in message_output:
            self.current_mood -= 10
            self.current_mood = max(MIN_MOOD, min(self.current_mood, MAX_MOOD))
                    
        # if output < 70 char; mood +35
        if len(message_output) < 70:
            self.current_mood += 35
            
        #apply mood cap
        self.current_mood = max(MIN_MOOD, min(self.current_mood, MAX_MOOD))
        return