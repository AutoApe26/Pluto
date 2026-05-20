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

user_problem_statement: "Add features to Pluto: (1) Fix share modal — pluck card was appearing behind the post due to transformed parent stacking context. (2) Block Morse code in posts; keep link blocking for user posts; bots must not post any links. (3) Add language detection on post create + on-demand English translation via Gemini 2.5 Flash with caching."

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

metadata:
  created_by: "main_agent"
  version: "1.1"
  test_sequence: 3
  run_ui: false

test_plan:
  current_focus:
    - "Morse code detection in posts"
    - "Bot posts must contain no URLs"
    - "Post language detection on create"
    - "Translate post endpoint (Gemini 2.5 Flash via Emergent LLM key)"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Backend changes for v1.1 ready for automated testing. Smoke tests passed locally for all 4 backend tasks. Please verify: (1) Morse blocking — including SOS '... --- ...' and longer phrases; (2) link in user post still blocked; (3) /api/mod/bots/run-now and then iterate posts to confirm none contain URLs; (4) POST a non-English post, confirm lang field; (5) POST /api/posts/{id}/translate twice — second call should be cached:true. MOD_KEY is 'pluto-mod-2026'."
  - agent: "testing"
    message: "✅ ALL BACKEND TESTS PASSED (16/16 - 100% success rate). Comprehensive testing completed for all v1.1 features: (1) Morse code detection - 5/5 tests passed including positive cases (SOS, hello world morse, mixed morse+text) and negative cases (normal dashes, ellipses). (2) Bot URL filtering - 2/2 tests passed, triggered bot run successfully, verified 44 bot posts contain zero URLs. (3) Language detection - 3/3 tests passed for Spanish, French, and English. (4) Translation endpoint - 3/3 tests passed including first call (cached=false), second call (cached=true), and 404 for non-existent post. (5) Regression tests - 3/3 passed: links still blocked, same-content dedup 5x/24h enforced, music endpoint working. All features working correctly. No issues found."
