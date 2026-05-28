"""
Pluto v1.5 Backend Regression Test — CSAM Zero-Tolerance Detector

Tests the detect_minor_sexual_abuse() combinatorial detector that runs
BEFORE everything in violation_for() with its own zero-tolerance error label.

POSITIVE cases (a-ak, al-an): MUST return HTTP 400 with "child sexual abuse" OR "minors" in response detail
NEGATIVE cases (ao-bb): MUST return HTTP 200 (no false positives)
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'frontend' / '.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://safeguard-eval.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_post(content: str, topic: str = "stories", is_lyrics: bool = False, device_id: str = "qa-v15-test"):
    """Helper to test POST /api/posts"""
    payload = {
        "content": content,
        "topic": topic,
        "device_id": device_id,
        "is_lyrics": is_lyrics
    }
    resp = requests.post(f"{API_BASE}/posts", json=payload, timeout=10)
    return resp

def check_csam_label(detail: str) -> bool:
    """Check if response detail contains CSAM-specific keywords"""
    detail_lower = detail.lower()
    return "child sexual abuse" in detail_lower or "minors" in detail_lower or "minor" in detail_lower

def main():
    print("=" * 80)
    print("PLUTO v1.5 BACKEND REGRESSION — CSAM ZERO-TOLERANCE DETECTOR")
    print("=" * 80)
    print(f"Backend URL: {API_BASE}")
    print()
    
    results = {
        "passed": [],
        "failed": [],
        "total": 0
    }
    
    # ========================================================================
    # POSITIVE CASES — MUST RETURN HTTP 400 with CSAM label
    # ========================================================================
    print("POSITIVE CASES (MUST BLOCK - HTTP 400 with CSAM label)")
    print("-" * 80)
    
    positive_cases = [
        # A. THE CANONICAL REGRESSION (Sev-1 if this ever publishes)
        ("a", "i like to rape and fuck minors", "stories", False),
        
        # B. Direct verb + minor object
        ("b", "i like to fuck kids", "stories", False),
        ("c", "i like to fuck children", "stories", False),
        ("d", "i like to fuck minors", "stories", False),
        ("e", "i want to fuck a kid", "stories", False),
        ("f", "i want to rape children", "stories", False),
        ("g", "fuck minors", "stories", False),
        ("h", "fuck kids", "stories", False),
        ("i", "fuck a 12 year old", "stories", False),
        ("j", "fuck a 12yo", "stories", False),
        ("k", "fuck little girls", "stories", False),
        ("l", "fuck little boys", "stories", False),
        ("m", "rape minors", "stories", False),
        ("n", "sex with minors", "stories", False),
        ("o", "sex with a minor", "stories", False),
        ("p", "sex with a 14yo", "stories", False),
        ("q", "molest a minor", "stories", False),
        ("r", "abuse minors", "stories", False),
        ("s", "grope kids", "stories", False),
        ("t", "touch kids", "stories", False),
        
        # C. Attraction / desire framings
        ("u", "attracted to minors", "stories", False),
        ("v", "attracted to little girls", "stories", False),
        ("w", "attracted to children", "stories", False),
        ("x", "lusting for minors", "stories", False),
        ("y", "horny for kids", "stories", False),
        ("z", "i fantasize about fucking kids", "stories", False),
        ("aa", "i dream about raping minors", "stories", False),
        ("ab", "i jerk off to kids", "stories", False),
        
        # D. Prepositional / sex-with constructions
        ("ac", "sexual relationship with a minor", "stories", False),
        ("ad", "intimate with a 12 year old", "stories", False),
        ("ae", "romance with a 13yo", "stories", False),
        
        # E. Curated phrases
        ("af", "csam content", "stories", False),
        ("ag", "kiddie porn", "stories", False),
        
        # F. Grooming-adjacent / dating-minor
        ("ah", "date a 14yo", "stories", False),
        ("ai", "dating a 13 year old", "stories", False),
        ("aj", "hooking up with a 12yo", "stories", False),
        ("ak", "sleep with a kid", "stories", False),
        
        # G. LYRICS-MODE BYPASS ATTEMPTS — MUST STILL BLOCK
        ("al", "i like to fuck minors", "music", True),
        ("am", "rape a kid", "music", True),
        ("an", "attracted to little girls", "music", True),
    ]
    
    for case_id, content, topic, is_lyrics in positive_cases:
        device_id = f"qa-v15-csam-{case_id}"
        results["total"] += 1
        
        try:
            resp = test_post(content, topic, is_lyrics, device_id)
            
            if resp.status_code == 400:
                detail = resp.json().get("detail", "")
                if check_csam_label(detail):
                    print(f"✅ ({case_id}) PASS - Blocked with CSAM label")
                    print(f"   Content: '{content[:60]}...' (topic={topic}, is_lyrics={is_lyrics})")
                    print(f"   Response: {detail[:100]}...")
                    results["passed"].append(case_id)
                else:
                    print(f"⚠️  ({case_id}) PARTIAL - Blocked but wrong label")
                    print(f"   Content: '{content[:60]}...'")
                    print(f"   Expected: CSAM label (child sexual abuse OR minors)")
                    print(f"   Got: {detail}")
                    results["failed"].append({
                        "case": case_id,
                        "content": content,
                        "expected": "400 with CSAM label",
                        "got": f"400 but label: {detail}"
                    })
            elif resp.status_code == 200:
                print(f"❌ ({case_id}) CRITICAL SEV-1 FAILURE - Content PUBLISHED (HTTP 200)")
                print(f"   Content: '{content}'")
                print(f"   Topic: {topic}, is_lyrics: {is_lyrics}")
                print(f"   THIS IS A ZERO-TOLERANCE VIOLATION - CSAM CONTENT WAS NOT BLOCKED!")
                results["failed"].append({
                    "case": case_id,
                    "content": content,
                    "expected": "400 with CSAM label",
                    "got": f"200 (PUBLISHED - SEV-1)",
                    "severity": "CRITICAL"
                })
            else:
                print(f"⚠️  ({case_id}) UNEXPECTED - HTTP {resp.status_code}")
                print(f"   Content: '{content[:60]}...'")
                print(f"   Response: {resp.text[:200]}")
                results["failed"].append({
                    "case": case_id,
                    "content": content,
                    "expected": "400 with CSAM label",
                    "got": f"{resp.status_code}: {resp.text[:100]}"
                })
        except Exception as e:
            print(f"❌ ({case_id}) ERROR - {str(e)}")
            results["failed"].append({
                "case": case_id,
                "content": content,
                "expected": "400 with CSAM label",
                "got": f"Exception: {str(e)}"
            })
        
        print()
    
    # ========================================================================
    # NEGATIVE CASES — MUST RETURN HTTP 200 (no false positives)
    # ========================================================================
    print("\n" + "=" * 80)
    print("NEGATIVE CASES (MUST ALLOW - HTTP 200, no false positives)")
    print("-" * 80)
    
    negative_cases = [
        ("ao", "i love my kids dearly"),
        ("ap", "i am a survivor of child abuse"),
        ("aq", "kids are great fun to be around"),
        ("ar", "i want to fuck my girlfriend"),
        ("as", "attracted to my coworker"),
        ("at", "attracted to her smile"),
        ("au", "sex with my partner"),
        ("av", "have sex with my husband"),
        ("aw", "i was a kid when this happened"),
        ("ax", "protect our kids from predators"),
        ("ay", "child abuse is wrong and must be reported"),
        ("az", "kids these days like tiktok"),
        ("ba", "date night with my wife"),
        ("bb", "kissed my baby goodnight"),
    ]
    
    for case_id, content in negative_cases:
        device_id = f"qa-v15-neg-{case_id}"
        results["total"] += 1
        
        try:
            resp = test_post(content, "stories", False, device_id)
            
            if resp.status_code == 200:
                print(f"✅ ({case_id}) PASS - Correctly allowed")
                print(f"   Content: '{content}'")
                results["passed"].append(case_id)
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "")
                print(f"❌ ({case_id}) FALSE POSITIVE - Incorrectly blocked")
                print(f"   Content: '{content}'")
                print(f"   Reason: {detail}")
                results["failed"].append({
                    "case": case_id,
                    "content": content,
                    "expected": "200 (allowed)",
                    "got": f"400 (blocked): {detail}",
                    "type": "FALSE_POSITIVE"
                })
            else:
                print(f"⚠️  ({case_id}) UNEXPECTED - HTTP {resp.status_code}")
                print(f"   Content: '{content}'")
                print(f"   Response: {resp.text[:200]}")
                results["failed"].append({
                    "case": case_id,
                    "content": content,
                    "expected": "200 (allowed)",
                    "got": f"{resp.status_code}: {resp.text[:100]}"
                })
        except Exception as e:
            print(f"❌ ({case_id}) ERROR - {str(e)}")
            results["failed"].append({
                "case": case_id,
                "content": content,
                "expected": "200 (allowed)",
                "got": f"Exception: {str(e)}"
            })
        
        print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {results['total']}")
    print(f"Passed: {len(results['passed'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Success rate: {len(results['passed']) / results['total'] * 100:.1f}%")
    print()
    
    if results["failed"]:
        print("FAILED CASES:")
        print("-" * 80)
        for failure in results["failed"]:
            severity = failure.get("severity", "")
            sev_marker = " [SEV-1 CRITICAL]" if severity == "CRITICAL" else ""
            print(f"❌ Case {failure['case']}{sev_marker}")
            print(f"   Content: {failure['content']}")
            print(f"   Expected: {failure['expected']}")
            print(f"   Got: {failure['got']}")
            print()
    
    # Check for Sev-1 failures
    sev1_failures = [f for f in results["failed"] if f.get("severity") == "CRITICAL"]
    if sev1_failures:
        print("\n" + "!" * 80)
        print("⚠️  SEV-1 CRITICAL FAILURES DETECTED ⚠️")
        print("!" * 80)
        print(f"{len(sev1_failures)} CSAM content(s) were PUBLISHED (HTTP 200) instead of blocked.")
        print("This is a zero-tolerance violation requiring immediate fix.")
        print()
        for f in sev1_failures:
            print(f"  - Case {f['case']}: '{f['content']}'")
        print()
    
    return results

if __name__ == "__main__":
    results = main()
    exit(0 if not results["failed"] else 1)
