#!/usr/bin/env python3
"""
Backend test suite for Pluto v1.4
Tests the two v1.4 backend changes:
1. Extremism / dehumanization category (never-relaxed under lyrics mode)
2. Expanded terror/explosives vocabulary
"""

import requests
import sys
from typing import Dict, Any

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

# ============================================================
# TEST SUITE 1: Extremism / dehumanization category (v1.4)
# ============================================================

def test_extremism_category():
    """Test v1.4 extremism/dehumanization category (never-relaxed)"""
    print("\n" + "="*80)
    print("TEST SUITE 1: Extremism / dehumanization category (v1.4)")
    print("="*80)
    
    # BLOCKED TESTS - must return 400 with extremism/dehumanization reason
    
    # Test 1a: Nazi slogan on music+is_lyrics=true (must be blocked)
    print("\n[1a] Testing Nazi slogan 'heil hitler' on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="heil hitler my brothers, sieg heil tonight",
        topic="music",
        device_id="qa-v14-extremism-1a",
        is_lyrics=True
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1a: Nazi slogan blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1a: Nazi slogan blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # Test 1b: Nazi slogan on stories (must be blocked)
    print("\n[1b] Testing Nazi slogan 'heil hitler' on stories (must be blocked)...")
    resp = create_post(
        content="heil hitler my brothers, sieg heil tonight",
        topic="stories",
        device_id="qa-v14-extremism-1b",
        is_lyrics=False
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1b: Nazi slogan blocked on stories", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1b: Nazi slogan blocked on stories", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # Test 1c: KKK slogan on music+is_lyrics=true (must be blocked)
    print("\n[1c] Testing KKK slogan on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="kkk forever in my hood",
        topic="music",
        device_id="qa-v14-extremism-1c",
        is_lyrics=True
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1c: KKK slogan blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1c: KKK slogan blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # Test 1d: White power slogan on music+is_lyrics=true (must be blocked)
    print("\n[1d] Testing white power slogan on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="white power and 1488 baby",
        topic="music",
        device_id="qa-v14-extremism-1d",
        is_lyrics=True
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1d: White power slogan blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1d: White power slogan blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # Test 1e: Replacement theory slogan on music+is_lyrics=true (must be blocked)
    print("\n[1e] Testing replacement theory slogan on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="jews will not replace us tonight",
        topic="music",
        device_id="qa-v14-extremism-1e",
        is_lyrics=True
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1e: Replacement theory slogan blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1e: Replacement theory slogan blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # Test 1f: Death to Israel/America on music+is_lyrics=true (must be blocked)
    print("\n[1f] Testing 'death to israel/america' on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="death to israel and death to america",
        topic="music",
        device_id="qa-v14-extremism-1f",
        is_lyrics=True
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1f: Death to Israel/America blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1f: Death to Israel/America blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # Test 1g: Gas the jews on music+is_lyrics=true (must be blocked)
    print("\n[1g] Testing 'gas the jews' on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="gas the jews tonight in my song",
        topic="music",
        device_id="qa-v14-extremism-1g",
        is_lyrics=True
    )
    detail_lower = resp.get("text", "").lower()
    has_extremism_keyword = any(kw in detail_lower for kw in ["extremist", "dehumanizing", "nazi", "genocide"])
    if resp["status"] == 400 and has_extremism_keyword:
        log_test("1g: Gas the jews blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail contains extremism keyword: {resp.get('text')[:100]}")
    else:
        log_test("1g: Gas the jews blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400 with extremism keyword, got: {resp.get('text')[:200]}")
    
    # REGRESSION TESTS - ordinary slurs/profanity should STILL be relaxed
    
    # Test 1h: Ordinary slurs on music+is_lyrics=true (must be ACCEPTED)
    print("\n[1h] Testing ordinary slurs on music+is_lyrics=true (regression - must be accepted)...")
    resp = create_post(
        content="fuckin nigga ass faggot energy in my track",
        topic="music",
        device_id="qa-v14-extremism-1h",
        is_lyrics=True
    )
    if resp["status"] in [200, 201] and resp.get("data") and resp["data"].get("is_lyrics") == True:
        log_test("1h: Ordinary slurs accepted on music+is_lyrics=true (regression)", True,
                f"Status: {resp['status']}, is_lyrics: {resp['data'].get('is_lyrics')}")
    else:
        log_test("1h: Ordinary slurs accepted on music+is_lyrics=true (regression)", False,
                f"Status: {resp['status']}, Expected 200/201 with is_lyrics=true, got: {resp.get('data') or resp.get('text')[:200]}")
    
    # Test 1i: Sexual content on music+is_lyrics=true (must be ACCEPTED)
    print("\n[1i] Testing sexual content on music+is_lyrics=true (regression - must be accepted)...")
    resp = create_post(
        content="send nudes to me tonight baby",
        topic="music",
        device_id="qa-v14-extremism-1i",
        is_lyrics=True
    )
    if resp["status"] in [200, 201] and resp.get("data") and resp["data"].get("is_lyrics") == True:
        log_test("1i: Sexual content accepted on music+is_lyrics=true (regression)", True,
                f"Status: {resp['status']}, is_lyrics: {resp['data'].get('is_lyrics')}")
    else:
        log_test("1i: Sexual content accepted on music+is_lyrics=true (regression)", False,
                f"Status: {resp['status']}, Expected 200/201 with is_lyrics=true, got: {resp.get('data') or resp.get('text')[:200]}")

# ============================================================
# TEST SUITE 2: Expanded terror/explosives vocabulary (v1.4)
# ============================================================

def test_explosives_expansion():
    """Test v1.4 expanded terror/explosives vocabulary"""
    print("\n" + "="*80)
    print("TEST SUITE 2: Expanded terror/explosives vocabulary (v1.4)")
    print("="*80)
    
    # BLOCKED TESTS - must return 400
    
    # Test 2a: Semtex and C4
    print("\n[2a] Testing 'semtex and c4' (must be blocked)...")
    resp = create_post(
        content="i have semtex and c4 ready for tonight",
        topic="stories",
        device_id="qa-v14-explosives-2a",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2a: Semtex and C4 blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2a: Semtex and C4 blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2b: Carrying semtex
    print("\n[2b] Testing 'carrying semtex' (must be blocked)...")
    resp = create_post(
        content="carrying semtex tonight to the show",
        topic="stories",
        device_id="qa-v14-explosives-2b",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2b: Carrying semtex blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2b: Carrying semtex blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2c: Made nitroglycerin
    print("\n[2c] Testing 'made nitroglycerin' (must be blocked)...")
    resp = create_post(
        content="made nitroglycerin for the gig",
        topic="stories",
        device_id="qa-v14-explosives-2c",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2c: Made nitroglycerin blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2c: Made nitroglycerin blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2d: Ammonium nitrate and ANFO
    print("\n[2d] Testing 'ammonium nitrate and anfo' (must be blocked)...")
    resp = create_post(
        content="i got ammonium nitrate and anfo in my truck",
        topic="stories",
        device_id="qa-v14-explosives-2d",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2d: Ammonium nitrate and ANFO blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2d: Ammonium nitrate and ANFO blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2e: Homemade dynamite
    print("\n[2e] Testing 'homemade dynamite' (must be blocked)...")
    resp = create_post(
        content="homemade dynamite for tonight",
        topic="stories",
        device_id="qa-v14-explosives-2e",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2e: Homemade dynamite blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2e: Homemade dynamite blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2f: Stick of dynamite
    print("\n[2f] Testing 'stick of dynamite' (must be blocked)...")
    resp = create_post(
        content="stick of dynamite in my hand",
        topic="stories",
        device_id="qa-v14-explosives-2f",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2f: Stick of dynamite blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2f: Stick of dynamite blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2g: Homemade TNT
    print("\n[2g] Testing 'homemade tnt' (must be blocked)...")
    resp = create_post(
        content="homemade tnt ready to go",
        topic="stories",
        device_id="qa-v14-explosives-2g",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2g: Homemade TNT blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2g: Homemade TNT blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2h: Pressure cooker bomb
    print("\n[2h] Testing 'pressure cooker bomb' (must be blocked)...")
    resp = create_post(
        content="pressure cooker bomb plan",
        topic="stories",
        device_id="qa-v14-explosives-2h",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2h: Pressure cooker bomb blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2h: Pressure cooker bomb blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2i: Fertilizer bomb
    print("\n[2i] Testing 'fertilizer bomb' (must be blocked)...")
    resp = create_post(
        content="fertilizer bomb tutorial",
        topic="stories",
        device_id="qa-v14-explosives-2i",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2i: Fertilizer bomb blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2i: Fertilizer bomb blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2j: Make C4 tutorial
    print("\n[2j] Testing 'make c4 at home' (must be blocked)...")
    resp = create_post(
        content="make c4 at home tutorial",
        topic="stories",
        device_id="qa-v14-explosives-2j",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2j: Make C4 tutorial blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2j: Make C4 tutorial blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2k: Thermite charge
    print("\n[2k] Testing 'thermite charge' (must be blocked)...")
    resp = create_post(
        content="thermite charge for the lock",
        topic="stories",
        device_id="qa-v14-explosives-2k",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2k: Thermite charge blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2k: Thermite charge blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2l: Napalm bomb instructions
    print("\n[2l] Testing 'napalm bomb instructions' (must be blocked)...")
    resp = create_post(
        content="napalm bomb instructions",
        topic="stories",
        device_id="qa-v14-explosives-2l",
        is_lyrics=False
    )
    if resp["status"] == 400:
        log_test("2l: Napalm bomb instructions blocked", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2l: Napalm bomb instructions blocked", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # Test 2m: Extremism + explosives on music+is_lyrics=true (both should block)
    print("\n[2m] Testing extremism + explosives on music+is_lyrics=true (must be blocked)...")
    resp = create_post(
        content="heil hitler — got that c4 ready for tonight",
        topic="music",
        device_id="qa-v14-explosives-2m",
        is_lyrics=True
    )
    if resp["status"] == 400:
        log_test("2m: Extremism + explosives blocked on music+is_lyrics=true", True,
                f"Status: {resp['status']}, detail: {resp.get('text')[:100]}")
    else:
        log_test("2m: Extremism + explosives blocked on music+is_lyrics=true", False,
                f"Status: {resp['status']}, Expected 400, got: {resp.get('text')[:200]}")
    
    # NEGATIVE TESTS - must return 200 (no false positives)
    
    # Test 2n: BTS Dynamite song reference
    print("\n[2n] Testing BTS Dynamite song reference (must be accepted)...")
    resp = create_post(
        content="that song dynamite by bts is straight fire today",
        topic="music",
        device_id="qa-v14-explosives-2n",
        is_lyrics=False
    )
    if resp["status"] in [200, 201]:
        log_test("2n: BTS Dynamite song reference accepted", True,
                f"Status: {resp['status']}")
    else:
        log_test("2n: BTS Dynamite song reference accepted", False,
                f"Status: {resp['status']}, Expected 200/201, got: {resp.get('text')[:200]}")
    
    # Test 2o: Dynamite as slang
    print("\n[2o] Testing 'you are dynamite' slang (must be accepted)...")
    resp = create_post(
        content="you are dynamite tonight baby",
        topic="music",
        device_id="qa-v14-explosives-2o",
        is_lyrics=False
    )
    if resp["status"] in [200, 201]:
        log_test("2o: Dynamite slang accepted", True,
                f"Status: {resp['status']}")
    else:
        log_test("2o: Dynamite slang accepted", False,
                f"Status: {resp['status']}, Expected 200/201, got: {resp.get('text')[:200]}")
    
    # Test 2p: TNT band reference
    print("\n[2p] Testing TNT band reference (must be accepted)...")
    resp = create_post(
        content="the band tnt rocks hard",
        topic="music",
        device_id="qa-v14-explosives-2p",
        is_lyrics=False
    )
    if resp["status"] in [200, 201]:
        log_test("2p: TNT band reference accepted", True,
                f"Status: {resp['status']}")
    else:
        log_test("2p: TNT band reference accepted", False,
                f"Status: {resp['status']}, Expected 200/201, got: {resp.get('text')[:200]}")
    
    # Test 2q: Explosive as positive slang
    print("\n[2q] Testing 'explosive' as positive slang (must be accepted)...")
    resp = create_post(
        content="that gig was explosive in a good way",
        topic="stories",
        device_id="qa-v14-explosives-2q",
        is_lyrics=False
    )
    if resp["status"] in [200, 201]:
        log_test("2q: Explosive slang accepted", True,
                f"Status: {resp['status']}")
    else:
        log_test("2q: Explosive slang accepted", False,
                f"Status: {resp['status']}, Expected 200/201, got: {resp.get('text')[:200]}")
    
    # Test 2r: Normal sentence
    print("\n[2r] Testing normal sentence (must be accepted)...")
    resp = create_post(
        content="this is a normal english sentence about my day",
        topic="stories",
        device_id="qa-v14-explosives-2r",
        is_lyrics=False
    )
    if resp["status"] in [200, 201]:
        log_test("2r: Normal sentence accepted", True,
                f"Status: {resp['status']}")
    else:
        log_test("2r: Normal sentence accepted", False,
                f"Status: {resp['status']}, Expected 200/201, got: {resp.get('text')[:200]}")

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*80)
    print("PLUTO v1.4 BACKEND TEST SUITE")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"MOD_KEY: {MOD_KEY}")
    print("\nNOTE: Only testing v1.4 NEW features (extremism category + explosives vocab)")
    print("      v1.1/v1.2/v1.3 tests are skipped (already verified)")
    
    # Run test suites
    test_extremism_category()
    test_explosives_expansion()
    
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
