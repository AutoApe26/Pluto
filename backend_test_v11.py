"""
Pluto Backend Testing v1.1 - New Features
Tests morse code detection, bot URL filtering, language detection, and translation.
"""
import requests
import json
import uuid
import time
from typing import Dict, Any, Optional

# Read backend URL from frontend/.env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BASE_URL = line.split('=', 1)[1].strip()
            break

API_URL = f"{BASE_URL}/api"
MOD_KEY = "pluto-mod-2026"

def new_device_id():
    """Generate a unique device ID for testing v1.1."""
    return f"qa-v11-{uuid.uuid4().hex[:12]}"

def post_content(content: str, topic: str = "stories", device_id: str = None) -> requests.Response:
    """Helper to POST content to /api/posts."""
    if device_id is None:
        device_id = new_device_id()
    payload = {
        "content": content,
        "topic": topic,
        "device_id": device_id
    }
    return requests.post(f"{API_URL}/posts", json=payload, timeout=30)

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
# 1. MORSE CODE DETECTION
# ============================================================================
def test_morse_code_detection():
    print_section("1. MORSE CODE DETECTION")
    
    passed_count = 0
    failed_count = 0
    
    # Test 1: SOS morse code (... --- ...)
    print("\nTest 1: SOS morse code '... --- ...' should be blocked")
    response = post_content("... --- ...", "stories")
    if response.status_code == 400:
        try:
            error_detail = response.json().get("detail", "")
            if "Morse code isn't allowed on Pluto." in error_detail:
                print_result("SOS morse code blocked", True)
                passed_count += 1
            else:
                print_result("SOS morse code blocked", False, 
                           f"Expected 'Morse code isn't allowed on Pluto.' but got '{error_detail}'")
                failed_count += 1
        except:
            print_result("SOS morse code blocked", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("SOS morse code blocked", False, 
                   f"Expected 400 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 2: Hello world in morse
    print("\nTest 2: 'Hello world' in morse should be blocked")
    morse_hello = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
    response = post_content(morse_hello, "stories")
    if response.status_code == 400:
        try:
            error_detail = response.json().get("detail", "")
            if "Morse code isn't allowed on Pluto." in error_detail:
                print_result("Hello world morse blocked", True)
                passed_count += 1
            else:
                print_result("Hello world morse blocked", False, 
                           f"Expected morse block but got '{error_detail}'")
                failed_count += 1
        except:
            print_result("Hello world morse blocked", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Hello world morse blocked", False, 
                   f"Expected 400 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 3: Morse with text mixed in
    print("\nTest 3: '... --- ... help me please' (morse + text) should be blocked")
    response = post_content("... --- ... help me please", "stories")
    if response.status_code == 400:
        try:
            error_detail = response.json().get("detail", "")
            if "Morse code isn't allowed on Pluto." in error_detail:
                print_result("Morse + text blocked", True)
                passed_count += 1
            else:
                print_result("Morse + text blocked", False, 
                           f"Expected morse block but got '{error_detail}'")
                failed_count += 1
        except:
            print_result("Morse + text blocked", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Morse + text blocked", False, 
                   f"Expected 400 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 4: Normal text with dashes (should NOT be blocked)
    print("\nTest 4: 'the score was 3-2 and i was sad...' (normal text) should pass")
    response = post_content("the score was 3-2 and i was sad about the game today", "sports")
    if response.status_code in [200, 201]:
        try:
            data = response.json()
            if "id" in data:
                print_result("Normal text with dashes allowed", True)
                passed_count += 1
            else:
                print_result("Normal text with dashes allowed", False, "Invalid response structure")
                failed_count += 1
        except:
            print_result("Normal text with dashes allowed", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Normal text with dashes allowed", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 5: Ellipses in normal English (should NOT be blocked)
    print("\nTest 5: 'yes... maybe... no' (ellipses) should pass")
    response = post_content("yes... maybe... no... i dont know what to think anymore", "rant")
    if response.status_code in [200, 201]:
        try:
            data = response.json()
            if "id" in data:
                print_result("Ellipses in normal text allowed", True)
                passed_count += 1
            else:
                print_result("Ellipses in normal text allowed", False, "Invalid response structure")
                failed_count += 1
        except:
            print_result("Ellipses in normal text allowed", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Ellipses in normal text allowed", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    print(f"\nMorse Code Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# 2. BOT POSTS CONTAIN NO URLs
# ============================================================================
def test_bot_posts_no_urls():
    print_section("2. BOT POSTS CONTAIN NO URLs")
    
    passed_count = 0
    failed_count = 0
    
    # Trigger bot run
    print("\nTriggering bot run with /api/mod/bots/run-now...")
    response = requests.post(
        f"{API_URL}/mod/bots/run-now",
        headers={"X-Mod-Key": MOD_KEY},
        timeout=60
    )
    
    if response.status_code == 200:
        print_result("Bot run triggered", True, f"Response: {response.json()}")
        passed_count += 1
    else:
        print_result("Bot run triggered", False, 
                   f"Expected 200 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
        # Continue anyway to check existing bot posts
    
    # Wait a bit for bots to post
    print("\nWaiting 3 seconds for bots to post...")
    time.sleep(3)
    
    # Fetch posts and check bot posts for URLs
    print("\nFetching posts to check bot content...")
    response = requests.get(f"{API_URL}/posts?limit=100", timeout=30)
    
    if response.status_code != 200:
        print_result("Fetch posts", False, 
                   f"Expected 200 but got {response.status_code}: {response.text[:200]}")
        return passed_count, failed_count + 1
    
    posts = response.json()
    print_result("Fetch posts", True, f"Found {len(posts)} posts")
    
    bot_posts = [p for p in posts if p.get("is_bot") is True]
    print(f"\nFound {len(bot_posts)} bot posts to check")
    
    if len(bot_posts) == 0:
        print("⚠️  WARNING: No bot posts found. Cannot verify URL filtering.")
        return passed_count, failed_count
    
    # Check each bot post for URLs
    url_patterns = [
        "http://", "https://", "www.", ".com", ".net", ".org", ".io", 
        ".co", ".gg", ".app", ".dev", ".xyz", ".me"
    ]
    
    bot_posts_with_urls = []
    for post in bot_posts:
        content = post.get("content", "").lower()
        for pattern in url_patterns:
            if pattern in content:
                bot_posts_with_urls.append({
                    "id": post.get("id"),
                    "content": post.get("content")[:100],
                    "pattern": pattern
                })
                break
    
    if len(bot_posts_with_urls) == 0:
        print_result(f"All {len(bot_posts)} bot posts contain no URLs", True)
        passed_count += 1
    else:
        print_result(f"Bot posts contain URLs", False, 
                   f"Found {len(bot_posts_with_urls)} bot posts with URLs")
        for bp in bot_posts_with_urls[:5]:  # Show first 5
            print(f"     Post {bp['id']}: contains '{bp['pattern']}' in '{bp['content']}'")
        failed_count += 1
    
    print(f"\nBot URL Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# 3. POST LANGUAGE DETECTION
# ============================================================================
def test_language_detection():
    print_section("3. POST LANGUAGE DETECTION")
    
    passed_count = 0
    failed_count = 0
    
    # Test 1: Spanish text
    print("\nTest 1: Spanish text should have lang='es'")
    spanish_text = "Hola mundo, hoy me siento muy feliz porque encontré algo hermoso"
    response = post_content(spanish_text, "stories")
    if response.status_code in [200, 201]:
        try:
            data = response.json()
            lang = data.get("lang")
            if lang == "es":
                print_result("Spanish language detected", True, f"lang='{lang}'")
                passed_count += 1
            else:
                print_result("Spanish language detected", False, 
                           f"Expected lang='es' but got lang='{lang}'")
                failed_count += 1
        except:
            print_result("Spanish language detected", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Spanish language detected", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 2: French text
    print("\nTest 2: French text should have lang='fr'")
    french_text = "Bonjour tout le monde, aujourd'hui je suis vraiment content"
    response = post_content(french_text, "stories")
    if response.status_code in [200, 201]:
        try:
            data = response.json()
            lang = data.get("lang")
            if lang == "fr":
                print_result("French language detected", True, f"lang='{lang}'")
                passed_count += 1
            else:
                print_result("French language detected", False, 
                           f"Expected lang='fr' but got lang='{lang}'")
                failed_count += 1
        except:
            print_result("French language detected", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("French language detected", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 3: English text
    print("\nTest 3: English text should have lang='en'")
    english_text = "this is a normal english sentence about my day and how i feel"
    response = post_content(english_text, "stories")
    if response.status_code in [200, 201]:
        try:
            data = response.json()
            lang = data.get("lang")
            if lang == "en":
                print_result("English language detected", True, f"lang='{lang}'")
                passed_count += 1
            else:
                print_result("English language detected", False, 
                           f"Expected lang='en' but got lang='{lang}'")
                failed_count += 1
        except:
            print_result("English language detected", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("English language detected", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    print(f"\nLanguage Detection Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# 4. TRANSLATE POST ENDPOINT
# ============================================================================
def test_translate_endpoint():
    print_section("4. TRANSLATE POST ENDPOINT")
    
    passed_count = 0
    failed_count = 0
    
    # Create a Spanish post first
    print("\nCreating a Spanish post for translation testing...")
    spanish_text = "Hola mundo, hoy me siento muy feliz porque encontré algo hermoso"
    response = post_content(spanish_text, "stories")
    
    if response.status_code not in [200, 201]:
        print_result("Create Spanish post", False, 
                   f"Failed to create post: {response.status_code} {response.text[:200]}")
        return 0, 1
    
    post_data = response.json()
    post_id = post_data.get("id")
    print_result("Create Spanish post", True, f"Post ID: {post_id}")
    
    # Test 1: First translation call (should return cached=false)
    print("\nTest 1: First translation call (should return cached=false)")
    response = requests.post(f"{API_URL}/posts/{post_id}/translate", timeout=30)
    
    if response.status_code == 200:
        try:
            data = response.json()
            translation = data.get("translation", "")
            lang = data.get("lang", "")
            cached = data.get("cached", None)
            
            # Check all required fields
            checks = []
            if translation and len(translation) > 0:
                checks.append(("translation non-empty", True))
            else:
                checks.append(("translation non-empty", False))
            
            if lang == "es":
                checks.append(("lang='es'", True))
            else:
                checks.append((f"lang='es' (got '{lang}')", False))
            
            if cached is False:
                checks.append(("cached=false", True))
            else:
                checks.append((f"cached=false (got {cached})", False))
            
            # Check if translation looks like English
            english_words = ["the", "a", "is", "are", "was", "were", "i", "you", "he", "she", "it", 
                           "today", "happy", "found", "something", "beautiful", "world", "feel"]
            has_english = any(word in translation.lower() for word in english_words)
            if has_english:
                checks.append(("translation is English", True))
            else:
                checks.append(("translation is English", False))
            
            all_passed = all(check[1] for check in checks)
            if all_passed:
                print_result("First translation call", True, 
                           f"translation='{translation[:60]}...', lang='{lang}', cached={cached}")
                passed_count += 1
            else:
                failed_checks = [c[0] for c in checks if not c[1]]
                print_result("First translation call", False, 
                           f"Failed checks: {', '.join(failed_checks)}")
                print(f"     Full response: {data}")
                failed_count += 1
        except Exception as e:
            print_result("First translation call", False, f"Error parsing response: {e}")
            failed_count += 1
    else:
        print_result("First translation call", False, 
                   f"Expected 200 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 2: Second translation call (should return cached=true)
    print("\nTest 2: Second translation call (should return cached=true)")
    response = requests.post(f"{API_URL}/posts/{post_id}/translate", timeout=30)
    
    if response.status_code == 200:
        try:
            data = response.json()
            cached = data.get("cached", None)
            translation = data.get("translation", "")
            
            if cached is True and translation:
                print_result("Second translation call (cached)", True, 
                           f"cached={cached}, translation='{translation[:60]}...'")
                passed_count += 1
            else:
                print_result("Second translation call (cached)", False, 
                           f"Expected cached=true but got cached={cached}")
                failed_count += 1
        except Exception as e:
            print_result("Second translation call (cached)", False, f"Error: {e}")
            failed_count += 1
    else:
        print_result("Second translation call (cached)", False, 
                   f"Expected 200 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 3: Non-existent post (should return 404)
    print("\nTest 3: Translate non-existent post (should return 404)")
    fake_id = str(uuid.uuid4())
    response = requests.post(f"{API_URL}/posts/{fake_id}/translate", timeout=30)
    
    if response.status_code == 404:
        print_result("Non-existent post returns 404", True)
        passed_count += 1
    else:
        print_result("Non-existent post returns 404", False, 
                   f"Expected 404 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    print(f"\nTranslation Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# 5. REGRESSION TESTS
# ============================================================================
def test_regression():
    print_section("5. REGRESSION TESTS")
    
    passed_count = 0
    failed_count = 0
    
    # Test 1: Links still blocked
    print("\nTest 1: Links should still be blocked")
    response = post_content("check https://malicious.com for more info", "rant")
    if response.status_code == 400:
        try:
            error_detail = response.json().get("detail", "")
            if "Links aren't allowed on Pluto." in error_detail:
                print_result("Links blocked", True)
                passed_count += 1
            else:
                print_result("Links blocked", False, f"Wrong error: '{error_detail}'")
                failed_count += 1
        except:
            print_result("Links blocked", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Links blocked", False, 
                   f"Expected 400 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    # Test 2: Same-content dedup 5x/24h still enforced
    print("\nTest 2: Same-content dedup 5x/24h still enforced")
    device_id = new_device_id()
    test_content = f"unique regression test message {uuid.uuid4().hex[:8]}"
    
    # Post 5 times (should succeed)
    success_count = 0
    for i in range(5):
        response = post_content(test_content, "rant", device_id)
        if response.status_code in [200, 201]:
            success_count += 1
    
    # 6th time should fail
    response = post_content(test_content, "rant", device_id)
    if success_count == 5 and response.status_code == 429:
        try:
            error_detail = response.json().get("detail", "")
            if "Same content max 5×/24h." in error_detail:
                print_result("Same-content dedup enforced", True)
                passed_count += 1
            else:
                print_result("Same-content dedup enforced", False, f"Wrong error: '{error_detail}'")
                failed_count += 1
        except:
            print_result("Same-content dedup enforced", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Same-content dedup enforced", False, 
                   f"First 5 posts: {success_count}/5 succeeded, 6th post: {response.status_code}")
        failed_count += 1
    
    # Test 3: Music endpoint still works
    print("\nTest 3: Music endpoint POST with YouTube link still works")
    music_payload = {
        "link_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "provider": "youtube",
        "title": "Test Song",
        "artist": "Test Artist",
        "device_id": new_device_id()
    }
    response = requests.post(f"{API_URL}/music", json=music_payload, timeout=30)
    
    if response.status_code in [200, 201]:
        try:
            data = response.json()
            if "id" in data and data.get("link_url"):
                print_result("Music endpoint works", True)
                passed_count += 1
            else:
                print_result("Music endpoint works", False, "Invalid response structure")
                failed_count += 1
        except:
            print_result("Music endpoint works", False, f"Invalid JSON: {response.text}")
            failed_count += 1
    else:
        print_result("Music endpoint works", False, 
                   f"Expected 200/201 but got {response.status_code}: {response.text[:200]}")
        failed_count += 1
    
    print(f"\nRegression Tests: {passed_count} passed, {failed_count} failed")
    return passed_count, failed_count

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print("\n" + "="*80)
    print("PLUTO BACKEND TESTING v1.1 - New Features")
    print(f"Testing against: {BASE_URL}")
    print("="*80)
    
    total_passed = 0
    total_failed = 0
    
    # Run all test sections
    test_sections = [
        ("Morse Code Detection", test_morse_code_detection),
        ("Bot Posts No URLs", test_bot_posts_no_urls),
        ("Language Detection", test_language_detection),
        ("Translate Endpoint", test_translate_endpoint),
        ("Regression Tests", test_regression),
    ]
    
    for section_name, test_func in test_sections:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
        except Exception as e:
            print(f"\n❌ {section_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            total_failed += 1
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    if (total_passed + total_failed) > 0:
        success_rate = 100 * total_passed / (total_passed + total_failed)
        print(f"Success Rate: {total_passed}/{total_passed + total_failed} ({success_rate:.1f}%)")
    print("="*80 + "\n")
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
