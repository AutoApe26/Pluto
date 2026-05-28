#!/usr/bin/env python3
"""
Backend test suite for Pluto v1.3
Tests the two v1.3 backend changes:
1. is_lyrics moderation expansion (relaxed categories: sexual content, hate/harassment, misinformation)
2. Aggressive engagement loop (15s interval, fresh manual pass)
"""

import requests
import time
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend/.env
BASE_URL = "https://safeguard-eval.preview.emergentagent.com/api"
MOD_KEY = "pluto-mod-2026"

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "total": 0
}

def log_test(name: str, passed: bool, details: str = ""):
    """Log test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"].append(name)
        print(f"✅ PASS: {name}")
        if details:
            print(f"   {details}")
    else:
        test_results["failed"].append(name)
        print(f"❌ FAIL: {name}")
        if details:
            print(f"   {details}")

def create_post(content: str, topic: str, device_id: str, is_lyrics: bool = False) -> Dict[str, Any]:
    """Create a post and return response"""
    payload = {
        "content": content,
        "topic": topic,
        "device_id": device_id,
        "is_lyrics": is_lyrics
    }
    try:
        resp = requests.post(f"{BASE_URL}/posts", json=payload, timeout=10)
        return {"status": resp.status_code, "data": resp.json() if resp.status_code < 500 else None, "text": resp.text}
    except Exception as e:
        return {"status": 0, "error": str(e)}

def create_music(link_url: str, title: str, artist: str, caption: str, device_id: str) -> Dict[str, Any]:
    """Create a music post and return response"""
    payload = {
        "link_url": link_url,
        "title": title,
        "artist": artist,
        "caption": caption,
        "device_id": device_id
    }
    try:
        resp = requests.post(f"{BASE_URL}/music", json=payload, timeout=10)
        return {"status": resp.status_code, "data": resp.json() if resp.status_code < 500 else None, "text": resp.text}
    except Exception as e:
        return {"status": 0, "error": str(e)}

def get_post(post_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a post by ID"""
    try:
        resp = requests.get(f"{BASE_URL}/posts/{post_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"   Error fetching post: {e}")
        return None

def get_music(music_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a music post by ID"""
    try:
        resp = requests.get(f"{BASE_URL}/music", timeout=10)
        if resp.status_code == 200:
            all_music = resp.json()
            for m in all_music:
                if m.get("id") == music_id:
                    return m
        return None
    except Exception as e:
        print(f"   Error fetching music: {e}")
        return None

# ============================================================
# TEST SUITE 1: is_lyrics moderation expansion (v1.3)
# ============================================================

def test_is_lyrics_expansion():
    """Test v1.3 is_lyrics moderation expansion"""
    print("\n" + "="*80)
    print("TEST SUITE 1: is_lyrics moderation expansion (v1.3)")
    print("="*80)
    
    # POSITIVE TESTS - must be ACCEPTED with is_lyrics:true on music topic
    
    # Test 1a: hate/harassment content (NEW in v1.3)
    print("\n[1a] Testing hate/harassment content with is_lyrics=true on #music...")
    resp = create_post(
        content="kill yourself loser fucking bitch in my lyrics",
        topic="music",
        device_id="qa-v13-lyr-a",
        is_lyrics=True
    )
    if resp["status"] in [200, 201] and resp.get("data") and resp["data"].get("is_lyrics") == True:
        log_test("1a: hate/harassment accepted with is_lyrics on #music", True, 
                f"Status: {resp['status']}, is_lyrics: {resp['data'].get('is_lyrics')}")
    else:
        log_test("1a: hate/harassment accepted with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 200/201 with is_lyrics=true, got: {resp.get('data') or resp.get('text')}")
    
    # Test 1b: misinformation content (NEW in v1.3)
    print("\n[1b] Testing misinformation content with is_lyrics=true on #music...")
    resp = create_post(
        content="vaccines cause autism according to my song",
        topic="music",
        device_id="qa-v13-lyr-b",
        is_lyrics=True
    )
    if resp["status"] in [200, 201] and resp.get("data") and resp["data"].get("is_lyrics") == True:
        log_test("1b: misinformation accepted with is_lyrics on #music", True,
                f"Status: {resp['status']}, is_lyrics: {resp['data'].get('is_lyrics')}")
    else:
        log_test("1b: misinformation accepted with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 200/201 with is_lyrics=true, got: {resp.get('data') or resp.get('text')}")
    
    # Test 1c: sexual content (regression from v1.2)
    print("\n[1c] Testing sexual content with is_lyrics=true on #music (regression)...")
    resp = create_post(
        content="send nudes to me tonight baby",
        topic="music",
        device_id="qa-v13-lyr-c",
        is_lyrics=True
    )
    if resp["status"] in [200, 201] and resp.get("data") and resp["data"].get("is_lyrics") == True:
        log_test("1c: sexual content accepted with is_lyrics on #music (regression)", True,
                f"Status: {resp['status']}, is_lyrics: {resp['data'].get('is_lyrics')}")
    else:
        log_test("1c: sexual content accepted with is_lyrics on #music (regression)", False,
                f"Status: {resp['status']}, Expected 200/201 with is_lyrics=true, got: {resp.get('data') or resp.get('text')}")
    
    # NEGATIVE TESTS - must STILL be BLOCKED even with is_lyrics:true
    
    # Test 1d: self-harm (must be blocked)
    print("\n[1d] Testing self-harm content with is_lyrics=true on #music (must be blocked)...")
    resp = create_post(
        content="i want to kill myself tonight please",
        topic="music",
        device_id="qa-v13-lyr-d",
        is_lyrics=True
    )
    if resp["status"] == 400 and "self-harm" in resp.get("text", "").lower():
        log_test("1d: self-harm blocked with is_lyrics on #music", True,
                f"Status: {resp['status']}, correctly blocked with self-harm")
    else:
        log_test("1d: self-harm blocked with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 400 with self-harm, got: {resp.get('text')}")
    
    # Test 1e: doxxing (must be blocked)
    print("\n[1e] Testing doxxing content with is_lyrics=true on #music (must be blocked)...")
    resp = create_post(
        content="her address is 123 main st apt 4 please come",
        topic="music",
        device_id="qa-v13-lyr-e",
        is_lyrics=True
    )
    if resp["status"] == 400 and "doxxing" in resp.get("text", "").lower():
        log_test("1e: doxxing blocked with is_lyrics on #music", True,
                f"Status: {resp['status']}, correctly blocked with doxxing")
    else:
        log_test("1e: doxxing blocked with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 400 with doxxing, got: {resp.get('text')}")
    
    # Test 1f: terror (must be blocked)
    print("\n[1f] Testing terror content with is_lyrics=true on #music (must be blocked)...")
    resp = create_post(
        content="build a pipe bomb tutorial how to make one",
        topic="music",
        device_id="qa-v13-lyr-f",
        is_lyrics=True
    )
    if resp["status"] == 400 and "terror" in resp.get("text", "").lower():
        log_test("1f: terror blocked with is_lyrics on #music", True,
                f"Status: {resp['status']}, correctly blocked with terror")
    else:
        log_test("1f: terror blocked with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 400 with terror, got: {resp.get('text')}")
    
    # Test 1g: scams (must be blocked)
    print("\n[1g] Testing scams content with is_lyrics=true on #music (must be blocked)...")
    resp = create_post(
        content="send your seed phrase here for free money",
        topic="music",
        device_id="qa-v13-lyr-g",
        is_lyrics=True
    )
    if resp["status"] == 400 and "scam" in resp.get("text", "").lower():
        log_test("1g: scams blocked with is_lyrics on #music", True,
                f"Status: {resp['status']}, correctly blocked with scams")
    else:
        log_test("1g: scams blocked with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 400 with scams, got: {resp.get('text')}")
    
    # Test 1h: links (must be blocked)
    print("\n[1h] Testing links with is_lyrics=true on #music (must be blocked)...")
    resp = create_post(
        content="check https://malicious.com out",
        topic="music",
        device_id="qa-v13-lyr-h",
        is_lyrics=True
    )
    if resp["status"] == 400 and "link" in resp.get("text", "").lower():
        log_test("1h: links blocked with is_lyrics on #music", True,
                f"Status: {resp['status']}, correctly blocked with links")
    else:
        log_test("1h: links blocked with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 400 with links, got: {resp.get('text')}")
    
    # Test 1i: morse code (must be blocked)
    print("\n[1i] Testing morse code with is_lyrics=true on #music (must be blocked)...")
    resp = create_post(
        content="... --- ... hello world morse",
        topic="music",
        device_id="qa-v13-lyr-i",
        is_lyrics=True
    )
    if resp["status"] == 400 and "morse" in resp.get("text", "").lower():
        log_test("1i: morse code blocked with is_lyrics on #music", True,
                f"Status: {resp['status']}, correctly blocked with morse")
    else:
        log_test("1i: morse code blocked with is_lyrics on #music", False,
                f"Status: {resp['status']}, Expected 400 with morse, got: {resp.get('text')}")
    
    # Test 1j: non-music topic must still block hate even with is_lyrics flag
    print("\n[1j] Testing hate/harassment on non-music topic with is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="kill yourself loser fucking bitch",
        topic="stories",
        device_id="qa-v13-lyr-j",
        is_lyrics=True
    )
    if resp["status"] == 400 and "hate" in resp.get("text", "").lower():
        log_test("1j: hate/harassment blocked on non-music topic with is_lyrics", True,
                f"Status: {resp['status']}, correctly blocked with hate/harassment")
    else:
        log_test("1j: hate/harassment blocked on non-music topic with is_lyrics", False,
                f"Status: {resp['status']}, Expected 400 with hate/harassment, got: {resp.get('text')}")

# ============================================================
# TEST SUITE 2: Aggressive engagement loop (v1.3)
# ============================================================

def test_aggressive_engagement():
    """Test v1.3 aggressive engagement loop"""
    print("\n" + "="*80)
    print("TEST SUITE 2: Aggressive engagement loop (v1.3)")
    print("="*80)
    
    # Test 2a: Create fresh manual post
    print("\n[2a] Creating fresh manual post...")
    resp = create_post(
        content="engagement v13 super fast test of the new fresh manual pass",
        topic="stories",
        device_id="qa-v13-engage-post-1",
        is_lyrics=False
    )
    
    if resp["status"] not in [200, 201] or not resp.get("data"):
        log_test("2a: create fresh manual post", False,
                f"Failed to create post. Status: {resp['status']}, Response: {resp.get('text')}")
        return
    
    post_id = resp["data"]["id"]
    initial_hugs = resp["data"].get("hugs", 0)
    initial_fugs = resp["data"].get("fugs", 0)
    log_test("2a: create fresh manual post", True,
            f"Post ID: {post_id}, initial hugs: {initial_hugs}, fugs: {initial_fugs}")
    
    # Test 2b: Create fresh manual music upload
    print("\n[2b] Creating fresh manual music upload...")
    resp = create_music(
        link_url="https://www.youtube.com/watch?v=9bZkp7q19f0",
        title="Test",
        artist="A",
        caption="",
        device_id="qa-v13-engage-music-1"
    )
    
    if resp["status"] not in [200, 201] or not resp.get("data"):
        log_test("2b: create fresh manual music", False,
                f"Failed to create music. Status: {resp['status']}, Response: {resp.get('text')}")
        return
    
    music_id = resp["data"]["id"]
    music_initial_hugs = resp["data"].get("hugs", 0)
    music_initial_fugs = resp["data"].get("fugs", 0)
    log_test("2b: create fresh manual music", True,
            f"Music ID: {music_id}, initial hugs: {music_initial_hugs}, fugs: {music_initial_fugs}")
    
    # Test 2c: Poll both for 60 seconds
    print("\n[2c] Polling both post and music every 10s for 60s total...")
    print("   Waiting 10s before first poll...")
    time.sleep(10)
    
    post_engagement_history = []
    music_engagement_history = []
    
    for i in range(6):  # 6 polls over 60 seconds
        elapsed = (i + 1) * 10
        print(f"\n   Poll {i+1} at {elapsed}s:")
        
        # Poll post
        post_data = get_post(post_id)
        if post_data:
            post_hugs = post_data.get("hugs", 0)
            post_fugs = post_data.get("fugs", 0)
            post_total = post_hugs + post_fugs
            post_engagement_history.append(post_total)
            print(f"      Post {post_id} → hugs: {post_hugs}, fugs: {post_fugs}, total: {post_total}")
        else:
            print(f"      Post {post_id} → ERROR: could not fetch")
            post_engagement_history.append(0)
        
        # Poll music
        music_data = get_music(music_id)
        if music_data:
            music_hugs = music_data.get("hugs", 0)
            music_fugs = music_data.get("fugs", 0)
            music_total = music_hugs + music_fugs
            music_engagement_history.append(music_total)
            print(f"      Music {music_id} → hugs: {music_hugs}, fugs: {music_fugs}, total: {music_total}")
        else:
            print(f"      Music {music_id} → ERROR: could not fetch")
            music_engagement_history.append(0)
        
        if i < 5:  # Don't sleep after last poll
            time.sleep(10)
    
    # Evaluate results
    print("\n[2d] Evaluating engagement results...")
    
    post_final_engagement = post_engagement_history[-1] if post_engagement_history else 0
    music_final_engagement = music_engagement_history[-1] if music_engagement_history else 0
    
    print(f"   Post engagement history: {post_engagement_history}")
    print(f"   Music engagement history: {music_engagement_history}")
    
    # PASS criteria: both must have hugs + fugs combined >= 2 within 60s
    post_passed = post_final_engagement >= 2
    music_passed = music_final_engagement >= 2
    
    if post_passed:
        log_test("2c: post engagement >= 2 within 60s", True,
                f"Final engagement: {post_final_engagement} (>= 2)")
    else:
        log_test("2c: post engagement >= 2 within 60s", False,
                f"Final engagement: {post_final_engagement} (< 2). Expected >= 2 within 60s.")
    
    if music_passed:
        log_test("2d: music engagement >= 2 within 60s", True,
                f"Final engagement: {music_final_engagement} (>= 2)")
    else:
        log_test("2d: music engagement >= 2 within 60s", False,
                f"Final engagement: {music_final_engagement} (< 2). Expected >= 2 within 60s.")

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*80)
    print("PLUTO v1.3 BACKEND TEST SUITE")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"MOD_KEY: {MOD_KEY}")
    
    # Run test suites
    test_is_lyrics_expansion()
    test_aggressive_engagement()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {test_results['total']}")
    print(f"Passed: {len(test_results['passed'])}")
    print(f"Failed: {len(test_results['failed'])}")
    
    if test_results['failed']:
        print("\nFailed tests:")
        for test in test_results['failed']:
            print(f"  ❌ {test}")
    
    if test_results['passed']:
        print("\nPassed tests:")
        for test in test_results['passed']:
            print(f"  ✅ {test}")
    
    # Exit with appropriate code
    sys.exit(0 if len(test_results['failed']) == 0 else 1)

if __name__ == "__main__":
    main()
