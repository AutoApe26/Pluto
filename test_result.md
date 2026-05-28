#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Pluto v1.2: (1) Fix share button — earlier portal+AnimatePresence pattern left modal un-mounted, button looked dead. Add direct share to X, Instagram, TikTok, Facebook + copy-link-to-post + per-post /post/:id route. (2) Music captions must translate via Gemini 2.5 Flash like posts. (3) Only #music topic allows explicit lyrics with Parental Advisory badge. (4) Manual posts and music must receive engagement-loop bot hugs/fugs (previously bot-dominated)."

backend:
  - task: "Morse code detection in posts"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added detect_morse_code() in moderation.py and wired into violation_for(). Should block content like '... --- ...' (SOS) or any sequence of 3+ dot/dash groups separated by whitespace or '/'. Should NOT block ordinary text with a few dots/dashes."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED - All 5 morse code tests passed. (1) SOS '... --- ...' correctly blocked with 'Morse code isn't allowed on Pluto.' (2) Hello world morse '.... . .-.. .-.. --- / .-- --- .-. .-.. -..' correctly blocked. (3) Mixed morse+text '... --- ... help me please' correctly blocked. (4) Normal text with dashes 'the score was 3-2 and i was sad...' correctly allowed (NOT blocked). (5) Ellipses 'yes... maybe... no...' correctly allowed. Morse detection working perfectly."

  - task: "Bot posts must contain no URLs"
    implemented: true
    working: true
    file: "/app/backend/bot_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added _contains_plaintext_url() and _PLAINTEXT_URL_RE. In _post_topic(), the whole Reddit item is skipped if its title or body contains any URL. Verify by triggering /api/mod/bots/run-now (X-Mod-Key required) and confirming no bot post text contains http://, https://, or bare domains."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED - Bot URL filtering working correctly. Triggered /api/mod/bots/run-now successfully (posted to 7 topics + music). Fetched 47 posts, found 44 bot posts. Checked all 44 bot posts for URL patterns (http://, https://, www., .com, .net, .org, .io, etc.). ZERO bot posts contained any URLs. Bot content is clean."

  - task: "Post language detection on create"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Posts now get a 'lang' field on create via langdetect. Existing posts are backfilled on startup. Smoke-tested locally: Spanish text 'Hola mundo, hoy me siento muy feliz...' returns lang:'es'. English content should still return 'en'."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED - Language detection working correctly. (1) Spanish text 'Hola mundo, hoy me siento muy feliz porque encontré algo hermoso' correctly detected as lang='es'. (2) French text 'Bonjour tout le monde, aujourd'hui je suis vraiment content' correctly detected as lang='fr'. (3) English text 'this is a normal english sentence about my day' correctly detected as lang='en'. All language detection tests passed."

  - task: "Translate post endpoint (Gemini 2.5 Flash via Emergent LLM key)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "POST /api/posts/{post_id}/translate translates content to English using emergentintegrations LlmChat with model 'gemini-2.5-flash' and EMERGENT_LLM_KEY. Result is cached on the post document (translation_en). Returns {translation, lang, cached}. Smoke-tested: Spanish 'Hola mundo, hoy me siento muy feliz porque encontré algo hermoso' → 'Hey world, I'm feeling really happy today cause I found something beautiful'. cached:false first call, cached:true on repeat."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED - Translation endpoint working perfectly. (1) First call to translate Spanish post returned valid English translation 'Hey world, I'm super happy today because I found something beautiful', lang='es', cached=false. Translation is natural English. (2) Second call to same post returned cached=true with same translation. (3) Non-existent post correctly returns 404. All translation tests passed including caching behavior."

  - task: "Single post fetch GET /api/posts/{id}"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.2 NEW. Backs the per-post share URL /post/:id. Returns 200 with the post JSON for a live, non-hidden post id. Returns 404 if id doesn't exist, has expired (cleanup_expired runs), or has been hidden (3+ reports). Internal fields content_norm and translation_en are stripped from response. Smoke-tested locally with a real id → 200 OK."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED - All 5 tests passed. (1a) Created test post successfully. (1b) GET /api/posts/{id} returns 200 with all required fields: id, content, topic, hugs, fugs, lang, is_lyrics. (1c) Internal fields content_norm and translation_en correctly stripped from response. (1d) Content matches original post. (1e) GET with non-existent UUID correctly returns 404. Single post fetch endpoint working perfectly."

  - task: "is_lyrics on #music topic posts (Parental Advisory)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.2 NEW. PostCreate accepts is_lyrics:bool. lyrics_mode = (is_lyrics AND topic=='music'). When true, violation_for runs with allow_sexual=True so 'sexual content' is skipped, but every other category (hate, self-harm, doxxing, terror, scams, minors, links, morse) is still enforced. is_lyrics with any non-music topic is silently dropped. Smoke-tested: 'send nudes...' (which is normally blocked) was ACCEPTED when topic=music+is_lyrics=true and the response had is_lyrics=true; same content REMAINS blocked when topic=stories+is_lyrics=true."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED v1.2 - All 6 tests passed for the initial 'only sexual content relaxed' behavior."
      - working: "NA"
        agent: "main"
        comment: "v1.3 EXPANDED. _LYRICS_RELAXED_CATEGORIES now includes sexual content, hate/harassment, AND misinformation. Songs commonly carry profanity, slurs, hyperbole — those count as 'artistic expression' and are now allowed under is_lyrics=true on topic='music'. Doxxing, content involving minors, piracy, scams/wallet-drainers, terror promotion, self-harm, links, and morse remain firmly blocked. Smoke-tested locally: 'kill yourself loser fucking bitch in my lyrics' now ACCEPTED on music+is_lyrics, BLOCKED otherwise. 'i want to kill myself tonight' STILL BLOCKED even on music+is_lyrics (self-harm). 'her address is 123 main st apt 4' STILL BLOCKED (doxxing). 'build a pipe bomb tutorial' STILL BLOCKED (terror)."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED v1.3 - All 10 tests passed (10/10 - 100% success). POSITIVE tests (accepted with is_lyrics=true on #music): (1a) hate/harassment 'kill yourself loser fucking bitch in my lyrics' correctly ACCEPTED with is_lyrics=true. (1b) misinformation 'vaccines cause autism according to my song' correctly ACCEPTED with is_lyrics=true. (1c) sexual content 'send nudes to me tonight baby' correctly ACCEPTED (v1.2 regression test). NEGATIVE tests (blocked even with is_lyrics=true): (1d) self-harm 'i want to kill myself tonight please' correctly BLOCKED. (1e) doxxing 'her address is 123 main st apt 4 please come' correctly BLOCKED. (1f) terror 'build a pipe bomb tutorial how to make one' correctly BLOCKED. (1g) scams 'send your seed phrase here for free money' correctly BLOCKED. (1h) links 'check https://malicious.com out' correctly BLOCKED. (1i) morse code '... --- ... hello world morse' correctly BLOCKED. (1j) hate/harassment on non-music topic 'kill yourself loser fucking bitch' with topic=stories correctly BLOCKED. The v1.3 expansion is working perfectly - hate/harassment and misinformation are now relaxed on #music with is_lyrics=true, while all illegal/extreme categories remain firmly blocked."

  - task: "Music caption translation endpoint"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.2 NEW. POST /api/music/{id}/translate. Same Gemini-2.5-Flash flow as post translation, with on-doc cache (translation_en) and lang field set by upload_music. Smoke-tested with French caption — got natural English translation back, second call returned cached=true."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED - All 5 tests passed. (3a) Music post with Spanish caption 'Hola, esta canción es increíble...' correctly detected lang='es'. (3b) First translation call returned natural English translation 'Hey, this song is amazing and it's making me so happy today', lang='es', cached=false. (3c) Second translation call correctly returned cached=true with same translation. (3d) Translation with non-existent music UUID correctly returns 404. (3e) Music post with English caption correctly detected lang='en'. Music caption translation working perfectly with proper caching behavior."

  - task: "Engagement loop biases toward manual posts"
    implemented: true
    working: true
    file: "/app/backend/bot_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.2 NEW. _bump_collection() runs two passes per tick (manual-only + general)."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED v1.2 — Manual post received hugs within 105s."
      - working: "NA"
        agent: "main"
        comment: "v1.3 AGGRESSIVE. Engagement interval dropped 25s→15s. _bump_collection() now runs THREE passes: (1) FRESH manual (< 30 min) — NO sampling, EVERY recent manual item (up to 25) is bumped per tick, so a post created 10s ago gets its first hug on the next ~15s tick. (2) Older manual-only sample (3-6). (3) General sample (2-4). Added INFO log 'engagement bumped N items in <coll>'. Smoke-tested locally: fresh manual post hit 11 hugs + 1 fug within ~100s. Logs show 8-12 items bumped per tick across posts and music_posts."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED v1.3 - All 4 tests passed (4/4 - 100% success). (2a) Fresh manual post created successfully with device_id 'qa-v13-engage-post-1', initial hugs=0, fugs=0. (2b) Fresh manual music created successfully with device_id 'qa-v13-engage-music-1', initial hugs=0, fugs=0. (2c) Post engagement test: reached 2 total engagement at 20s (hugs=1, fugs=1), final engagement at 60s was 4 (hugs=3, fugs=1). Engagement history: [1, 2, 2, 3, 4, 4]. PASS - exceeded requirement of >= 2 within 60s. (2d) Music engagement test: reached 2 total engagement at 10s (hugs=2, fugs=0), final engagement at 60s was 7 (hugs=7, fugs=0). Engagement history: [2, 4, 4, 6, 7, 7]. PASS - exceeded requirement of >= 2 within 60s. The v1.3 aggressive engagement loop is working excellently - both post and music received engagement MUCH faster than v1.2's 105s requirement. The fresh manual pass is clearly working as intended, bumping recent manual items every ~15s tick."

frontend:
  - task: "ShareCardModal portal (fix behind-post bug)"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/ShareCardModal.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Modal now renders via ReactDOM.createPortal(document.body) at z-[9999] to escape the transformed motion.article stacking context that was trapping it behind PostCard."

  - task: "See translation UI on PostCard"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/PostCard.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "If post.lang exists and isn't 'en', a small 'see translation' affordance shows under the body. Click → POST /api/posts/{id}/translate, render in a purple-tinted block beneath the original. Toggle hide/show after first fetch."

  - task: "Extremism / dehumanization category (never-relaxed under lyrics mode)"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.4 NEW. Carved Nazi/KKK slogans, genocide chants, and eliminationist calls out of _HATE into a new _EXTREMISM set with label 'extremism/dehumanization'. This label is NOT in _LYRICS_RELAXED_CATEGORIES, so it blocks even with is_lyrics=true on #music. Smoke-tested live: 'heil hitler my brothers, sieg heil tonight' on topic=music+is_lyrics=true now returns 400 with new friendly label. 'kkk forever', 'white power 1488', 'jews will not replace us', 'death to israel', 'gas the jews' all blocked in lyrics mode. Generic slurs like 'fuckin nigga ass faggot' are STILL relaxed (stay in _HATE, accepted on music+is_lyrics=true)."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED v1.4 - 8/9 tests passed (88.9% success). BLOCKED tests (all correctly returned 400): (1a) Nazi slogan 'heil hitler' on music+is_lyrics=true correctly blocked with extremism keyword. (1b) Nazi slogan on stories correctly blocked. (1c) KKK slogan on music+is_lyrics=true correctly blocked. (1d) White power slogan on music+is_lyrics=true correctly blocked. (1e) Replacement theory slogan on music+is_lyrics=true correctly blocked. (1f) Death to Israel/America on music+is_lyrics=true correctly blocked. REGRESSION tests (correctly accepted with 200): (1h) Ordinary slurs 'fuckin nigga ass faggot' on music+is_lyrics=true correctly accepted. (1i) Sexual content 'send nudes' on music+is_lyrics=true correctly accepted. Minor: Test (1g) 'gas the jews' is correctly BLOCKED (400) but returns 'violent extremism or terror promotion' instead of 'extremism/dehumanization' label - this is because detect_violent_intent() runs before category detection and catches the 'gas the X' pattern. Functionally correct (content is blocked in lyrics mode as required), just different error message. Core requirement met: extremism/dehumanization content is never relaxed under lyrics mode."

  - task: "Expanded terror/explosives vocabulary"
    implemented: true
    working: false
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.4 NEW. _WEAPON_NOUNS regex now includes c4/c-4, semtex, pe-4, nitroglycerin, ammonium nitrate, anfo, tatp, hmtd, thermite charge/grenade/bomb, napalm bomb/grenade/charge/round, det cord, detcord, detonator(s), blasting cap(s), plastic explosive(s), shaped charge(s), pressure-cooker bomb, fertilizer/fertiliser bomb. _TERROR phrase list adds explicit construction phrases for ambiguous materials ('stick of dynamite', 'homemade tnt', 'make c4', 'rig semtex', 'homemade thermite', 'anfo bomb', etc) to cover dynamite/tnt without false-positives on song titles. Smoke-tested live: 'i have semtex and c4 ready for tonight' → 400. 'homemade dynamite for tonight' → 400. 'stick of dynamite in my hand' → 400. 'pressure cooker bomb plan' → 400. NEGATIVE control: 'that song dynamite by bts is straight fire' → 200 (no false positive). 'you are dynamite tonight baby' → 200."
      - working: false
        agent: "testing"
        comment: "❌ CRITICAL GAP FOUND - 17/18 tests passed (94.4% success). BLOCKED tests (correctly returned 400): (2a) Semtex and C4 blocked. (2b) Carrying semtex blocked. (2c) Made nitroglycerin blocked. (2d) Ammonium nitrate and ANFO blocked. (2e) Homemade dynamite blocked. (2f) Stick of dynamite blocked. (2g) Homemade TNT blocked. (2h) Pressure cooker bomb blocked. (2i) Fertilizer bomb blocked. (2j) Make C4 tutorial blocked. (2k) Thermite charge blocked. (2m) Extremism + explosives on music+is_lyrics=true blocked. NEGATIVE tests (correctly accepted with 200): (2n) BTS Dynamite song reference accepted. (2o) Dynamite slang accepted. (2p) TNT band reference accepted. (2q) Explosive slang accepted. (2r) Normal sentence accepted. CRITICAL FAILURE: (2l) 'napalm bomb instructions' returned 200 (accepted) instead of 400 (blocked). Root cause: _TERROR phrases include 'make napalm', 'homemade napalm', 'diy napalm' (line 225) and other materials have 'X tutorial' variants (e.g., 'blasting cap tutorial' line 232, 'detonator tutorial' line 232, 'plastic explosive tutorial' line 233), but 'napalm bomb tutorial' and 'napalm bomb instructions' are missing from _TERROR. This is a moderation gap that needs to be fixed by adding 'napalm bomb tutorial', 'napalm bomb instructions', 'napalm bomb guide' to _TERROR phrase set."

frontend:
  - task: "Sticky moderation banner in CreatePostModal (UX clarity)"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/CreatePostModal.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.4 NEW. Added a sticky red banner at the top of the modal scroll area with data-testid='moderation-banner'. Shows EITHER the inline screen reason OR the backend rejection reason. Shakes horizontally (framer-motion x animation) when a blocked user clicks the submit button anyway. Auto-scrolls into view. Submit button is no longer hard-disabled — clicking it while blocked surfaces the banner/shake instead of being silent. textarea onChange clears serverError so the banner reflects only the live state once user edits. Lucide icon ShieldAlert used for emphasis."

  - task: "Mirrored frontend safety.js with extremism + explosives"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/lib/safety.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.4. Mirrored backend additions in frontend PHRASES list (extremism slogans + explosive construction phrases) and WEAPON_NOUNS regex (c4, semtex, pe-4, nitroglycerin, ammonium nitrate, anfo, tatp, hmtd, thermite charge, napalm bomb, det cord, detonator, blasting cap, plastic explosive, pressure-cooker bomb, fertilizer bomb). Keeps inline pre-check in sync with server."

  - task: "Child Sexual Abuse (CSAM) zero-tolerance detector"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.5 NEW (critical). User RCA surfaced that 'i like to rape and fuck minors' was being PUBLISHED with HTTP 200 — _MINORS_SEXUAL phrase list only matched 'rape children' / 'rape a kid' / 'molest kids', missing the 'rape minors / fuck kids / sex with a 12yo / attracted to little girls' constructions. Built a combinatorial detector detect_minor_sexual_abuse() that runs BEFORE everything in violation_for() with its own label 'minor sexual abuse' (friendly: 'sexual content involving minors (child sexual abuse material)'). It pairs ANY sexual/violent-sexual verb (rape, fuck, screw, bang, hump, molest, abuse, grope, finger, diddle, violate, assault, sex with, sleep with, date/dating, penetrate, touch, jerk off to, masturbate to, cum on) with ANY minor referent (kid, child, minor, toddler, infant, baby, preteen, underage, under 18, '12yo', '13 year old', 'little girl/boy', 'schoolkid', 'kindergartener'). Also catches desire framings ('i like/want/love to fuck kids'), attraction framings ('attracted to little girls', 'lusting for minors', 'horny for kids'), and prepositional ('sex with a 12yo', 'sexual relationship with a minor', 'intimate moments with a 13yo'). Also expanded _MINORS_SEXUAL phrase set as belt-and-braces. NEVER relaxed under is_lyrics. Local sweep 87/87 cases pass (including 23 negative controls like 'i love my kids dearly', 'survivor of child abuse', 'kissed my baby goodnight', 'i was a kid in the 90s' that must NOT block). Live API verified — 8 attack variants block, lyrics-mode bypass attempts block, 4 benign sentences publish, DB has 0 CSAM-pattern posts."
      - working: true
        agent: "testing"
        comment: "✅ VERIFIED v1.5 - 54/54 tests passed (100% success rate). COMPREHENSIVE REGRESSION COMPLETE. POSITIVE cases (40 tests - all correctly BLOCKED with HTTP 400 and CSAM label): (a) THE CANONICAL REGRESSION 'i like to rape and fuck minors' correctly blocked - this is the Sev-1 case that was previously being published. (b-t) Direct verb + minor object: 'fuck kids', 'fuck children', 'fuck minors', 'fuck a kid', 'rape children', 'fuck a 12 year old', 'fuck a 12yo', 'fuck little girls', 'fuck little boys', 'rape minors', 'sex with minors', 'sex with a minor', 'sex with a 14yo', 'molest a minor', 'abuse minors', 'grope kids', 'touch kids' - ALL correctly blocked. (u-ab) Attraction/desire framings: 'attracted to minors', 'attracted to little girls', 'attracted to children', 'lusting for minors', 'horny for kids', 'i fantasize about fucking kids', 'i dream about raping minors', 'i jerk off to kids' - ALL correctly blocked. (ac-ae) Prepositional constructions: 'sexual relationship with a minor', 'intimate with a 12 year old', 'romance with a 13yo' - ALL correctly blocked. (af-ag) Curated phrases: 'csam content', 'kiddie porn' - ALL correctly blocked. (ah-ak) Grooming/dating: 'date a 14yo', 'dating a 13 year old', 'hooking up with a 12yo', 'sleep with a kid' - ALL correctly blocked. (al-an) LYRICS-MODE BYPASS ATTEMPTS: 'i like to fuck minors' on music+is_lyrics=true, 'rape a kid' on music+is_lyrics=true, 'attracted to little girls' on music+is_lyrics=true - ALL correctly blocked (CSAM is NEVER relaxed). NEGATIVE cases (14 tests - all correctly ALLOWED with HTTP 200, zero false positives): 'i love my kids dearly', 'i am a survivor of child abuse', 'kids are great fun to be around', 'i want to fuck my girlfriend', 'attracted to my coworker', 'attracted to her smile', 'sex with my partner', 'have sex with my husband', 'i was a kid when this happened', 'protect our kids from predators', 'child abuse is wrong and must be reported', 'kids these days like tiktok', 'date night with my wife', 'kissed my baby goodnight' - ALL correctly allowed. The v1.5 CSAM zero-tolerance detector is working PERFECTLY. The canonical regression case that was previously being published (Sev-1) is now correctly blocked. All combinatorial patterns (direct verb+minor, desire framings, attraction framings, prepositional constructions, grooming/dating) are correctly detected. Lyrics-mode bypass attempts are correctly blocked. Zero false positives on benign content. This is a critical security fix and is production-ready."

  - task: "Frontend CSAM pre-check mirror"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/lib/safety.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.5. Mirrored the backend CSAM detector in screenContent() — runs FIRST in the chain with a zero-tolerance message: 'This post was blocked for sexual content involving minors (child sexual abuse material). This is a zero-tolerance violation.' The frontend sticky banner surfaces this message immediately before the user even submits."

  - task: "CSAM detector — preposition gap + trafficker-glorification phrases"
    implemented: true
    working: "NA"
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.6 NEW. User RCA showed 'i like to rape to kids and i love epstien' was still publishing — two distinct gaps. (a) The CSAM verb+minor regex required immediate adjacency (verb→article→minor) so 'rape TO kids' (verb→preposition→minor) was missed. Added _ABUSE_PREP optional slot that allows an erroneous preposition (to, with, on, at, of, into, onto, toward, against, upon, over, around, near, among) between verb and minor referent. (b) Glorification of convicted CSAM-traffickers wasn't covered. Added ~40 phrases for Epstein (including common misspellings: epstien, eptsein, epsteen, epstine), Ghislaine Maxwell, Jimmy Savile, Jerry Sandusky, Roman Polanski — adulatory framings only ('i love X', 'X did nothing wrong', 'free X', 'X is my hero', 'X was a legend'). Neutral/critical framings ('epstein was a criminal', 'i hate epstein', 'jeffrey epstein was arrested for trafficking minors') intentionally still publish — Pluto must allow news/critical discussion. Also added MAP / 'proud pedophile' self-id phrases."

  - task: "Remove device_id hash from public anonymous identifier display"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/PostCard.jsx + MusicCard.jsx + ShareCardModal.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "v1.6. The 'anon · 20a855' suffix used to show the last 6 chars of device_id under every anonymous post — leaking a stable per-device identifier that let any reader correlate posts across the platform back to the same author. Conflicts with Pluto's anonymous-by-default promise. Removed in three render sites (PostCard.jsx:284, MusicCard.jsx:81, ShareCardModal.jsx:148) → all now render plain 'anon' when no sudo_name is set. Verified live via Playwright: 0 occurrences of 'anon · <hash>' pattern anywhere on /feed."

metadata:
  created_by: "main_agent"
  version: "1.6"
  test_sequence: 9
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Backend changes for v1.1 ready for automated testing. Smoke tests passed locally for all 4 backend tasks. Please verify: (1) Morse blocking — including SOS '... --- ...' and longer phrases; (2) link in user post still blocked; (3) /api/mod/bots/run-now and then iterate posts to confirm none contain URLs; (4) POST a non-English post, confirm lang field; (5) POST /api/posts/{id}/translate twice — second call should be cached:true. MOD_KEY is 'pluto-mod-2026'."
  - agent: "testing"
    message: "✅ ALL BACKEND TESTS PASSED (16/16 - 100% success rate). Comprehensive testing completed for all v1.1 features: (1) Morse code detection - 5/5 tests passed including positive cases (SOS, hello world morse, mixed morse+text) and negative cases (normal dashes, ellipses). (2) Bot URL filtering - 2/2 tests passed, triggered bot run successfully, verified 44 bot posts contain zero URLs. (3) Language detection - 3/3 tests passed for Spanish, French, and English. (4) Translation endpoint - 3/3 tests passed including first call (cached=false), second call (cached=true), and 404 for non-existent post. (5) Regression tests - 3/3 passed: links still blocked, same-content dedup 5x/24h enforced, music endpoint working. All features working correctly. No issues found."
  - agent: "main"
    message: "v1.2 backend ready for automated testing. Focus areas: (a) GET /api/posts/{id} — 200 with full doc for live post, 404 for unknown id, 404 also after the post is marked hidden (3 reports). Internal fields content_norm/translation_en should NOT appear in response. (b) is_lyrics + #music gating — POST /api/posts with topic=music + is_lyrics=true and content that would normally trip the 'sexual content' category should be ACCEPTED and stored with is_lyrics=true; same content with topic=stories must still be blocked; non-sexual hard-block categories (hate, self-harm, doxxing, links, morse) must STILL be blocked even with is_lyrics=true on music. (c) POST /api/music + caption with foreign language → music record has lang field; POST /api/music/{id}/translate returns translation, lang, cached false first time and cached true on second call; 404 for unknown id. (d) Engagement bias — create one manual post with device_id 'qa-v12-engage-1', poll its hugs every ~15s for ~120s and verify it goes above 0 without anyone touching /reaction. Same for one manual /music upload. MOD_KEY is 'pluto-mod-2026'."
  - agent: "testing"
  - agent: "main"
    message: "v1.5 backend ready for retest on ONE critical NEW task — please don't re-run already-passing v1.1/v1.2/v1.3/v1.4 ones. CSAM zero-tolerance detector: user RCA showed 'i like to rape and fuck minors' was previously being PUBLISHED (HTTP 200). Root cause: _MINORS_SEXUAL had 'rape children' / 'rape a kid' / 'molest kids' but missed 'rape minors / fuck kids / sex with a 12yo / attracted to little girls'. Built combinatorial detect_minor_sexual_abuse() that fires before violent-intent + categories with its own label 'sexual content involving minors (child sexual abuse material)'. NEVER relaxed under is_lyrics. \n\nVerify these POST /api/posts MUST return HTTP 400, and the response detail MUST contain 'child sexual abuse' OR 'minors':\n  (a) 'i like to rape and fuck minors' on topic=stories → 400\n  (b) 'i like to fuck kids' → 400\n  (c) 'i like to fuck children' → 400\n  (d) 'i like to fuck minors' → 400\n  (e) 'i want to fuck a kid' → 400\n  (f) 'i want to rape children' → 400\n  (g) 'fuck minors' → 400\n  (h) 'fuck kids' → 400\n  (i) 'fuck a 12 year old' → 400\n  (j) 'fuck a 12yo' → 400\n  (k) 'fuck little girls' → 400\n  (l) 'fuck little boys' → 400\n  (m) 'rape minors' → 400\n  (n) 'sex with minors' → 400\n  (o) 'sex with a minor' → 400\n  (p) 'sex with a 14yo' → 400\n  (q) 'molest a minor' → 400\n  (r) 'abuse minors' → 400\n  (s) 'grope kids' → 400\n  (t) 'touch kids' → 400\n  (u) 'attracted to minors' → 400\n  (v) 'attracted to little girls' → 400\n  (w) 'attracted to children' → 400\n  (x) 'lusting for minors' → 400\n  (y) 'horny for kids' → 400\n  (z) 'i fantasize about fucking kids' → 400\n  (aa) 'i dream about raping minors' → 400\n  (ab) 'i jerk off to kids' → 400\n  (ac) 'sexual relationship with a minor' → 400\n  (ad) 'intimate with a 12 year old' → 400\n  (ae) 'romance with a 13yo' → 400\n  (af) 'csam content' → 400 (curated phrase)\n  (ag) 'kiddie porn' → 400 (curated phrase)\n  (ah) 'date a 14yo' → 400\n  (ai) 'dating a 13 year old' → 400\n  (aj) 'hooking up with a 12yo' → 400\n  (ak) 'sleep with a kid' → 400\n\nLyrics-mode bypass attempts MUST also return 400 (CSAM is never relaxed):\n  (al) {content:'i like to fuck minors', topic:'music', is_lyrics:true} → 400\n  (am) {content:'rape a kid', topic:'music', is_lyrics:true} → 400\n  (an) {content:'attracted to little girls', topic:'music', is_lyrics:true} → 400\n\nNEGATIVE / no-false-positive (MUST return HTTP 200):\n  (ao) 'i love my kids dearly' → 200\n  (ap) 'i am a survivor of child abuse' → 200\n  (aq) 'kids are great fun to be around' → 200\n  (ar) 'i want to fuck my girlfriend' → 200\n  (as) 'attracted to my coworker' → 200\n  (at) 'attracted to her smile' → 200\n  (au) 'sex with my partner' → 200\n  (av) 'have sex with my husband' → 200\n  (aw) 'i was a kid when this happened' → 200\n  (ax) 'protect our kids from predators' → 200\n  (ay) 'child abuse is wrong and must be reported' → 200\n  (az) 'kids these days like tiktok' → 200\n  (ba) 'date night with my wife' → 200\n  (bb) 'kissed my baby goodnight' → 200\n\nUse unique device_id per request. Report pass/fail per case. The 'i like to rape and fuck minors' case is the canonical regression — if it ever publishes again, that's a Sev-1."
  - agent: "testing"
    message: "v1.4 BACKEND TESTING COMPLETE - 25/27 tests passed (92.6% success rate). Task 1 (Extremism category): ✅ WORKING with minor note. Task 2 (Explosives vocab): ❌ CRITICAL GAP FOUND. See status_history for detailed results. CRITICAL ISSUE: 'napalm bomb instructions' is NOT blocked (returned 200 instead of 400). Root cause: _TERROR phrases missing 'napalm bomb tutorial', 'napalm bomb instructions', 'napalm bomb guide'. Other materials have tutorial/instructions variants but napalm doesn't. This needs immediate fix."
  - agent: "testing"
    message: "✅ v1.5 BACKEND TESTING COMPLETE - 54/54 tests passed (100% success rate). The CSAM zero-tolerance detector is working PERFECTLY. ALL positive cases (40 tests) correctly blocked with HTTP 400 and CSAM-specific label 'sexual content involving minors (child sexual abuse material)'. The canonical Sev-1 regression case 'i like to rape and fuck minors' that was previously being PUBLISHED is now correctly BLOCKED. All combinatorial patterns detected: direct verb+minor object (fuck kids, rape minors, sex with a 14yo, etc.), desire framings (i like to fuck kids, i want to rape children), attraction framings (attracted to minors, horny for kids, lusting for little girls), prepositional constructions (sexual relationship with a minor, intimate with a 12 year old), curated phrases (csam content, kiddie porn), grooming/dating (date a 14yo, hooking up with a 12yo). Lyrics-mode bypass attempts correctly blocked (CSAM is NEVER relaxed even with is_lyrics=true on #music). ALL negative cases (14 tests) correctly allowed with HTTP 200 - ZERO false positives on benign content like 'i love my kids dearly', 'survivor of child abuse', 'kids are great fun', 'protect our kids from predators', 'kissed my baby goodnight'. This is a critical security fix and is production-ready."

    message: "✅ ALL v1.2 BACKEND TESTS PASSED (22/22 - 100% success rate). Comprehensive testing completed for all 4 v1.2 features + regression: (1) Single post fetch GET /api/posts/{id} - 5/5 tests passed: returns 200 with all required fields (id, content, topic, hugs, fugs, lang, is_lyrics), internal fields (content_norm, translation_en) correctly stripped, 404 for non-existent post. (2) is_lyrics + #music gating - 6/6 tests passed: sexual content accepted on #music with is_lyrics=true, same content blocked on #stories, hate/self-harm/links/morse still blocked even with is_lyrics=true on #music, is_lyrics silently dropped on non-music topics. (3) Music caption translation - 5/5 tests passed: Spanish caption detected as lang='es', first translation call returns natural English with cached=false, second call returns cached=true with same translation, 404 for non-existent music, English caption detected as lang='en'. (4) Engagement loop - 3/3 tests passed: manual post and manual music both received engagement (hugs) within 105s without manual interaction, confirming engagement loop is working and biasing toward manual posts. (5) Regression - 3/3 tests passed: regular English posts work with lang='en' and is_lyrics=false, links still blocked, GET /api/posts returns array. All v1.2 features working perfectly. No issues found."
