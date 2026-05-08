"""
Test bot human names specifically
"""
import requests

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

def test_bot_human_names():
    print("\n" + "="*80)
    print("E. BOT HUMAN NAMES VERIFICATION")
    print("="*80)
    
    print("\nFetching trending posts to check bot names:")
    response = requests.get(f"{API_URL}/posts/trending")
    
    if response.status_code != 200:
        print(f"❌ FAIL | Fetch trending posts - Expected 200 but got {response.status_code}")
        return
    
    posts = response.json()
    print(f"✅ PASS | Fetch trending posts - Found {len(posts)} posts")
    
    bot_posts = [p for p in posts if p.get("is_bot") is True]
    print(f"\nFound {len(bot_posts)} bot posts")
    
    if len(bot_posts) == 0:
        print("⚠️  WARNING: No bot posts found in trending.")
        return
    
    passed_count = 0
    failed_count = 0
    
    print("\nChecking bot names:")
    for i, post in enumerate(bot_posts, 1):
        sudo_name = post.get("sudo_name")
        content_preview = post.get("content", "")[:50]
        
        if sudo_name:
            # Check if it's a real human name format: "FirstName LastName"
            parts = sudo_name.split()
            
            # Must be exactly 2 words
            if len(parts) != 2:
                print(f"❌ FAIL | Bot post #{i}: '{sudo_name}' - Not exactly 2 words")
                print(f"         Content: {content_preview}")
                failed_count += 1
                continue
            
            first_name, last_name = parts
            
            # Both must start with capital letter
            if not (first_name[0].isupper() and last_name[0].isupper()):
                print(f"❌ FAIL | Bot post #{i}: '{sudo_name}' - Not properly capitalized")
                print(f"         Content: {content_preview}")
                failed_count += 1
                continue
            
            # Should not contain digits (old-style usernames like "lonelyfox42")
            if any(char.isdigit() for char in sudo_name):
                print(f"❌ FAIL | Bot post #{i}: '{sudo_name}' - Contains digits (old-style username)")
                print(f"         Content: {content_preview}")
                failed_count += 1
                continue
            
            # Check it's not old-style username patterns
            old_style_patterns = ["voidkitten", "lonelyfox", "ghostnova", "ghost42"]
            if any(pattern in sudo_name.lower() for pattern in old_style_patterns):
                print(f"❌ FAIL | Bot post #{i}: '{sudo_name}' - Old-style username pattern")
                print(f"         Content: {content_preview}")
                failed_count += 1
                continue
            
            # All checks passed
            print(f"✅ PASS | Bot post #{i}: '{sudo_name}'")
            print(f"         Content: {content_preview}")
            passed_count += 1
        else:
            print(f"❌ FAIL | Bot post #{i} - No sudo_name found")
            print(f"         Content: {content_preview}")
            failed_count += 1
    
    print("\n" + "="*80)
    print(f"Bot Name Tests: {passed_count} passed, {failed_count} failed")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_bot_human_names()
