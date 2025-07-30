#!/usr/bin/env python3
"""
🎨 Python Midjourney Client
Midjourney automation system using Discord user tokens
"""

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from PIL import Image


class MidjourneyClient:
    """Midjourney automation client"""
    
    def __init__(self, 
                 user_token: str = None, 
                 channel_id: str = None,
                 auto_split: bool = True):
        """
        Initialize Midjourney client
        
        Args:
            user_token: Discord user token (can use DISCORD_USER_TOKEN environment variable)
            channel_id: Discord channel ID (can use MIDJOURNEY_CHANNEL_ID environment variable)
            auto_split: Whether to automatically split generated images
        """
        self.user_token = user_token or os.getenv("DISCORD_USER_TOKEN")
        self.channel_id = channel_id or os.getenv("MIDJOURNEY_CHANNEL_ID")
        self.base_url = "https://discord.com/api/v10"
        self.auto_split = auto_split
        
        # Headers for user token
        self.headers = {
            'Authorization': self.user_token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        if not self.user_token:
            raise ValueError("Discord User Token not set. Please set DISCORD_USER_TOKEN environment variable or provide user_token parameter.")
        
        if not self.channel_id:
            raise ValueError("Midjourney Channel ID not set. Please set MIDJOURNEY_CHANNEL_ID environment variable or provide channel_id parameter.")
    
    def generate_image(
        self, 
        prompt: str, 
        channel_id: str = None, 
        timeout: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a single image
        
        Args:
            prompt: Image generation prompt
            channel_id: Discord channel ID (default: channel set during initialization)
            timeout: Timeout in seconds
            
        Returns:
            Generation result dictionary or None
        """
        channel_id = channel_id or self.channel_id
        
        if not channel_id:
            raise ValueError("Channel ID is required")
        
        print(f"🎨 Starting image generation: {prompt}")
        
        try:
            # 1. Send slash command
            result = self._send_slash_command(channel_id, prompt)
            
            if not result.get('success'):
                print("❌ Failed to send command")
                return None
            
            print("✅ Command sent successfully, waiting for image generation...")
            
            # 2. Wait for result
            midjourney_result = self._wait_for_result(channel_id, timeout)
            
            if not midjourney_result:
                print("⏰ Timeout: No response from Midjourney")
                return None
            
            print("✅ Image generation completed!")
            
            # 3. Download image
            original_file = self._download_image(midjourney_result, prompt)
            
            if not original_file:
                print("❌ Failed to download image")
                return None
            
            print(f"💾 Image saved: {original_file}")
            
            # 4. Auto-split (optional)
            split_files = []
            if self.auto_split:
                split_files = self._split_image(original_file)
                if split_files:
                    print(f"🔪 Auto-split completed: {len(split_files)} files")
            
            # 5. Return result
            return {
                'success': True,
                'prompt': prompt,
                'original_file': original_file,
                'split_files': split_files,
                'message_id': midjourney_result.get('message_id'),
                'timestamp': datetime.now().isoformat(),
                'total_files': len(split_files) + 1
            }
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            return None
    
    def generate_batch(
        self, 
        prompts: List[str], 
        channel_id: str = None, 
        delay: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images in batch
        
        Args:
            prompts: List of prompts
            channel_id: Discord channel ID
            delay: Delay between requests in seconds
            
        Returns:
            List of generation results
        """
        print(f"🎨 Starting batch image generation: {len(prompts)} images")
        print("=" * 60)
        
        results = []
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n📷 {i}/{len(prompts)}: {prompt}")
            
            result = self.generate_image(prompt, channel_id)
            results.append(result)
            
            if result and result.get('success'):
                print(f"✅ Completed: {result['total_files']} files")
            else:
                print(f"❌ Failed: {prompt}")
            
            # Wait if not the last one
            if i < len(prompts):
                print(f"⏳ Waiting {delay} seconds...")
                time.sleep(delay)
        
        # Result summary
        successful = [r for r in results if r and r.get('success')]
        print(f"\n🎉 Batch generation completed: {len(successful)}/{len(prompts)} successful")
        
        return results
    
    def _send_slash_command(self, channel_id: str, prompt: str) -> Dict[str, Any]:
        """Send slash command"""
        try:
            # Find server ID from channel info
            channel_response = requests.get(
                f"{self.base_url}/channels/{channel_id}",
                headers=self.headers
            )
            
            if channel_response.status_code != 200:
                raise Exception(f"Failed to get channel info: {channel_response.status_code}")
            
            guild_id = channel_response.json().get('guild_id')
            if not guild_id:
                raise Exception("Could not find server ID")
            
            # Slash command data
            data = {
                "type": 2,  # APPLICATION_COMMAND
                "application_id": "936929561302675456",  # Midjourney Bot ID
                "guild_id": guild_id,
                "channel_id": channel_id,
                "session_id": "1234567890abcdef",
                "data": {
                    "version": "1237876415471554623",  # Current actual version
                    "id": "938956540159881230",  # Current actual ID
                    "name": "imagine",
                    "type": 1,
                    "options": [
                        {
                            "type": 3,  # STRING
                            "name": "prompt",
                            "value": prompt
                        }
                    ],
                    "application_command": {
                        "id": "938956540159881230",
                        "application_id": "936929561302675456",
                        "version": "1237876415471554623",
                        "type": 1,
                        "name": "imagine",
                        "description": "Create images with Midjourney",
                        "options": [
                            {
                                "type": 3,
                                "name": "prompt",
                                "description": "The prompt to imagine",
                                "required": True
                            }
                        ]
                    }
                }
            }
            
            # Call Discord Interactions API
            response = requests.post(
                f"{self.base_url}/interactions",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 204:
                return {"success": True, "message": "Slash command sent"}
            else:
                raise Exception(f"Slash command failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Slash command error: {e}")
    
    def _wait_for_result(self, channel_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """Wait for Midjourney result"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self._get_messages(channel_id, limit=10)
            
            for message in messages:
                # Check recent Midjourney Bot messages within 5 minutes
                if (message.get('author', {}).get('id') == '936929561302675456' and 
                    message.get('attachments')):
                    
                    message_time = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                    if (datetime.now(message_time.tzinfo) - message_time).total_seconds() < 300:
                        
                        for attachment in message['attachments']:
                            if attachment.get('content_type', '').startswith('image/'):
                                return {
                                    'message_id': message['id'],
                                    'image_url': attachment['url'],
                                    'filename': attachment.get('filename', 'image.png'),
                                    'content': message.get('content', ''),
                                    'timestamp': message['timestamp']
                                }
            
            time.sleep(5)
        
        return None
    
    def _get_messages(self, channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get message list"""
        params = {'limit': limit}
        response = requests.get(
            f"{self.base_url}/channels/{channel_id}/messages",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def _download_image(self, midjourney_result: dict, prompt: str) -> Optional[str]:
        """Download image"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')[:30]
            filename = f"images/{timestamp}_{safe_prompt}_midjourney.png"
            
            # Create images folder
            os.makedirs("images", exist_ok=True)
            
            # Download
            response = requests.get(midjourney_result['image_url'])
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return filename
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def _split_image(self, image_path: str) -> List[str]:
        """Split image into 4 parts"""
        try:
            # Open image
            img = Image.open(image_path)
            width, height = img.size
            
            # Create split folder
            split_dir = "images/split"
            os.makedirs(split_dir, exist_ok=True)
            
            # Prepare filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # Calculate quarter coordinates
            half_width = width // 2
            half_height = height // 2
            
            # Define 4 regions (top-left, top-right, bottom-left, bottom-right)
            regions = [
                (0, 0, half_width, half_height),           # Top-left (1)
                (half_width, 0, width, half_height),       # Top-right (2)
                (0, half_height, half_width, height),      # Bottom-left (3)
                (half_width, half_height, width, height)   # Bottom-right (4)
            ]
            
            split_files = []
            
            for i, (left, top, right, bottom) in enumerate(regions, 1):
                # Crop region
                cropped = img.crop((left, top, right, bottom))
                
                # Generate filename
                output_file = os.path.join(split_dir, f"{base_name}_part{i}.png")
                
                # Save
                cropped.save(output_file)
                split_files.append(output_file)
            
            return split_files
            
        except Exception as e:
            print(f"❌ Split failed: {e}")
            return []
    
    def set_channel(self, channel_id: str):
        """Set default channel"""
        self.channel_id = channel_id
    
    def get_channel_info(self, channel_id: str = None) -> Dict[str, Any]:
        """Get channel information"""
        channel_id = channel_id or self.channel_id
        response = requests.get(f"{self.base_url}/channels/{channel_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()


# Convenience functions
def quick_generate(prompt: str, 
                  user_token: str = None, 
                  channel_id: str = None,
                  auto_split: bool = True) -> Optional[Dict[str, Any]]:
    """Quick image generation function"""
    client = MidjourneyClient(user_token, channel_id, auto_split)
    return client.generate_image(prompt) 