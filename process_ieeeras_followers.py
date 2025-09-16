#!/usr/bin/env python3
"""
Process ieeeras_iit Real Followers - Activity-Based Filtering
Processes your real Instagram followers with timestamp analysis.

USAGE:
1. To fetch fresh data from Instagram:
   curl --request GET \
     --url 'https://instagram360.p.rapidapi.com/userfollowers/?username_or_id=ieeeras_iit' \
     --header 'x-rapidapi-host: instagram360.p.rapidapi.com' \
     --header 'x-rapidapi-key: YOUR_API_KEY' > ieeeras_iit_followers.json

2. To process the data for React app:
   python3 process_ieeeras_followers.py

3. Refresh your React app to see updated followers
"""

import json
import time
import datetime
import os

def process_ieeeras_followers():
    """Process the ieeeras_iit followers response"""
    
    # Load your real followers data
    try:
        with open('ieeeras_iit_followers.json', 'r', encoding='utf-8') as f:
            response_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading ieeeras_iit followers: {e}")
        return
    
    current_time = time.time()
    followers = response_data.get('data', {}).get('items', [])
    
    print(f"🎯 Processing {len(followers)} REAL followers from @ieeeras_iit...")
    print("=" * 60)
    
    # Categorize followers by their story activity timestamps
    categorized_followers = []
    activity_counts = {
        'active_15min': 0,
        'active_30min': 0, 
        'active_1hour': 0,
        'active_24hour': 0,
        'no_activity': 0
    }
    
    recent_activity_found = []
    
    for follower in followers:
        # Convert to our standard format
        processed_follower = {
            "pk": follower.get("id", ""),
            "id": follower.get("id", ""),
            "username": follower.get("username", ""),
            "full_name": follower.get("full_name", ""),
            "is_private": follower.get("is_private", False),
            "is_verified": follower.get("is_verified", False),
            "profile_pic_url": follower.get("profile_pic_url", "")
        }
        
        # Analyze story activity timestamp
        latest_story = follower.get("latest_story_ts")
        
        if latest_story and latest_story > 0:
            time_diff_minutes = (current_time - latest_story) / 60
            
            # Convert timestamp to readable format for logging
            story_time = datetime.datetime.fromtimestamp(latest_story).strftime('%Y-%m-%d %H:%M:%S')
            
            if time_diff_minutes <= 15:
                processed_follower["time_category"] = "active_15min"
                activity_counts['active_15min'] += 1
                recent_activity_found.append(f"  ✨ {processed_follower['full_name'][:30]:30} | Active 15min ago ({story_time})")
            elif time_diff_minutes <= 30:
                processed_follower["time_category"] = "active_30min"
                activity_counts['active_30min'] += 1
                recent_activity_found.append(f"  🔥 {processed_follower['full_name'][:30]:30} | Active 30min ago ({story_time})")
            elif time_diff_minutes <= 60:
                processed_follower["time_category"] = "active_1hour"
                activity_counts['active_1hour'] += 1
                recent_activity_found.append(f"  ⚡ {processed_follower['full_name'][:30]:30} | Active 1hour ago ({story_time})")
            elif time_diff_minutes <= 1440:  # 24 hours
                processed_follower["time_category"] = "active_24hour"
                activity_counts['active_24hour'] += 1
            else:
                processed_follower["time_category"] = "older_activity"
        else:
            processed_follower["time_category"] = "no_recent_activity"
            activity_counts['no_activity'] += 1
        
        categorized_followers.append(processed_follower)
    
    # Create output for React app
    output_data = {
        "status": "done",
        "fetch_info": {
            "timestamp": current_time,
            "total_count": len(categorized_followers),
            "api_source": "instagram360_real_account",
            "account": "ieeeras_iit",
            "method": "real_activity_based_filtering",
            "note": "Real followers from @ieeeras_iit with genuine activity timestamps",
            "activity_breakdown": {
                "active_15min": activity_counts['active_15min'],
                "active_30min": activity_counts['active_30min'],
                "active_1hour": activity_counts['active_1hour'],
                "active_24hour": activity_counts['active_24hour'],
                "no_activity": activity_counts['no_activity']
            },
            "time_breakdown": {
                "15min": activity_counts['active_15min'],
                "30min": activity_counts['active_30min'],
                "1hour": activity_counts['active_1hour'],
                "all": len(categorized_followers)
            }
        },
        "new_followers": categorized_followers
    }
    
    # Save to React app data file
    output_file = "public/FINAL-new-followers-with-time.json"
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Successfully saved {len(categorized_followers)} REAL followers to {output_file}")
    except Exception as e:
        print(f"❌ Error saving output: {e}")
        return
    
    # Print comprehensive report
    print("\n" + "=" * 60)
    print("🎯 @IEEERAS_IIT REAL FOLLOWERS REPORT")
    print("=" * 60)
    
    print(f"\n⚡ Real Activity Analysis (your actual followers):")
    print(f"  🔥 Active in last 15min: {activity_counts['active_15min']} followers")
    print(f"  🔥 Active in last 30min: {activity_counts['active_30min']} followers")
    print(f"  🔥 Active in last 1hour: {activity_counts['active_1hour']} followers")
    print(f"  🔥 Active in last 24hour: {activity_counts['active_24hour']} followers")
    print(f"  😴 No recent activity: {activity_counts['no_activity']} followers")
    
    print(f"\n🎮 Your React App Will Show:")
    print(f"  ⏰ Last 15 Minutes: {activity_counts['active_15min']} participants")
    print(f"  ⏰ Last 30 Minutes: {activity_counts['active_30min']} participants")
    print(f"  ⏰ Last Hour: {activity_counts['active_1hour']} participants")
    print(f"  ⏰ All Followers: {len(categorized_followers)} participants")
    
    if recent_activity_found:
        print(f"\n✨ Recent Activity Detected:")
        for activity in recent_activity_found[:10]:  # Show first 10
            print(activity)
        if len(recent_activity_found) > 10:
            print(f"  ... and {len(recent_activity_found) - 10} more")
    
    # Sample real followers
    print(f"\n👥 Sample Real Followers (from @ieeeras_iit):")
    for i, follower in enumerate(categorized_followers[:8], 1):
        name = follower.get('full_name', 'No name')[:25]
        username = follower.get('username', '')[:20] 
        private = "🔒" if follower.get('is_private') else "🔓"
        print(f"  {i}. {name:25} (@{username:20}) {private}")
    
    print(f"\n✅ SUCCESS: Your raffle now uses 100% REAL data from @ieeeras_iit!")
    print(f"🚀 No fake or demo data - these are your genuine Instagram followers!")
    print("=" * 60)

if __name__ == "__main__":
    process_ieeeras_followers()
