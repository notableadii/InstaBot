import time
import logging
from datetime import datetime
from instagrapi import Client
import google.generativeai as genai
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

# Bot settings
BOT_ACTIVE = True  # Set to False to pause bot
RESPONSE_DELAY = random.randint(60, 300)  # Seconds to wait before responding

# ============================================
# BOT CODE (Don't modify below unless you know what you're doing)
# ============================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstagramCoupleBot:
    def __init__(self):
        # Instagram setup
        self.client = Client()
        self.username = INSTAGRAM_USERNAME
        self.password = INSTAGRAM_PASSWORD
        self.girlfriend_username = GIRLFRIEND_USERNAME
        
        # Gemini setup
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Bot state
        self.is_active = BOT_ACTIVE
        self.processed_messages = set()
        self.my_user_id = None
        self.girlfriend_id = None
        
    def login(self):
        """Login to Instagram"""
        try:
            logger.info("🔐 Logging into Instagram...")
            self.client.login(self.username, self.password)
            self.my_user_id = self.client.user_id
            logger.info(f"✅ Logged in successfully! User ID: {self.my_user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            logger.error("💡 Tips: Check username/password, make sure account isn't locked")
            return False
    
    def get_girlfriend_user_id(self):
        """Get girlfriend's user ID"""
        try:
            logger.info(f"🔍 Looking up user: {self.girlfriend_username}")
            user_info = self.client.user_info_by_username(self.girlfriend_username)
            self.girlfriend_id = user_info.pk
            logger.info(f"✅ Found girlfriend's ID: {self.girlfriend_id}")
            return self.girlfriend_id
        except Exception as e:
            logger.error(f"❌ Could not find user {self.girlfriend_username}: {e}")
            return None
    
    def generate_response(self, message):
        """Generate AI response using Gemini"""
        try:
            logger.info("🤖 Generating AI response...")
            
            prompt = f"""
            You are responding as a boyfriend in a text conversation with your girlfriend.
            Be sweet, very casual, authentic, and caring. Keep responses natural and under 40 words.
            dont Use emojis. Don't mention you're an AI. Message her like a real human being, keep the texts in lowercase, and use keywords like - cutie like call her cutie time to time, bbg which means babygirl i call her that sometimes and respond to her in a genz style but dont overdo it keep it natural 
            
            ALSO DONT REPLY TO OLD MESSAGES REPLY TO NEW MESSAGES
            
            Her message: "{message}"
            
            Respond as her boyfriend would in a genz style dont overdo it:
            """
            
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()
            logger.info(f"✅ Generated response: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            # Fallback responses
            fallbacks = [
                "Hey cutiee! ❤️",
                "Love you too! 😘",
                "That sounds awesome!",
                "I'm here for you! 💕",
                "Miss you! 🥰"
            ]
            import random
            return random.choice(fallbacks)
    
    def get_dm_thread(self):
        """Get DM thread with girlfriend"""
        try:
            logger.info("📱 Getting DM threads...")
            threads = self.client.direct_threads(amount=20)
            
            for thread in threads:
                for user in thread.users:
                    if user.pk == self.girlfriend_id:
                        logger.info(f"✅ Found DM thread: {thread.id}")
                        return thread
            
            logger.error("❌ No DM thread found with girlfriend")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting DM threads: {e}")
            return None
    
    def get_recent_messages(self, thread_id, count=5):
        """Get recent messages from thread"""
        try:
            messages = self.client.direct_messages(thread_id, amount=count)
            return messages
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    def send_message(self, message):
        """Send message to girlfriend"""
        try:
            logger.info(f"⏳ Waiting {RESPONSE_DELAY} seconds before responding...")
            time.sleep(RESPONSE_DELAY)
            
            logger.info("📤 Sending message...")
            self.client.direct_send(message, user_ids=[self.girlfriend_id])
            logger.info(f"✅ Message sent: {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    def should_respond_to_message(self, message):
        """Check if bot should respond to this message"""
        # Don't respond to own messages
        if message.user_id == self.my_user_id:
            return False
        
        # Don't respond if we've already processed this message
        if message.id in self.processed_messages:
            return False
        
        # Don't respond if bot is paused
        if not self.is_active:
            return False
        
        # Only respond to messages from girlfriend
        if message.user_id != self.girlfriend_id:
            return False
        
        return True
    
    def start_monitoring(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting Instagram DM Bot...")
        
        # Step 1: Login
        if not self.login():
            return
        
        # Step 2: Get girlfriend's user ID
        if not self.get_girlfriend_user_id():
            return
        
        # Step 3: Get DM thread
        dm_thread = self.get_dm_thread()
        if not dm_thread:
            return
        
        logger.info("🤖 Bot is now monitoring DMs! Press Ctrl+C to stop")
        logger.info(f"👤 Monitoring messages from: {self.girlfriend_username}")
        logger.info(f"⏰ Response delay: {RESPONSE_DELAY} seconds")
        
        # Main monitoring loop
        try:
            while True:
                if not self.is_active:
                    logger.info("⏸️ Bot is paused")
                    time.sleep(30)
                    continue
                
                # Get recent messages
                messages = self.get_recent_messages(dm_thread.id, 3)
                
                # Process messages (newest first)
                for message in reversed(messages):
                    if self.should_respond_to_message(message):
                        logger.info(f"📨 New message from {self.girlfriend_username}: '{message.text}'")
                        
                        # Mark as processed
                        self.processed_messages.add(message.id)
                        
                        # Generate and send response
                        response = self.generate_response(message.text)
                        if self.send_message(response):
                            logger.info("💬 Response sent successfully!")
                        else:
                            logger.error("❌ Failed to send response")
                
                # Wait before next check
                logger.info("⏳ Waiting random seconds before next check...")
                time.sleep(random.randint(120, 300))  # 2-10 minutes instead of 30 seconds
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            logger.info("🔄 Restarting in 60 seconds...")
            time.sleep(60)
            self.start_monitoring()  # Restart

def main():
    """Main function to run the bot"""
    
    # Validate configuration
    if INSTAGRAM_USERNAME == "your_test_username_here":
        print("❌ ERROR: Please configure your Instagram username in the code!")
        return
    
    if INSTAGRAM_PASSWORD == "your_test_password_here":
        print("❌ ERROR: Please configure your Instagram password in the code!")
        return
    
    if GIRLFRIEND_USERNAME == "her_username_here":
        print("❌ ERROR: Please configure your girlfriend's username in the code!")
        return
    
    if GEMINI_API_KEY == "your_gemini_api_key_here":
        print("❌ ERROR: Please configure your Gemini API key in the code!")
        print("💡 Get it from: https://makersuite.google.com/app/apikey")
        return
    
    # Create and start bot
    bot = InstagramCoupleBot()
    bot.start_monitoring()

if __name__ == "__main__":
    main()