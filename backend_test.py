#!/usr/bin/env python3
"""
Pluto v1.2 Backend Test Suite
Tests all 4 v1.2 features + regression checks
"""

import requests
import time
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend/.env
BASE_URL = "https://pluto-share-fix.preview.emergentagent.com/api"
MOD_KEY = "pluto-mod-2026"

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_pass(test_name: str, details: str = ""):
    """Log a passing test"""
    msg = f"✅ PASS: {test_name}"
    if details:
        msg += f" - {details}"
    print(msg)
    test_results["passed"].append(test_name)

def log_fail(test_name: str, details: str):
    """Log a failing test"""
    msg = f"❌ FAIL: {test_name} - {details}"
    print(msg)
    test_results["failed"].append(f"{test_name}: {details}")

def log_warn(test_name: str, details: str):
    """Log a warning"""
    msg = f"⚠️  WARN: {test_name} - {details}"
    print(msg)
    test_results["warnings"].append(f"{test_name}: {details}")

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ============================================================
# TEST 1: GET /api/posts/{id} - Single post fetch
# ============================================================
def test_single_post_fetch():
    print_section("TEST 1: GET /api/posts/{id} - Single Post Fetch")
    
    # First create a post to fetch
    create_payload = {
        "content": "single fetch v12 test post for GET endpoint",
        "topic": "stories",
        "device_id": "qa-v12-getpost-1"
    }
    
    print("Creating test post...")
    resp = requests.post(f"{BASE_URL}/posts", json=create_payload)
    if resp.status_code not in [200, 201]:
        log_fail("1a. Create post for GET test", f"Status {resp.status_code}: {resp.text}")
        return
    
    post_data = resp.json()
    post_id = post_data.get("id")
    if not post_id:
        log_fail("1a. Create post for GET test", "No id in response")
        return
    
    log_pass("1a. Create post for GET test", f"Created post {post_id}")
    
    # Test GET /api/posts/{id} with valid id
    print(f"Fetching post {post_id}...")
    resp = requests.get(f"{BASE_URL}/posts/{post_id}")
    if resp.status_code != 200:
        log_fail("1b. GET /api/posts/{id} with valid id", f"Status {resp.status_code}: {resp.text}")
        return
    
    fetched = resp.json()
    
    # Verify required fields are present
    required_fields = ["id", "content", "topic", "hugs", "fugs", "lang", "is_lyrics"]
    missing_fields = [f for f in required_fields if f not in fetched]
    if missing_fields:
        log_fail("1b. GET /api/posts/{id} response fields", f"Missing fields: {missing_fields}")
    else:
        log_pass("1b. GET /api/posts/{id} response fields", f"All required fields present")
    
    # Verify internal fields are NOT present
    internal_fields = ["content_norm", "translation_en"]
    present_internal = [f for f in internal_fields if f in fetched]
    if present_internal:
        log_fail("1c. Internal fields stripped", f"Internal fields present: {present_internal}")
    else:
        log_pass("1c. Internal fields stripped", "content_norm and translation_en not in response")
    
    # Verify content matches
    if fetched.get("content") != create_payload["content"]:
        log_fail("1d. Content matches", f"Expected '{create_payload['content']}', got '{fetched.get('content')}'")
    else:
        log_pass("1d. Content matches", "Content correct")
    
    # Test GET with non-existent id (should return 404)
    print("Testing GET with non-existent id...")
    resp = requests.get(f"{BASE_URL}/posts/00000000-0000-0000-0000-000000000000")
    if resp.status_code != 404:
        log_fail("1e. GET non-existent post returns 404", f"Status {resp.status_code}, expected 404")
    else:
        log_pass("1e. GET non-existent post returns 404", "Correctly returns 404")


# ============================================================
# TEST 2: is_lyrics + #music topic gating
# ============================================================
def test_is_lyrics_music_gating():
    print_section("TEST 2: is_lyrics + #music Topic Gating")
    
    # 2a. Sexual content with topic=music + is_lyrics=true should be ACCEPTED
    print("2a. Testing sexual content with topic=music + is_lyrics=true...")
    payload = {
        "content": "send nudes please tonight baby",
        "topic": "music",
        "device_id": "qa-v12-lyr-1",
        "is_lyrics": True
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code not in [200, 201]:
        log_fail("2a. Sexual lyrics on #music accepted", f"Status {resp.status_code}: {resp.text}")
    else:
        data = resp.json()
        if data.get("is_lyrics") != True:
            log_fail("2a. Sexual lyrics on #music accepted", f"is_lyrics={data.get('is_lyrics')}, expected True")
        elif data.get("topic") != "music":
            log_fail("2a. Sexual lyrics on #music accepted", f"topic={data.get('topic')}, expected 'music'")
        else:
            log_pass("2a. Sexual lyrics on #music accepted", f"Post created with is_lyrics=true")
    
    # 2b. Sexual content with topic=stories + is_lyrics=true should be BLOCKED
    print("2b. Testing sexual content with topic=stories + is_lyrics=true...")
    payload = {
        "content": "send nudes please tonight baby",
        "topic": "stories",
        "device_id": "qa-v12-lyr-2",
        "is_lyrics": True
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code != 400:
        log_fail("2b. Sexual content on #stories blocked", f"Status {resp.status_code}, expected 400")
    elif "sexual content" not in resp.text.lower():
        log_fail("2b. Sexual content on #stories blocked", f"Wrong error: {resp.text}")
    else:
        log_pass("2b. Sexual content on #stories blocked", "Correctly blocked with 'sexual content' error")
    
    # 2c. Hate/self-harm content with topic=music + is_lyrics=true should STILL be blocked
    print("2c. Testing hate/self-harm with topic=music + is_lyrics=true...")
    payload = {
        "content": "kill yourself loser you should die tonight",
        "topic": "music",
        "device_id": "qa-v12-lyr-3",
        "is_lyrics": True
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code != 400:
        log_fail("2c. Hate/self-harm still blocked on #music", f"Status {resp.status_code}, expected 400")
    else:
        log_pass("2c. Hate/self-harm still blocked on #music", f"Correctly blocked: {resp.text[:100]}")
    
    # 2d. Links with topic=music + is_lyrics=true should STILL be blocked
    print("2d. Testing links with topic=music + is_lyrics=true...")
    payload = {
        "content": "check this https://malicious.com",
        "topic": "music",
        "device_id": "qa-v12-lyr-4",
        "is_lyrics": True
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code != 400:
        log_fail("2d. Links still blocked on #music", f"Status {resp.status_code}, expected 400")
    elif "link" not in resp.text.lower():
        log_fail("2d. Links still blocked on #music", f"Wrong error: {resp.text}")
    else:
        log_pass("2d. Links still blocked on #music", "Correctly blocked with link error")
    
    # 2e. Morse code with topic=music + is_lyrics=true should STILL be blocked
    print("2e. Testing morse code with topic=music + is_lyrics=true...")
    payload = {
        "content": "... --- ... hello world",
        "topic": "music",
        "device_id": "qa-v12-lyr-5",
        "is_lyrics": True
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code != 400:
        log_fail("2e. Morse code still blocked on #music", f"Status {resp.status_code}, expected 400")
    elif "morse" not in resp.text.lower():
        log_fail("2e. Morse code still blocked on #music", f"Wrong error: {resp.text}")
    else:
        log_pass("2e. Morse code still blocked on #music", "Correctly blocked with morse error")
    
    # 2f. Normal content with topic=stories + is_lyrics=true should be accepted but is_lyrics silently dropped
    print("2f. Testing normal content with topic=stories + is_lyrics=true...")
    payload = {
        "content": "some normal post body that should pass without issues here",
        "topic": "stories",
        "device_id": "qa-v12-lyr-6",
        "is_lyrics": True
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code not in [200, 201]:
        log_fail("2f. Normal content on #stories accepted", f"Status {resp.status_code}: {resp.text}")
    else:
        data = resp.json()
        if data.get("is_lyrics") != False:
            log_fail("2f. is_lyrics silently dropped on non-music", f"is_lyrics={data.get('is_lyrics')}, expected False")
        else:
            log_pass("2f. is_lyrics silently dropped on non-music", "is_lyrics=false as expected")


# ============================================================
# TEST 3: Music caption translation
# ============================================================
def test_music_caption_translation():
    print_section("TEST 3: Music Caption Translation")
    
    # Create a music post with Spanish caption
    print("Creating music post with Spanish caption...")
    payload = {
        "link_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "title": "Test Song",
        "artist": "Test Artist",
        "caption": "Hola, esta canción es increíble y me hace muy feliz hoy",
        "device_id": "qa-v12-music-1"
    }
    resp = requests.post(f"{BASE_URL}/music", json=payload)
    if resp.status_code not in [200, 201]:
        log_fail("3a. Create music with Spanish caption", f"Status {resp.status_code}: {resp.text}")
        return
    
    music_data = resp.json()
    music_id = music_data.get("id")
    if not music_id:
        log_fail("3a. Create music with Spanish caption", "No id in response")
        return
    
    # Verify lang field is set
    if music_data.get("lang") != "es":
        log_warn("3a. Music lang detection", f"lang={music_data.get('lang')}, expected 'es'")
    else:
        log_pass("3a. Music lang detection", "lang='es' detected correctly")
    
    # First translation call (should return cached=false)
    print(f"Translating music {music_id} (first call)...")
    resp = requests.post(f"{BASE_URL}/music/{music_id}/translate")
    if resp.status_code != 200:
        log_fail("3b. First translation call", f"Status {resp.status_code}: {resp.text}")
        return
    
    trans_data = resp.json()
    translation = trans_data.get("translation", "")
    lang = trans_data.get("lang")
    cached = trans_data.get("cached")
    
    if not translation:
        log_fail("3b. First translation call", "Empty translation")
    elif cached != False:
        log_fail("3b. First translation call", f"cached={cached}, expected False")
    elif lang != "es":
        log_warn("3b. First translation call", f"lang={lang}, expected 'es'")
    else:
        log_pass("3b. First translation call", f"Translation: '{translation[:50]}...', cached=false")
    
    # Second translation call (should return cached=true)
    print(f"Translating music {music_id} (second call)...")
    time.sleep(0.5)  # Small delay
    resp = requests.post(f"{BASE_URL}/music/{music_id}/translate")
    if resp.status_code != 200:
        log_fail("3c. Second translation call (cached)", f"Status {resp.status_code}: {resp.text}")
    else:
        trans_data2 = resp.json()
        if trans_data2.get("cached") != True:
            log_fail("3c. Second translation call (cached)", f"cached={trans_data2.get('cached')}, expected True")
        elif trans_data2.get("translation") != translation:
            log_fail("3c. Second translation call (cached)", "Translation changed between calls")
        else:
            log_pass("3c. Second translation call (cached)", "cached=true, same translation")
    
    # Test with non-existent music id (should return 404)
    print("Testing translate with non-existent music id...")
    resp = requests.post(f"{BASE_URL}/music/00000000-0000-0000-0000-000000000000/translate")
    if resp.status_code != 404:
        log_fail("3d. Translate non-existent music returns 404", f"Status {resp.status_code}, expected 404")
    else:
        log_pass("3d. Translate non-existent music returns 404", "Correctly returns 404")
    
    # Test with English caption (should detect lang=en)
    print("Creating music post with English caption...")
    payload = {
        "link_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "title": "English Song",
        "artist": "English Artist",
        "caption": "this song is amazing and makes me feel great",
        "device_id": "qa-v12-music-2"
    }
    resp = requests.post(f"{BASE_URL}/music", json=payload)
    if resp.status_code not in [200, 201]:
        log_fail("3e. Music with English caption", f"Status {resp.status_code}: {resp.text}")
    else:
        data = resp.json()
        if data.get("lang") != "en":
            log_warn("3e. Music with English caption", f"lang={data.get('lang')}, expected 'en'")
        else:
            log_pass("3e. Music with English caption", "lang='en' detected correctly")


# ============================================================
# TEST 4: Engagement loop biases toward manual posts
# ============================================================
def test_engagement_loop():
    print_section("TEST 4: Engagement Loop Biases Toward Manual Posts")
    
    # Create a fresh manual post
    print("Creating fresh manual post...")
    post_payload = {
        "content": "engagement smoke test manual post v12 abcd xyz testing",
        "topic": "stories",
        "device_id": "qa-v12-engage-1"
    }
    resp = requests.post(f"{BASE_URL}/posts", json=post_payload)
    if resp.status_code not in [200, 201]:
        log_fail("4a. Create manual post for engagement test", f"Status {resp.status_code}: {resp.text}")
        return
    
    post_data = resp.json()
    post_id = post_data.get("id")
    initial_post_hugs = post_data.get("hugs", 0)
    initial_post_fugs = post_data.get("fugs", 0)
    log_pass("4a. Create manual post for engagement test", f"Post {post_id}, hugs={initial_post_hugs}, fugs={initial_post_fugs}")
    
    # Create a fresh manual music upload
    print("Creating fresh manual music upload...")
    music_payload = {
        "link_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "title": "Gangnam Style",
        "artist": "Psy",
        "caption": "",
        "device_id": "qa-v12-engage-2"
    }
    resp = requests.post(f"{BASE_URL}/music", json=music_payload)
    if resp.status_code not in [200, 201]:
        log_fail("4b. Create manual music for engagement test", f"Status {resp.status_code}: {resp.text}")
        return
    
    music_data = resp.json()
    music_id = music_data.get("id")
    initial_music_hugs = music_data.get("hugs", 0)
    initial_music_fugs = music_data.get("fugs", 0)
    log_pass("4b. Create manual music for engagement test", f"Music {music_id}, hugs={initial_music_hugs}, fugs={initial_music_fugs}")
    
    # Poll every 15s for up to 150s
    print("\nPolling for engagement changes (up to 150s, checking every 15s)...")
    print("Engagement loop interval is ~25s, so we should see changes within 2-3 cycles")
    
    max_wait = 150
    poll_interval = 15
    elapsed = 0
    
    post_engaged = False
    music_engaged = False
    
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        
        print(f"\n[{elapsed}s] Checking engagement...")
        
        # Check post
        resp = requests.get(f"{BASE_URL}/posts")
        if resp.status_code == 200:
            posts = resp.json()
            for p in posts:
                if p.get("id") == post_id:
                    current_hugs = p.get("hugs", 0)
                    current_fugs = p.get("fugs", 0)
                    print(f"  Post: hugs={current_hugs} (was {initial_post_hugs}), fugs={current_fugs} (was {initial_post_fugs})")
                    if current_hugs > initial_post_hugs or current_fugs > initial_post_fugs:
                        post_engaged = True
                    break
        
        # Check music
        resp = requests.get(f"{BASE_URL}/music")
        if resp.status_code == 200:
            music_posts = resp.json()
            for m in music_posts:
                if m.get("id") == music_id:
                    current_hugs = m.get("hugs", 0)
                    current_fugs = m.get("fugs", 0)
                    print(f"  Music: hugs={current_hugs} (was {initial_music_hugs}), fugs={current_fugs} (was {initial_music_fugs})")
                    if current_hugs > initial_music_hugs or current_fugs > initial_music_fugs:
                        music_engaged = True
                    break
        
        # Check if both have engagement
        if post_engaged and music_engaged:
            log_pass("4c. Engagement loop working", f"Both post and music received engagement within {elapsed}s")
            break
    
    # Final check
    if not post_engaged:
        log_fail("4c. Post engagement", f"Post did not receive any hugs/fugs after {max_wait}s")
    elif not music_engaged:
        log_fail("4c. Music engagement", f"Music did not receive any hugs/fugs after {max_wait}s")
    elif not (post_engaged and music_engaged):
        log_fail("4c. Engagement loop working", f"Not all items received engagement after {max_wait}s")


# ============================================================
# TEST 5: Regression tests
# ============================================================
def test_regression():
    print_section("TEST 5: Regression Tests")
    
    # 5a. Regular English post should work
    print("5a. Testing regular English post...")
    payload = {
        "content": "this is a normal english post about my day and how things are going",
        "topic": "stories",
        "device_id": "qa-v12-regression-1"
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code not in [200, 201]:
        log_fail("5a. Regular English post", f"Status {resp.status_code}: {resp.text}")
    else:
        data = resp.json()
        if data.get("lang") != "en":
            log_warn("5a. Regular English post", f"lang={data.get('lang')}, expected 'en'")
        if data.get("is_lyrics") != False:
            log_fail("5a. Regular English post", f"is_lyrics={data.get('is_lyrics')}, expected False")
        else:
            log_pass("5a. Regular English post", "Works correctly with lang='en', is_lyrics=false")
    
    # 5b. Post with link should still be blocked
    print("5b. Testing post with link (should be blocked)...")
    payload = {
        "content": "check out this cool site https://example.com for more info",
        "topic": "stories",
        "device_id": "qa-v12-regression-2"
    }
    resp = requests.post(f"{BASE_URL}/posts", json=payload)
    if resp.status_code != 400:
        log_fail("5b. Link blocking", f"Status {resp.status_code}, expected 400")
    elif "link" not in resp.text.lower():
        log_fail("5b. Link blocking", f"Wrong error: {resp.text}")
    else:
        log_pass("5b. Link blocking", "Links still correctly blocked")
    
    # 5c. GET /api/posts should still return array
    print("5c. Testing GET /api/posts returns array...")
    resp = requests.get(f"{BASE_URL}/posts")
    if resp.status_code != 200:
        log_fail("5c. GET /api/posts", f"Status {resp.status_code}: {resp.text}")
    else:
        data = resp.json()
        if not isinstance(data, list):
            log_fail("5c. GET /api/posts", f"Response is {type(data)}, expected list")
        else:
            log_pass("5c. GET /api/posts", f"Returns array with {len(data)} posts")


# ============================================================
# Main test runner
# ============================================================
def main():
    print("\n" + "="*70)
    print("  PLUTO v1.2 BACKEND TEST SUITE")
    print("  Backend URL:", BASE_URL)
    print("="*70)
    
    try:
        # Run all tests
        test_single_post_fetch()
        test_is_lyrics_music_gating()
        test_music_caption_translation()
        test_engagement_loop()
        test_regression()
        
        # Print summary
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)
        print(f"\n✅ PASSED: {len(test_results['passed'])} tests")
        print(f"❌ FAILED: {len(test_results['failed'])} tests")
        print(f"⚠️  WARNINGS: {len(test_results['warnings'])} warnings")
        
        if test_results['failed']:
            print("\nFailed tests:")
            for fail in test_results['failed']:
                print(f"  - {fail}")
        
        if test_results['warnings']:
            print("\nWarnings:")
            for warn in test_results['warnings']:
                print(f"  - {warn}")
        
        # Exit code
        if test_results['failed']:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)
        else:
            print("\n✅ ALL TESTS PASSED")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
