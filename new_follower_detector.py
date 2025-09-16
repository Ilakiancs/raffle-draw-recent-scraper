#!/usr/bin/env python3
"""
New Follower Detection System
Compares current followers with previous snapshots to find truly new followers.

USAGE:
1. First time setup (create baseline):
   python3 new_follower_detector.py --create-baseline

2. Detect new followers:
   python3 new_follower_detector.py --detect-new

3. Auto-fetch and detect:
   python3 new_follower_detector.py --auto
"""

import json
import time
import datetime
import os
import sys
import subprocess
import argparse

def fetch_fresh_followers():
    """Fetch fresh follower data from Instagram API"""
    print("🔄 Fetching fresh follower data from Instagram...")
    
    api_command = [
        'curl', '--request', 'GET',
        '--url', 'https://instagram360.p.rapidapi.com/userfollowers/?username_or_id=ieeeras_iit',
        '--header', 'x-rapidapi-host: instagram360.p.rapidapi.com',
        '--header', 'x-rapidapi-key: 9d1ccd9d6fmshf515f96baa1683cp14eed1jsn5b6d08cc4694'
    ]
    
    try:
        result = subprocess.run(api_command, capture_output=True, text=True)
        if result.returncode == 0:
            with open('ieeeras_iit_followers.json', 'w') as f:
                f.write(result.stdout)
            print("✅ Fresh data fetched successfully")
            return True
        else:
            print(f"❌ API call failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return False

def load_current_followers():
    """Load current followers from API response"""
    try:
        with open('ieeeras_iit_followers.json', 'r', encoding='utf-8') as f:
            response_data = json.load(f)
        
        followers = response_data.get('data', {}).get('items', [])
        
        # Extract just the essential info for comparison
        follower_list = []
        for follower in followers:
            follower_info = {
                "id": follower.get("id", ""),
                "username": follower.get("username", ""),
                "full_name": follower.get("full_name", ""),
                "is_private": follower.get("is_private", False),
                "is_verified": follower.get("is_verified", False),
                "profile_pic_url": follower.get("profile_pic_url", ""),
                "latest_story_ts": follower.get("latest_story_ts", 0)
            }
            follower_list.append(follower_info)
        
        print(f"📊 Loaded {len(follower_list)} current followers")
        return follower_list
        
    except Exception as e:
        print(f"❌ Error loading current followers: {e}")
        return []

def save_baseline_snapshot(followers):
    """Save current followers as baseline for future comparison"""
    snapshot_data = {
        "timestamp": time.time(),
        "date": datetime.datetime.now().isoformat(),
        "follower_count": len(followers),
        "followers": followers
    }
    
    with open('baseline_followers.json', 'w', encoding='utf-8') as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Baseline snapshot saved: {len(followers)} followers")
    print(f"📅 Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def load_baseline_snapshot():
    """Load previous baseline snapshot"""
    try:
        with open('baseline_followers.json', 'r', encoding='utf-8') as f:
            snapshot_data = json.load(f)
        
        baseline_followers = snapshot_data.get('followers', [])
        baseline_date = snapshot_data.get('date', 'Unknown')
        
        print(f"📂 Loaded baseline: {len(baseline_followers)} followers from {baseline_date}")
        return baseline_followers
        
    except FileNotFoundError:
        print("❌ No baseline snapshot found. Run with --create-baseline first.")
        return None
    except Exception as e:
        print(f"❌ Error loading baseline: {e}")
        return None

def find_new_followers(current_followers, baseline_followers):
    """Find followers who are in current but not in baseline"""
    
    # Create sets of follower IDs for comparison
    baseline_ids = {follower['id'] for follower in baseline_followers}
    current_ids = {follower['id'] for follower in current_followers}
    
    # Find new follower IDs
    new_follower_ids = current_ids - baseline_ids
    
    # Get full info for new followers
    new_followers = [
        follower for follower in current_followers 
        if follower['id'] in new_follower_ids
    ]
    
    print(f"🆕 Found {len(new_followers)} new followers since baseline!")
    
    if new_followers:
        print("\n🎉 NEW FOLLOWERS:")
        print("=" * 50)
        for i, follower in enumerate(new_followers, 1):
            print(f"{i}. @{follower['username']} - {follower['full_name']}")
    
    return new_followers

def save_new_followers_for_react(new_followers):
    """Save new followers in format expected by React app"""
    
    output_data = {
        "status": "done",
        "fetch_info": {
            "timestamp": time.time(),
            "total_count": len(new_followers),
            "api_source": "instagram360_new_follower_detection",
            "account": "ieeeras_iit",
            "method": "snapshot_comparison",
            "note": f"NEW followers detected by comparing with baseline snapshot"
        },
        "new_followers": new_followers
    }
    
    # Save to React public folder
    output_path = 'public/FINAL-new-followers-with-time.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(new_followers)} NEW followers for React app")
    print(f"📁 File: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Detect new Instagram followers')
    parser.add_argument('--create-baseline', action='store_true', 
                       help='Create baseline snapshot of current followers')
    parser.add_argument('--detect-new', action='store_true',
                       help='Detect new followers since baseline')
    parser.add_argument('--auto', action='store_true',
                       help='Fetch fresh data and detect new followers')
    
    args = parser.parse_args()
    
    if args.create_baseline:
        print("🎯 Creating baseline snapshot...")
        if not os.path.exists('ieeeras_iit_followers.json'):
            print("⚠️  No current data found. Fetching fresh data first...")
            if not fetch_fresh_followers():
                return
        
        current_followers = load_current_followers()
        if current_followers:
            save_baseline_snapshot(current_followers)
            print("✅ Baseline created successfully!")
            print("💡 Now you can use --detect-new to find new followers")
    
    elif args.detect_new:
        print("🔍 Detecting new followers...")
        baseline_followers = load_baseline_snapshot()
        if baseline_followers is None:
            return
        
        current_followers = load_current_followers()
        if not current_followers:
            return
        
        new_followers = find_new_followers(current_followers, baseline_followers)
        save_new_followers_for_react(new_followers)
        
        if new_followers:
            print("🎊 New followers detected and saved for React app!")
        else:
            print("📭 No new followers found since baseline")
    
    elif args.auto:
        print("🚀 Auto-detecting new followers...")
        
        # Step 1: Fetch fresh data
        if not fetch_fresh_followers():
            return
        
        # Step 2: Load baseline
        baseline_followers = load_baseline_snapshot()
        if baseline_followers is None:
            print("💡 No baseline found. Creating one now...")
            current_followers = load_current_followers()
            if current_followers:
                save_baseline_snapshot(current_followers)
                print("✅ Baseline created. Run --auto again to detect new followers")
            return
        
        # Step 3: Detect new followers
        current_followers = load_current_followers()
        if not current_followers:
            return
        
        new_followers = find_new_followers(current_followers, baseline_followers)
        save_new_followers_for_react(new_followers)
        
        if new_followers:
            print("🎊 New followers detected and ready for raffle!")
        else:
            print("📭 No new followers since baseline")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
