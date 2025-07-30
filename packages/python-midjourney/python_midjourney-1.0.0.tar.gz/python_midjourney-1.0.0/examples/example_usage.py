#!/usr/bin/env python3
"""
🎨 Python Midjourney Usage Examples
"""

import os

from python_midjourney import MidjourneyClient, quick_generate


def example_basic_usage():
    """Basic usage example"""
    print("🎯 Basic Usage Example")
    print("=" * 40)
    
    try:
        # Create client (automatically uses environment variables)
        client = MidjourneyClient()
        
        # Generate image
        result = client.generate_image("a beautiful sunset over mountains")
        
        if result and result['success']:
            print("✅ Image generation successful!")
            print(f"Original file: {result['original_file']}")
            print(f"Split files: {len(result['split_files'])} files")
            for i, file in enumerate(result['split_files'], 1):
                print(f"  {i}. {file}")
        else:
            print("❌ Image generation failed")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")


def example_direct_token():
    """Direct token specification example"""
    print("\n🔑 Direct Token Specification Example")
    print("=" * 40)
    
    # For actual use, enter real tokens here
    user_token = os.getenv("DISCORD_USER_TOKEN")
    channel_id = os.getenv("MIDJOURNEY_CHANNEL_ID")
    
    if not user_token or not channel_id:
        print("❌ Environment variables not set.")
        print("   Please set DISCORD_USER_TOKEN and MIDJOURNEY_CHANNEL_ID.")
        return
    
    try:
        # Specify token and channel ID directly
        client = MidjourneyClient(
            user_token=user_token,
            channel_id=channel_id,
            auto_split=True  # Enable auto-split
        )
        
        result = client.generate_image("cyberpunk city landscape")
        
        if result and result['success']:
            print("✅ Image generation successful!")
            print(f"Prompt: {result['prompt']}")
            print(f"Total files: {result['total_files']} files")
        else:
            print("❌ Image generation failed")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")


def example_batch_processing():
    """Batch processing example"""
    print("\n📦 Batch Processing Example")
    print("=" * 40)
    
    try:
        client = MidjourneyClient()
        
        prompts = [
            "cozy coffee shop with warm lighting",
            "modern minimalist workspace"
        ]
        
        print(f"Starting batch processing: {len(prompts)} prompts")
        
        # Batch generation (3 second intervals)
        results = client.generate_batch(prompts, delay=3)
        
        # Check results
        successful = 0
        for i, result in enumerate(results):
            if result and result['success']:
                successful += 1
                print(f"✅ Image {i+1}: {result['total_files']} files generated")
            else:
                print(f"❌ Image {i+1}: Failed")
        
        print(f"\n🎉 Batch processing completed: {successful}/{len(results)} successful")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")


def example_quick_generate():
    """Quick generation function example"""
    print("\n⚡ Quick Generation Function Example")
    print("=" * 40)
    
    try:
        # Generate image in one line
        result = quick_generate("fantasy castle in the clouds")
        
        if result and result['success']:
            print("✅ Quick generation successful!")
            print(f"Original: {result['original_file']}")
            print(f"Split: {len(result['split_files'])} files")
        else:
            print("❌ Quick generation failed")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")


def example_no_split():
    """Auto-split disabled example"""
    print("\n🚫 Auto-Split Disabled Example")
    print("=" * 40)
    
    try:
        # Save original image only (no splitting)
        client = MidjourneyClient(auto_split=False)
        result = client.generate_image("abstract art")
        
        if result and result['success']:
            print("✅ Original only save completed!")
            print(f"Original file: {result['original_file']}")
            print(f"Split files: {len(result['split_files'])} files (splitting disabled)")
        else:
            print("❌ Image generation failed")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")


def example_channel_info():
    """Channel information check example"""
    print("\n🔍 Channel Information Check Example")
    print("=" * 40)
    
    try:
        client = MidjourneyClient()
        
        # Get current channel information
        info = client.get_channel_info()
        print("✅ Channel information:")
        print(f"   Channel ID: {info.get('id')}")
        print(f"   Channel name: {info.get('name')}")
        print(f"   Channel type: {info.get('type')}")
        print(f"   Server ID: {info.get('guild_id')}")
        
    except Exception as e:
        print(f"❌ Failed to get channel information: {e}")


def main():
    """Main function"""
    print("🎨 Python Midjourney Package Usage Examples")
    print("=" * 50)
    
    # Check environment variables
    if not os.getenv("DISCORD_USER_TOKEN"):
        print("❌ DISCORD_USER_TOKEN environment variable not set.")
        print("   Set command: export DISCORD_USER_TOKEN='token'")
        return
    
    if not os.getenv("MIDJOURNEY_CHANNEL_ID"):
        print("❌ MIDJOURNEY_CHANNEL_ID environment variable not set.")
        print("   Set command: export MIDJOURNEY_CHANNEL_ID='channel_id'")
        return
    
    print("✅ Environment variable setup confirmed!")
    
    # Run examples
    example_basic_usage()
    example_direct_token()
    example_batch_processing()
    example_quick_generate()
    example_no_split()
    example_channel_info()
    
    print("\n🎉 All examples execution completed!")
    print("📂 Generated files:")
    print("   - images/ : Original images")
    print("   - images/split/ : Split images")


if __name__ == "__main__":
    main() 