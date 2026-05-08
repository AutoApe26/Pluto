"""
Pluto Backend Testing - Content Moderation & Rate Limiting
Tests moderation rules, same-content rate limit, reaction toggle, and bot names.
"""
import requests
import json
import uuid
from typing import Dict, Any

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

def new_device_id():
    """Generate a unique device ID for testing."""
    return f"test-{uuid.uuid4().hex[:12]}"

def post_content(content: str, topic: str = "rant", device_id: str = None) -> requests.Response:
    """Helper to POST content to /api/posts."""
    if device_id is None:
        device_id = new_device_id()
    payload = {
        "content": content,
        "topic": topic,
        "device_id": device_id
    }
    return requests.post(f"{API_URL}/posts", json=payload)

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with formatting."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"     {details}")

def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

# ============================================================================
# A. MODERATION RULE ENFORCEMENT
# ============================================================================
def test_moderation_rules():
    print_section("A. MODERATION RULE ENFORCEMENT")
    
    test_cases = [
        ("I want to die tonight", "self-harm", "Blocked: self-harm."),
        ("going to kill myself", "self-harm", "Blocked: self-harm."),
        ("k!ll myself", "self-harm", "Blocked: self-harm."),
        ("k.i.l.l m.y.s.e.l.f", "self-harm", "Blocked: self-harm."),
        ("kiiillll myselfffff", "self-harm", "Blocked: self-harm."),
        ("kill yourself loser", "hate/harassment", "Blocked: hate/harassment."),
        ("imma kill you", "hate/harassment", "Blocked: hate/harassment."),
        ("send nudes", "sexual content", "Blocked: sexual content."),
        ("let's fuck tonight", "sexual content", "Blocked: sexual content."),
        ("check https://malicious.com", "link blocked", "Links aren't allowed on Pluto."),
        ("see www.scammer.io", "link blocked", "Links aren't allowed on Pluto."),
        ("send your seed phrase here", "scams/wallet-drainers", "Blocked: scams/wallet-drainers."),
        ("build a pipe bomb tutorial", "terror promotion", "Blocked: terror promotion."),
        ("her address is 12 main st", "doxxing", "Blocked: doxxing."),
        ("vaccines cause autism", "misinformation", "Blocked: misinformation."),
    ]
    
    passed_count = 0
    failed_count = 0
    
    for content, category, expected_reason in test_cases:
        device_id = "qa-mod-1"
        response = post_content(content, "rant", device_id)
        
        if response.status_code == 400:
            try:
                error_detail = response.json().get("detail", "")
                if expected_reason in error_detail:
                    print_result(f"{category}: '{content[:40]}'", True)
                    passed_count += 1
                else:
                    print_result(f"{category}: '{content[:40]}'", False, 
                               f"Expected '{expected_reason}' but got '{error_detail}'")
                    failed_count += 1
            except:
                print_result(f"{category}: '{content[:40]}'", False, 
                           f"Status 400 but invalid JSON response: {response.text}")
                failed_count += 1
        else:
            print_result(f"{category}: '{content[:40]}'", False, 
                       f"Expected 400 but got {response.status_code}: {response.text[:100]}")
            failed_count += 1
    
    print(f"\nModeration Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# B. LEGITIMATE CONTENT SHOULD PASS
# ============================================================================
def test_legitimate_content():
    print_section("B. LEGITIMATE CONTENT SHOULD PASS")
    
    test_cases = [
        "My therapist said I am doing great",
        "Lost a friend to suicide last year, still hurts",
        "I'm sad and tired, just venting",
        "this game is wild",
        "feeling really good today",
    ]
    
    passed_count = 0
    failed_count = 0
    
    for content in test_cases:
        device_id = new_device_id()
        response = post_content(content, "rant", device_id)
        
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                if "id" in data and data.get("content"):
                    print_result(f"'{content[:40]}'", True)
                    passed_count += 1
                else:
                    print_result(f"'{content[:40]}'", False, 
                               f"Status {response.status_code} but invalid response structure")
                    failed_count += 1
            except:
                print_result(f"'{content[:40]}'", False, 
                           f"Status {response.status_code} but invalid JSON: {response.text}")
                failed_count += 1
        else:
            print_result(f"'{content[:40]}'", False, 
                       f"Expected 200/201 but got {response.status_code}: {response.text[:100]}")
            failed_count += 1
    
    print(f"\nLegitimate Content Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# C. SAME-CONTENT RATE LIMIT (5×/24h)
# ============================================================================
def test_same_content_rate_limit():
    print_section("C. SAME-CONTENT RATE LIMIT (5×/24h)")
    
    device_id = "qa-dedup-1"
    test_content = "this is a unique dedup test message"
    different_content = "this is a completely different message for testing"
    
    passed_tests = []
    failed_tests = []
    
    # Test 1-5: Should all succeed
    print("\nPosting same content 5 times (should all succeed):")
    for i in range(1, 6):
        response = post_content(test_content, "rant", device_id)
        if response.status_code in [200, 201]:
            print_result(f"Post #{i} with same content", True)
            passed_tests.append(f"Post #{i}")
        else:
            print_result(f"Post #{i} with same content", False, 
                       f"Expected 200/201 but got {response.status_code}: {response.text[:100]}")
            failed_tests.append(f"Post #{i}")
    
    # Test 6: Should fail with 429
    print("\nPosting same content 6th time (should fail with 429):")
    response = post_content(test_content, "rant", device_id)
    if response.status_code == 429:
        try:
            error_detail = response.json().get("detail", "")
            if "Same content max 5×/24h." in error_detail:
                print_result("6th post with same content blocked", True)
                passed_tests.append("6th post blocked")
            else:
                print_result("6th post with same content blocked", False, 
                           f"Expected 'Same content max 5×/24h.' but got '{error_detail}'")
                failed_tests.append("6th post blocked")
        except:
            print_result("6th post with same content blocked", False, 
                       f"Status 429 but invalid JSON: {response.text}")
            failed_tests.append("6th post blocked")
    else:
        print_result("6th post with same content blocked", False, 
                   f"Expected 429 but got {response.status_code}: {response.text[:100]}")
        failed_tests.append("6th post blocked")
    
    # Test 7: Different content should still work
    print("\nPosting different content from same device (should succeed):")
    response = post_content(different_content, "rant", device_id)
    if response.status_code in [200, 201]:
        print_result("Different content after rate limit", True)
        passed_tests.append("Different content")
    else:
        print_result("Different content after rate limit", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:100]}")
        failed_tests.append("Different content")
    
    print(f"\nRate Limit Tests: {len(passed_tests)} passed, {len(failed_tests)} failed")
    return len(passed_tests), len(failed_tests)

# ============================================================================
# D. REACTION TOGGLE/SWITCH
# ============================================================================
def test_reaction_toggle_switch():
    print_section("D. REACTION TOGGLE/SWITCH")
    
    device_id = "qa-react-1"
    passed_tests = []
    failed_tests = []
    
    # Create a fresh post
    print("\nCreating a fresh post for reaction testing:")
    create_response = post_content("Test post for reactions", "rant", new_device_id())
    if create_response.status_code not in [200, 201]:
        print_result("Create test post", False, f"Failed to create post: {create_response.text}")
        return 0, 1
    
    post_id = create_response.json()["id"]
    print_result("Create test post", True, f"Post ID: {post_id}")
    
    # Test 1: Add hug reaction
    print("\nTest 1: Add hug reaction (hugs should become 1):")
    response = requests.post(
        f"{API_URL}/posts/{post_id}/reaction",
        json={"type": "hug", "device_id": device_id}
    )
    if response.status_code == 200:
        # Verify hugs count
        my_reaction = requests.get(f"{API_URL}/posts/{post_id}/my-reaction", params={"device_id": device_id})
        if my_reaction.status_code == 200 and my_reaction.json().get("type") == "hug":
            print_result("Add hug reaction", True)
            passed_tests.append("Add hug")
        else:
            print_result("Add hug reaction", False, f"Reaction not recorded correctly: {my_reaction.text}")
            failed_tests.append("Add hug")
    else:
        print_result("Add hug reaction", False, f"Expected 200 but got {response.status_code}: {response.text}")
        failed_tests.append("Add hug")
    
    # Test 2: Toggle off hug (hugs should become 0)
    print("\nTest 2: Toggle off hug (hugs should become 0, my-reaction null):")
    response = requests.post(
        f"{API_URL}/posts/{post_id}/reaction",
        json={"type": "hug", "device_id": device_id}
    )
    if response.status_code == 200:
        my_reaction = requests.get(f"{API_URL}/posts/{post_id}/my-reaction", params={"device_id": device_id})
        if my_reaction.status_code == 200 and my_reaction.json().get("type") is None:
            print_result("Toggle off hug", True)
            passed_tests.append("Toggle off")
        else:
            print_result("Toggle off hug", False, f"Reaction not removed: {my_reaction.text}")
            failed_tests.append("Toggle off")
    else:
        print_result("Toggle off hug", False, f"Expected 200 but got {response.status_code}: {response.text}")
        failed_tests.append("Toggle off")
    
    # Test 3: Add hug again (hugs should become 1)
    print("\nTest 3: Add hug again (hugs should become 1):")
    response = requests.post(
        f"{API_URL}/posts/{post_id}/reaction",
        json={"type": "hug", "device_id": device_id}
    )
    if response.status_code == 200:
        my_reaction = requests.get(f"{API_URL}/posts/{post_id}/my-reaction", params={"device_id": device_id})
        if my_reaction.status_code == 200 and my_reaction.json().get("type") == "hug":
            print_result("Add hug again", True)
            passed_tests.append("Add hug again")
        else:
            print_result("Add hug again", False, f"Reaction not recorded: {my_reaction.text}")
            failed_tests.append("Add hug again")
    else:
        print_result("Add hug again", False, f"Expected 200 but got {response.status_code}: {response.text}")
        failed_tests.append("Add hug again")
    
    # Test 4: Switch to fug (hugs=0, fugs=1)
    print("\nTest 4: Switch to fug (hugs should become 0, fugs should become 1):")
    response = requests.post(
        f"{API_URL}/posts/{post_id}/reaction",
        json={"type": "fug", "device_id": device_id}
    )
    if response.status_code == 200:
        my_reaction = requests.get(f"{API_URL}/posts/{post_id}/my-reaction", params={"device_id": device_id})
        if my_reaction.status_code == 200 and my_reaction.json().get("type") == "fug":
            print_result("Switch to fug", True)
            passed_tests.append("Switch to fug")
        else:
            print_result("Switch to fug", False, f"Reaction not switched: {my_reaction.text}")
            failed_tests.append("Switch to fug")
    else:
        print_result("Switch to fug", False, f"Expected 200 but got {response.status_code}: {response.text}")
        failed_tests.append("Switch to fug")
    
    # Test 5: Verify only ONE reaction at a time
    print("\nTest 5: Verify only ONE reaction at a time (should be 'fug'):")
    my_reaction = requests.get(f"{API_URL}/posts/{post_id}/my-reaction", params={"device_id": device_id})
    if my_reaction.status_code == 200:
        reaction_type = my_reaction.json().get("type")
        if reaction_type == "fug":
            print_result("Only one reaction at a time", True)
            passed_tests.append("One reaction only")
        else:
            print_result("Only one reaction at a time", False, f"Expected 'fug' but got '{reaction_type}'")
            failed_tests.append("One reaction only")
    else:
        print_result("Only one reaction at a time", False, f"Failed to get reaction: {my_reaction.text}")
        failed_tests.append("One reaction only")
    
    print(f"\nReaction Tests: {len(passed_tests)} passed, {len(failed_tests)} failed")
    return len(passed_tests), len(failed_tests)

# ============================================================================
# E. BOT HUMAN NAMES
# ============================================================================
def test_bot_human_names():
    print_section("E. BOT HUMAN NAMES")
    
    print("\nFetching trending posts to check bot names:")
    response = requests.get(f"{API_URL}/posts/trending")
    
    if response.status_code != 200:
        print_result("Fetch trending posts", False, f"Expected 200 but got {response.status_code}: {response.text}")
        return 0, 1
    
    posts = response.json()
    print_result("Fetch trending posts", True, f"Found {len(posts)} posts")
    
    bot_posts = [p for p in posts if p.get("is_bot") is True]
    print(f"\nFound {len(bot_posts)} bot posts")
    
    if len(bot_posts) == 0:
        print("⚠️  WARNING: No bot posts found in trending. Cannot verify bot names.")
        print("    This might be expected if bots haven't run yet.")
        return 0, 0
    
    passed_count = 0
    failed_count = 0
    
    for i, post in enumerate(bot_posts[:10], 1):  # Check first 10 bot posts
        sudo_name = post.get("sudo_name")
        if sudo_name:
            # Check if it's a real human name format: "FirstName LastName"
            parts = sudo_name.split()
            if len(parts) == 2 and parts[0][0].isupper() and parts[1][0].isupper():
                # Check it's not old-style username
                if not any(char.isdigit() for char in sudo_name) and sudo_name.lower() not in [
                    "voidkitten", "lonelyfox42", "ghostnova", "ghost42"
                ]:
                    print_result(f"Bot post #{i}: '{sudo_name}'", True)
                    passed_count += 1
                else:
                    print_result(f"Bot post #{i}: '{sudo_name}'", False, 
                               "Contains digits or old-style username")
                    failed_count += 1
            else:
                print_result(f"Bot post #{i}: '{sudo_name}'", False, 
                           "Not in 'FirstName LastName' format")
                failed_count += 1
        else:
            print_result(f"Bot post #{i}", False, "No sudo_name found")
            failed_count += 1
    
    print(f"\nBot Name Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print("\n" + "="*80)
    print("PLUTO BACKEND TESTING - Content Moderation & Rate Limiting")
    print("="*80)
    
    total_passed = 0
    total_failed = 0
    
    # Run all test sections
    try:
        passed, failed = test_moderation_rules()
        total_passed += passed
        total_failed += failed
    except Exception as e:
        print(f"\n❌ Section A failed with exception: {e}")
        total_failed += 1
    
    try:
        passed, failed = test_legitimate_content()
        total_passed += passed
        total_failed += failed
    except Exception as e:
        print(f"\n❌ Section B failed with exception: {e}")
        total_failed += 1
    
    try:
        passed, failed = test_same_content_rate_limit()
        total_passed += passed
        total_failed += failed
    except Exception as e:
        print(f"\n❌ Section C failed with exception: {e}")
        total_failed += 1
    
    try:
        passed, failed = test_reaction_toggle_switch()
        total_passed += passed
        total_failed += failed
    except Exception as e:
        print(f"\n❌ Section D failed with exception: {e}")
        total_failed += 1
    
    try:
        passed, failed = test_bot_human_names()
        total_passed += passed
        total_failed += failed
    except Exception as e:
        print(f"\n❌ Section E failed with exception: {e}")
        total_failed += 1
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {total_passed}/{total_passed + total_failed} ({100*total_passed/(total_passed+total_failed) if (total_passed+total_failed) > 0 else 0:.1f}%)")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
