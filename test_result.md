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

user_problem_statement: "Test the Pluto backend's content moderation rules and the same-content rate limit on POST /api/posts. Test moderation rule enforcement, legitimate content passing, same-content rate limiting (5×/24h), reaction toggle/switch functionality, and bot human names verification."

backend:
  - task: "Content Moderation - Self-harm Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested 5 self-harm phrases including leetspeak and punctuation bypasses. All correctly blocked with 'Blocked: self-harm.' message. Phrases tested: 'I want to die tonight', 'going to kill myself', 'k!ll myself', 'k.i.l.l m.y.s.e.l.f', 'kiiillll myselfffff'. All returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Hate/Harassment Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested 2 hate/harassment phrases. Both correctly blocked with 'Blocked: hate/harassment.' message. Phrases tested: 'kill yourself loser', 'imma kill you'. All returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Sexual Content Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested 2 sexual content phrases. Both correctly blocked with 'Blocked: sexual content.' message. Phrases tested: 'send nudes', 'let's fuck tonight'. All returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Link Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested 2 link patterns. Both correctly blocked with 'Links aren't allowed on Pluto.' message. Phrases tested: 'check https://malicious.com', 'see www.scammer.io'. All returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Scams/Wallet-drainers Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested scam phrase 'send your seed phrase here'. Correctly blocked with 'Blocked: scams/wallet-drainers.' message. Returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Terror Promotion Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested terror phrase 'build a pipe bomb tutorial'. Correctly blocked with 'Blocked: terror promotion.' message. Returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Doxxing Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested doxxing phrase 'her address is 12 main st'. Correctly blocked with 'Blocked: doxxing.' message. Returned HTTP 400 with correct error detail."

  - task: "Content Moderation - Misinformation Detection"
    implemented: true
    working: true
    file: "/app/backend/moderation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested misinformation phrase 'vaccines cause autism'. Correctly blocked with 'Blocked: misinformation.' message. Returned HTTP 400 with correct error detail."

  - task: "Legitimate Content Acceptance"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested 5 legitimate content phrases that should pass moderation. All correctly accepted with HTTP 200/201 and valid Post response. Phrases tested: 'My therapist said I am doing great', 'Lost a friend to suicide last year, still hurts', 'I'm sad and tired, just venting', 'this game is wild', 'feeling really good today'. All returned valid post objects with id and content fields."

  - task: "Same-Content Rate Limit (5×/24h)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested same-content rate limiting with device_id 'qa-dedup-1'. Posted identical content 'this is a unique dedup test message' 5 times - all succeeded with HTTP 200/201. 6th attempt correctly blocked with HTTP 429 and error detail 'Same content max 5×/24h.'. Verified that posting different content from same device still works after rate limit. All 7 test cases passed."

  - task: "Post Reaction Toggle/Switch"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested reaction toggle and switch functionality on POST /api/posts/{id}/reaction. Created test post, then with device_id 'qa-react-1': (1) Added hug reaction - verified via GET /api/posts/{id}/my-reaction returns type:'hug'. (2) Toggled off hug - verified my-reaction returns type:null. (3) Added hug again - verified type:'hug'. (4) Switched to fug - verified type:'fug'. (5) Confirmed only ONE reaction at a time per device per post. All 5 test cases passed, unique constraint working correctly."

  - task: "Bot Human Names"
    implemented: true
    working: true
    file: "/app/backend/bot_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Tested bot human names by fetching GET /api/posts/trending. Triggered bot cycle via POST /api/mod/bots/run-now. Verified 5 bot posts, all have sudo_name in correct format: 'FirstName LastName' with proper capitalization. Examples: 'Rafael Silva', 'Noah Suzuki', 'Caleb Morales', 'Miles Silva', 'Sarah Hayes'. No old-style usernames like 'voidkitten' or 'lonelyfox42'. All bot posts correctly use real-looking human names from the FIRST_NAMES and LAST_NAMES pools."

frontend:
  # No frontend testing required for this review

metadata:
  created_by: "testing_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "All backend moderation and rate limiting tests completed"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "testing"
    message: "Completed comprehensive backend testing of Pluto content moderation rules, rate limiting, reaction toggle/switch, and bot names. All 32 test cases passed (15 moderation rules, 5 legitimate content, 7 rate limit tests, 5 reaction tests, 5 bot name verifications). No issues found. Backend is working correctly as per requirements."
