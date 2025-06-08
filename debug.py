import time
import logging
from datetime import datetime
from instagrapi import Client
import google.generativeai as genai
import json
import random

# ============================================
# CONFIGURE YOUR CREDENTIALS HERE
# ============================================

# Instagram credentials (your TEST account)
INSTAGRAM_USERNAME = "your_test_username_here"
INSTAGRAM_PASSWORD = "your_test_password_here"
GIRLFRIEND_USERNAME = "her_username_here"

# Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY = "your_gemini_api_key_here"

# DEBUG SETTINGS
DEBUG_MODE = True          # Set to False for production
DRY_RUN = True            # If True, won't actually send messages
VERBOSE_LOGGING = True     # Extra detailed logs
SAVE_MESSAGES = True       # Save messages to file for analysis

# Bot settings
BOT_ACTIVE = True
RESPONSE_DELAY = 60
MIN_CHECK_INTERVAL = 60    # Minimum seconds between checks
MAX_CHECK_INTERVAL = 300   # Maximum seconds between checks

# ============================================
# DEBUG BOT CODE
# ============================================

# Configure logging
log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstagramCouplebotDebug:
    def __init__(self):
        self.client = Client()
        self.username = INSTAGRAM_USERNAME
        self.password = INSTAGRAM_PASSWORD
        self.girlfriend_username = GIRLFRIEND_USERNAME
        
        # Gemini setup
        if GEMINI_API_KEY != "your_gemini_api_key_here":
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("⚠️ Gemini API key not configured - using fallback responses")
        
        # Bot state
        self.is_active = BOT_ACTIVE
        self.processed_messages = set()
        self.my_user_id = None
        self.girlfriend_id = None
        self.message_log = []
        self.session_stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'ai_responses': 0,
            'fallback_responses': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        logger.info("🐛 DEBUG MODE ENABLED")
        logger.info(f"🔍 Dry run: {'ON' if DRY_RUN else 'OFF'}")
        logger.info(f"💾 Save messages: {'ON' if SAVE_MESSAGES else 'OFF'}")
    
    def debug_print(self, message, level="INFO"):
        """Enhanced debug printing"""
        if DEBUG_MODE and VERBOSE_LOGGING:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def save_message_log(self):
        """Save message log to file"""
        if SAVE_MESSAGES:
            try:
                with open('message_log.json', 'w') as f:
                    json.dump(self.message_log, f, indent=2, default=str)
                self.debug_print("💾 Message log saved")
            except Exception as e:
                logger.error(f"❌ Failed to save message log: {e}")
    
    def print_session_stats(self):
        """Print session statistics"""
        duration = datetime.now() - self.session_stats['start_time']
        logger.info("📊 SESSION STATISTICS")
        logger.info(f"⏱️ Duration: {duration}")
        logger.info(f"📨 Messages received: {self.session_stats['messages_received']}")
        logger.info(f"📤 Messages sent: {self.session_stats['messages_sent']}")
        logger.info(f"🤖 AI responses: {self.session_stats['ai_responses']}")
        logger.info(f"🔄 Fallback responses: {self.session_stats['fallback_responses']}")
        logger.info(f"❌ Errors: {self.session_stats['errors']}")
    
    def test_connection(self):
        """Test Instagram connection without logging in"""
        try:
            logger.info("🔍 Testing connection to Instagram...")
            # Just test if we can reach Instagram
            test_client = Client()
            logger.info("✅ Connection test passed")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def test_gemini_api(self):
        """Test Gemini API connection"""
        if not self.model:
            logger.warning("⚠️ Gemini API not configured")
            return False
        
        try:
            logger.info("🔍 Testing Gemini API...")
            test_response = self.model.generate_content("Say hello")
            logger.info(f"✅ Gemini API test passed: {test_response.text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Gemini API test failed: {e}")
            return False
    
    def login(self):
        """Login to Instagram with debug info"""
        try:
            logger.info("🔐 Attempting Instagram login...")
            self.debug_print(f"Username: {self.username}")
            self.debug_print("Password: [HIDDEN]")
            
            # Try to load session first
            try:
                session_file = f"{self.username}_session.json"
                self.client.load_settings(session_file)
                self.client.login(self.username, self.password)
                logger.info("✅ Loaded existing session")
            except:
                # Fresh login
                self.client.login(self.username, self.password)
                # Save session
                self.client.dump_settings(f"{self.username}_session.json")
                logger.info("✅ Created new session")
            
            self.my_user_id = self.client.user_id
            logger.info(f"✅ Login successful! User ID: {self.my_user_id}")
            
            # Get account info for debugging
            if VERBOSE_LOGGING:
                account_info = self.client.account_info()
                self.debug_print(f"Account followers: {account_info.follower_count}")
                self.debug_print(f"Account following: {account_info.following_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            self.session_stats['errors'] += 1
            
            # Debug suggestions
            if "challenge_required" in str(e):
                logger.info("💡 Instagram is asking for verification - try logging in manually first")
            elif "bad_password" in str(e):
                logger.info("💡 Check your password")
            elif "user_not_found" in str(e):
                logger.info("💡 Check your username")
            
            return False
    
    def get_girlfriend_user_id(self):
        """Get girlfriend's user ID with debug info"""
        try:
            logger.info(f"🔍 Looking up user: {self.girlfriend_username}")
            user_info = self.client.user_info_by_username(self.girlfriend_username)
            self.girlfriend_id = user_info.pk
            
            logger.info(f"✅ Found user: {user_info.username}")
            logger.info(f"👤 Full name: {user_info.full_name}")
            logger.info(f"🆔 User ID: {self.girlfriend_id}")
            
            if VERBOSE_LOGGING:
                self.debug_print(f"Is private: {user_info.is_private}")
                self.debug_print(f"Followers: {user_info.follower_count}")
                self.debug_print(f"Following: {user_info.following_count}")
            
            return self.girlfriend_id
            
        except Exception as e:
            logger.error(f"❌ Could not find user {self.girlfriend_username}: {e}")
            self.session_stats['errors'] += 1
            return None
    
    def generate_response(self, message):
        """Generate AI response with debug info"""
        try:
            logger.info("🤖 Generating AI response...")
            self.debug_print(f"Input message: '{message}'")
            
            if not self.model:
                logger.warning("⚠️ Using fallback response (no Gemini API)")
                self.session_stats['fallback_responses'] += 1
                return self.get_fallback_response()
            
            prompt = f"""
            You are responding as a loving boyfriend in a text conversation with your girlfriend.
            Be sweet, casual, authentic, and caring. Keep responses natural and under 40 words.
            Use emojis occasionally but don't overdo it. Don't mention you're an AI.
            
            Her message: "{message}"
            
            Respond as her boyfriend would:
            """
            
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()
            
            self.debug_print(f"AI response: '{ai_response}'")
            logger.info(f"✅ Generated response: {ai_response[:50]}...")
            
            self.session_stats['ai_responses'] += 1
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            self.session_stats['errors'] += 1
            self.session_stats['fallback_responses'] += 1
            return self.get_fallback_response()
    
    def get_fallback_response(self):
        """Get fallback response"""
        fallbacks = [
            "Hey babe! ❤️",
            "Love you too! 😘",
            "That sounds awesome!",
            "I'm here for you! 💕",
            "Miss you! 🥰",
            "You're amazing! ✨",
            "Can't wait to see you! 💖",
            "That made me smile! 😊"
        ]
        response = random.choice(fallbacks)
        self.debug_print(f"Using fallback: '{response}'")
        return response
    
    def get_dm_thread(self):
        """Get DM thread with debug info"""
        try:
            logger.info("📱 Getting DM threads...")
            threads = self.client.direct_threads(amount=20)
            
            self.debug_print(f"Found {len(threads)} threads")
            
            for i, thread in enumerate(threads):
                self.debug_print(f"Thread {i}: {len(thread.users)} users")
                
                for user in thread.users:
                    self.debug_print(f"  User: {user.username} (ID: {user.pk})")
                    
                    if user.pk == self.girlfriend_id:
                        logger.info(f"✅ Found DM thread with {user.username}")
                        logger.info(f"🆔 Thread ID: {thread.id}")
                        
                        # Get thread info
                        if VERBOSE_LOGGING:
                            self.debug_print(f"Thread title: {thread.thread_title}")
                            self.debug_print(f"Last activity: {thread.last_activity_at}")
                        
                        return thread
            
            logger.error("❌ No DM thread found with girlfriend")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting DM threads: {e}")
            self.session_stats['errors'] += 1
            return None
    
    def get_recent_messages(self, thread_id, count=5):
        """Get recent messages with debug info"""
        try:
            self.debug_print(f"Getting {count} recent messages from thread {thread_id}")
            messages = self.client.direct_messages(thread_id, amount=count)
            
            logger.info(f"📨 Retrieved {len(messages)} messages")
            
            if VERBOSE_LOGGING:
                for i, msg in enumerate(messages):
                    self.debug_print(f"Message {i}: {msg.text[:50]}... (User: {msg.user_id})")
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            self.session_stats['errors'] += 1
            return []
    
    def send_message(self, message):
        """Send message with debug info"""
        try:
            # Calculate random delay for more human-like behavior
            delay = random.randint(RESPONSE_DELAY, RESPONSE_DELAY + 60)
            logger.info(f"⏳ Waiting {delay} seconds before responding...")
            
            if DRY_RUN:
                logger.info(f"🧪 DRY RUN - Would send: '{message}'")
                logger.info("✅ Message 'sent' (dry run)")
                return True
            
            time.sleep(delay)
            
            logger.info("📤 Sending message...")
            self.client.direct_send(message, user_ids=[self.girlfriend_id])
            logger.info(f"✅ Message sent: {message}")
            
            self.session_stats['messages_sent'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            self.session_stats['errors'] += 1
            return False
    
    def should_respond_to_message(self, message):
        """Check if bot should respond with debug info"""
        self.debug_print(f"Checking message ID: {message.id}")
        
        # Don't respond to own messages
        if message.user_id == self.my_user_id:
            self.debug_print("Skipping - own message")
            return False
        
        # Don't respond if already processed
        if message.id in self.processed_messages:
            self.debug_print("Skipping - already processed")
            return False
        
        # Don't respond if bot is paused
        if not self.is_active:
            self.debug_print("Skipping - bot paused")
            return False
        
        # Only respond to girlfriend
        if message.user_id != self.girlfriend_id:
            self.debug_print("Skipping - not from girlfriend")
            return False
        
        self.debug_print("✅ Should respond to this message")
        return True
    
    def run_diagnostics(self):
        """Run full diagnostic check"""
        logger.info("🔧 RUNNING DIAGNOSTICS...")
        
        # Test 1: Configuration
        logger.info("1️⃣ Checking configuration...")
        config_ok = True
        
        if INSTAGRAM_USERNAME == "your_test_username_here":
            logger.error("❌ Instagram username not configured")
            config_ok = False
        
        if INSTAGRAM_PASSWORD == "your_test_password_here":
            logger.error("❌ Instagram password not configured")
            config_ok = False
        
        if GIRLFRIEND_USERNAME == "her_username_here":
            logger.error("❌ Girlfriend username not configured")
            config_ok = False
        
        if GEMINI_API_KEY == "your_gemini_api_key_here":
            logger.warning("⚠️ Gemini API key not configured - will use fallbacks")
        
        if config_ok:
            logger.info("✅ Configuration looks good")
        
        # Test 2: Connection
        logger.info("2️⃣ Testing connection...")
        if self.test_connection():
            logger.info("✅ Connection test passed")
        
        # Test 3: Gemini API
        logger.info("3️⃣ Testing Gemini API...")
        if self.test_gemini_api():
            logger.info("✅ Gemini API test passed")
        
        # Test 4: Login (if config is OK)
        if config_ok:
            logger.info("4️⃣ Testing login...")
            if self.login():
                logger.info("✅ Login test passed")
                
                # Test 5: User lookup
                logger.info("5️⃣ Testing user lookup...")
                if self.get_girlfriend_user_id():
                    logger.info("✅ User lookup test passed")
                    
                    # Test 6: DM thread
                    logger.info("6️⃣ Testing DM thread access...")
                    thread = self.get_dm_thread()
                    if thread:
                        logger.info("✅ DM thread test passed")
                        
                        # Test 7: Message retrieval
                        logger.info("7️⃣ Testing message retrieval...")
                        messages = self.get_recent_messages(thread.id, 3)
                        if messages:
                            logger.info(f"✅ Retrieved {len(messages)} messages")
                        
        logger.info("🔧 DIAGNOSTICS COMPLETE")
        return config_ok
    
    def start_monitoring(self):
        """Main monitoring loop with debug features"""
        logger.info("🚀 Starting Instagram DM Bot (DEBUG MODE)...")
        
        # Run diagnostics first
        if not self.run_diagnostics():
            logger.error("❌ Diagnostics failed - please fix configuration")
            return
        
        # Get DM thread
        dm_thread = self.get_dm_thread()
        if not dm_thread:
            logger.error("❌ Could not access DM thread")
            return
        
        logger.info("🤖 Bot is now monitoring DMs! Press Ctrl+C to stop")
        logger.info(f"👤 Monitoring messages from: {self.girlfriend_username}")
        logger.info(f"⏰ Response delay: {RESPONSE_DELAY}-{RESPONSE_DELAY+60} seconds")
        logger.info(f"🔄 Check interval: {MIN_CHECK_INTERVAL}-{MAX_CHECK_INTERVAL} seconds")
        
        # Main monitoring loop
        try:
            while True:
                if not self.is_active:
                    logger.info("⏸️ Bot is paused")
                    time.sleep(30)
                    continue
                
                # Get recent messages
                messages = self.get_recent_messages(dm_thread.id, 5)
                
                # Process messages (newest first)
                for message in reversed(messages):
                    if self.should_respond_to_message(message):
                        logger.info(f"📨 New message from {self.girlfriend_username}: '{message.text}'")
                        
                        self.session_stats['messages_received'] += 1
                        
                        # Save message to log
                        if SAVE_MESSAGES:
                            self.message_log.append({
                                'timestamp': datetime.now(),
                                'from': self.girlfriend_username,
                                'message': message.text,
                                'message_id': message.id
                            })
                        
                        # Mark as processed
                        self.processed_messages.add(message.id)
                        
                        # Generate and send response
                        response = self.generate_response(message.text)
                        
                        # Save response to log
                        if SAVE_MESSAGES:
                            self.message_log.append({
                                'timestamp': datetime.now(),
                                'from': 'bot',
                                'message': response,
                                'type': 'response'
                            })
                        
                        if self.send_message(response):
                            logger.info("💬 Response sent successfully!")
                        else:
                            logger.error("❌ Failed to send response")
                
                # Save message log
                self.save_message_log()
                
                # Random wait time to appear more human
                wait_time = random.randint(MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL)
                logger.info(f"⏳ Waiting {wait_time} seconds before next check...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            self.print_session_stats()
            self.save_message_log()
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            self.session_stats['errors'] += 1
            self.print_session_stats()
            self.save_message_log()
            
            if DEBUG_MODE:
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
            
            logger.info("🔄 Restarting in 60 seconds...")
            time.sleep(60)
            self.start_monitoring()  # Restart

def main():
    """Main function with debug menu"""
    print("🐛 Instagram Bot - DEBUG VERSION")
    print("="*50)
    
    if DEBUG_MODE:
        print("Available options:")
        print("1. Run diagnostics only")
        print("2. Start monitoring (with debug)")
        print("3. Test AI responses")
        print("4. Exit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        bot = InstagramCouplebotDebug()
        
        if choice == "1":
            bot.run_diagnostics()
        elif choice == "2":
            bot.start_monitoring()
        elif choice == "3":
            # Test AI responses
            test_messages = [
                "Hey babe!",
                "How was your day?",
                "I love you",
                "What are you up to?",
                "Miss you so much"
            ]
            
            for msg in test_messages:
                print(f"\nInput: {msg}")
                response = bot.generate_response(msg)
                print(f"Output: {response}")
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice, starting monitoring...")
            bot.start_monitoring()
    else:
        # Production mode
        bot = InstagramCouplebotDebug()
        bot.start_monitoring()

if __name__ == "__main__":
    main()