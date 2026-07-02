#!/usr/bin/env bash

PASS=0 FAIL=0

assert() {
    local label="$1" expected="$2" actual="$3"
    if [[ "$actual" == "$expected" ]]; then
        echo "  PASS | $label"
        ((PASS++))
    else
        echo "  FAIL | $label | expected: $expected | actual: $actual"
        ((FAIL++))
    fi
}

assert_contains() {
    local label="$1" needle="$2" haystack="$3"
    if echo "$haystack" | grep -qF "$needle" 2>/dev/null; then
        echo "  PASS | $label"
        ((PASS++))
    else
        echo "  FAIL | $label | expected to contain: $needle"
        ((FAIL++))
    fi
}

json_f() {
    python3 -c "
import sys,json
d=json.load(sys.stdin)
for k in '$1'.split('.'):
    if isinstance(d, dict): d=d.get(k,'')
    elif isinstance(d, list): d=d[int(k)] if k.isdigit() else d
    else: d=''
print(d)" <<<"$2" 2>/dev/null || echo ""
}

plen() {
    python3 -c "import sys,json;d=json.load(sys.stdin);items=d.get('results',d);print(len(items))" 2>/dev/null || echo "0"
}

pfirst() {
    python3 -c "import sys,json;d=json.load(sys.stdin);items=d.get('results',d);print(items[0].get('$1',''))" 2>/dev/null || echo ""
}

echo "============================================"
echo " HIREMATCH — FULL API TEST SUITE"
echo "============================================"
echo ""

# cleanup old processes
fuser -k 8000/tcp 2>/dev/null 1>&2 || true
fuser -k 8001/tcp 2>/dev/null 1>&2 || true
sleep 2
fuser 8000/tcp 2>/dev/null 1>&2 && { echo "ERROR: port 8000 still in use"; exit 1; } || true
fuser 8001/tcp 2>/dev/null 1>&2 && { echo "ERROR: port 8001 still in use"; exit 1; } || true

# fresh DB
cd /home/abhishek-atole/Desktop/mca_final_project/backend
rm -f db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python3 manage.py makemigrations > /dev/null 2>&1
python3 manage.py migrate > /dev/null 2>&1
DJANGO_SUPERUSER_PASSWORD=admin123 python3 manage.py createsuperuser --email=admin@test.com --role=admin --noinput > /dev/null 2>&1

# start services
python3 manage.py runserver 0.0.0.0:8000 &>/tmp/djtest.log &
sleep 3
cd /home/abhishek-atole/Desktop/mca_final_project/screening_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 &>/tmp/nlptest.log &
sleep 3

# warm up NLP service (slow first request due to TF-IDF init)
curl -s --max-time 20 -X POST http://localhost:8001/api/score/ -H "Content-Type: application/json" -d '{"resume_text":"x","job_description":"x"}' > /dev/null 2>&1

BASE="http://localhost:8000/api"
H="Content-Type: application/json"

echo "============================================"
echo " 1. PUBLIC ENDPOINTS"
echo "============================================"

r=$(curl -s -o /dev/null -w "%{http_code}" $BASE/jobs/)
assert "GET /api/jobs/ (unauthenticated) — 200" "200" "$r"

r=$(curl -s -o /dev/null -w "%{http_code}" $BASE/jobs/999/)
assert "GET /api/jobs/999/ (unauthenticated, not found) — 404" "404" "$r"

r=$(curl -s -w "\n%{http_code}" -X POST $BASE/auth/register/ -H "$H" -d '{"email":"bad"}' 2>&1)
assert "POST /api/auth/register/ (invalid data) — 400" "400" "$(echo "$r" | tail -1)"

echo ""
echo "============================================"
echo " 2. AUTHENTICATION"
echo "============================================"

r=$(curl -s -X POST $BASE/auth/register/ -H "$H" -d '{"email":"emp@test.com","password":"Test@1234","role":"employer"}')
assert_contains "Register employer — email" "emp@test.com" "$(json_f "email" "$r")"
assert_contains "Register employer — role employer" "employer" "$(json_f "role" "$r")"
id_emp=$(json_f "id" "$r")

r=$(curl -s -X POST $BASE/auth/register/ -H "$H" -d '{"email":"can@test.com","password":"Test@1234","role":"candidate","first_name":"Alice","last_name":"Smith"}')
assert_contains "Register candidate — email" "can@test.com" "$(json_f "email" "$r")"
id_can=$(json_f "id" "$r")

r=$(curl -s -w "\n%{http_code}" -X POST $BASE/auth/register/ -H "$H" -d '{"email":"emp@test.com","password":"Test@1234","role":"employer"}' 2>&1)
assert "Register duplicate email — 400" "400" "$(echo "$r" | tail -1)"

r=$(curl -s -X POST $BASE/auth/login/ -H "$H" -d '{"email":"emp@test.com","password":"Test@1234"}')
assert_contains "Login employer — has access" "access" "$r"
EMP_AT=$(json_f "access" "$r")
EMP_RT=$(json_f "refresh" "$r")

r=$(curl -s -X POST $BASE/auth/login/ -H "$H" -d '{"email":"can@test.com","password":"Test@1234"}')
CAN_AT=$(json_f "access" "$r")
CAN_RT=$(json_f "refresh" "$r")

r=$(curl -s -w "\n%{http_code}" -X POST $BASE/auth/login/ -H "$H" -d '{"email":"emp@test.com","password":"wrong"}' 2>&1)
assert "Login wrong password — 401" "401" "$(echo "$r" | tail -1)"

r=$(curl -s -X POST $BASE/auth/login/ -H "$H" -d '{"email":"admin@test.com","password":"admin123"}')
ADM_AT=$(json_f "access" "$r")

r=$(curl -s -X POST $BASE/auth/token/refresh/ -H "$H" -d "{\"refresh\":\"$EMP_RT\"}")
assert_contains "Token refresh — has access" "access" "$r"

r=$(curl -s $BASE/auth/me/ -H "Authorization: Bearer $EMP_AT")
assert "GET /api/auth/me/ (employer) — role" "employer" "$(json_f "role" "$r")"
assert "GET /api/auth/me/ (employer) — email" "emp@test.com" "$(json_f "email" "$r")"

r=$(curl -s $BASE/auth/me/ -H "Authorization: Bearer $CAN_AT")
assert "GET /api/auth/me/ (candidate) — role" "candidate" "$(json_f "role" "$r")"
assert "GET /api/auth/me/ (candidate) — first_name" "Alice" "$(json_f "first_name" "$r")"

echo ""
echo "============================================"
echo " 3. EMPLOYER ENDPOINTS"
echo "============================================"

r=$(curl -s -X PUT $BASE/employers/me/ -H "Authorization: Bearer $EMP_AT" -H "$H" -d '{"company_name":"TechCorp"}')
assert "PUT /api/employers/me/ — company_name" "TechCorp" "$(json_f "company_name" "$r")"

r=$(curl -s $BASE/employers/me/ -H "Authorization: Bearer $EMP_AT")
assert "GET /api/employers/me/ — company_name" "TechCorp" "$(json_f "company_name" "$r")"

r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
    -d '{"title":"Senior Python Developer","description":"Need Python, Django, PostgreSQL developer with 5+ years","required_skills":"Python,Django,PostgreSQL,REST,API","location":"Remote","salary_min":80000,"salary_max":120000,"employment_type":"full-time","experience_required":"5+ years"}')
JOB1_ID=$(json_f "id" "$r")
assert "POST /api/jobs/ — title" "Senior Python Developer" "$(json_f "title" "$r")"
assert "POST /api/jobs/ — employer_name" "TechCorp" "$(json_f "employer_name" "$r")"

r=$(curl -s $BASE/jobs/)
jr=$(echo "$r" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('results',d))" 2>/dev/null)
assert_contains "GET /api/jobs/ (public) — has our job" "Senior" "$jr"

r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
    -d '{"title":"Junior Developer","description":"Entry level Python dev","required_skills":"Python","location":"Office","salary_min":40000,"salary_max":60000}')
JOB2_ID=$(json_f "id" "$r")

r=$(curl -s $BASE/jobs/$JOB1_ID/)
assert "GET /api/jobs/$JOB1_ID/ — title" "Senior Python Developer" "$(json_f "title" "$r")"

r=$(curl -s -X PUT $BASE/jobs/$JOB1_ID/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
    -d '{"title":"Senior Python Developer (Updated)","description":"Need Python, Django, PostgreSQL dev","required_skills":"Python,Django,PostgreSQL,REST"}')
assert_contains "PUT /api/jobs/$JOB1_ID/ — updated title" "Updated" "$(json_f "title" "$r")"

r=$(curl -s $BASE/jobs/mine/ -H "Authorization: Bearer $EMP_AT")
count=$(echo "$r" | plen)
assert "GET /api/jobs/mine/ — count" "2" "$count"

r_srch=$(curl -s "$BASE/jobs/?search=Python")
assert_contains "GET /api/jobs/?search=Python — found" "Senior" "$r_srch"

# Candidate cannot create jobs
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/jobs/ -H "Authorization: Bearer $CAN_AT" -H "$H" -d '{"title":"Hacker","description":"test","required_skills":"x"}')
assert "POST /api/jobs/ (as candidate) — 403" "403" "$status"

# Candidate cannot access employer profile
status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/employers/me/ -H "Authorization: Bearer $CAN_AT")
assert "GET /api/employers/me/ (as candidate) — 403" "403" "$status"

echo ""
echo "============================================"
echo " 4. CANDIDATE ENDPOINTS"
echo "============================================"

r=$(curl -s -X PUT $BASE/candidates/me/ -H "Authorization: Bearer $CAN_AT" -H "$H" \
    -d '{"skills":"Python,Django,PostgreSQL,REST,API,Docker,React,TypeScript","experience_years":5,"education":"MCA","phone":"+1234567890","location":"Mumbai"}')
assert_contains "PUT /api/candidates/me/ — skills" "Python,Django" "$(json_f "skills" "$r")"
assert "PUT /api/candidates/me/ — education" "MCA" "$(json_f "education" "$r")"

# Employer cannot update candidate profile
status=$(curl -s -o /dev/null -w "%{http_code}" -X PUT $BASE/candidates/me/ -H "Authorization: Bearer $EMP_AT" -H "$H" -d '{"skills":"x"}')
assert "PUT /api/candidates/me/ (as employer) — 403" "403" "$status"

# Skill extraction from text
r=$(curl -s -X POST $BASE/candidates/extract-skills/ -H "Authorization: Bearer $CAN_AT" \
    -F "resume_file=@/dev/null" 2>/dev/null)
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/candidates/extract-skills/ -H "Authorization: Bearer $CAN_AT")
assert "Extract skills (no file) — 400" "400" "$code"

echo ""
echo "============================================"
echo " 5. APPLICATION ENDPOINTS"
echo "============================================"

r=$(curl -s -X POST $BASE/applications/jobs/$JOB1_ID/apply/ -H "Authorization: Bearer $CAN_AT")
assert "POST apply — status" "applied" "$(json_f "status" "$r")"
SCORE=$(json_f "match_score" "$r")
gt0=$(python3 -c "print(float('$SCORE') > 0)" 2>/dev/null || echo "False")
assert "POST apply — match_score > 0" "True" "$gt0"
assert "POST apply — job_title" "Senior Python Developer (Updated)" "$(json_f "job_title" "$r")"
assert "POST apply — candidate_name" "Alice Smith" "$(json_f "candidate_name" "$r")"
APP1_ID=$(json_f "id" "$r")

r=$(curl -s -w "\n%{http_code}" -X POST $BASE/applications/jobs/$JOB1_ID/apply/ -H "Authorization: Bearer $CAN_AT" 2>&1)
assert "POST apply duplicate — 400" "400" "$(echo "$r" | tail -1)"

# Candidate 2: register, login, profile, apply
curl -s -X POST $BASE/auth/register/ -H "$H" -d '{"email":"can2@test.com","password":"Test@1234","role":"candidate","first_name":"Bob","last_name":"Jones"}' > /dev/null
r2=$(curl -s -X POST $BASE/auth/login/ -H "$H" -d '{"email":"can2@test.com","password":"Test@1234"}')
CAN2_AT=$(json_f "access" "$r2")
curl -s -X PUT $BASE/candidates/me/ -H "Authorization: Bearer $CAN2_AT" -H "$H" -d '{"skills":"Java,Spring,SQL","experience_years":2,"education":"B.Tech"}' > /dev/null
r2=$(curl -s -X POST $BASE/applications/jobs/$JOB1_ID/apply/ -H "Authorization: Bearer $CAN2_AT")
APP2_ID=$(json_f "id" "$r2")
assert "POST apply (candidate2) — status" "applied" "$(json_f "status" "$r2")"
SCORE2=$(json_f "match_score" "$r2")

# View applicants (employer) — ranked by score descending
r=$(curl -s $BASE/applications/jobs/$JOB1_ID/applications/ -H "Authorization: Bearer $EMP_AT")
app_count=$(echo "$r" | plen)
assert "GET applications/ — count" "2" "$app_count"
# Verify ranking: first applicant should be higher score
first_score=$(echo "$r" | pfirst "match_score")
second_score=$(echo "$r" | python3 -c "import sys,json;d=json.load(sys.stdin);items=d.get('results',d);print(items[1].get('match_score','0'))" 2>/dev/null || echo "0")
ranked=$(python3 -c "print(float('$first_score') >= float('$second_score'))" 2>/dev/null || echo "False")
assert "Applicants ranked by score descending" "True" "$ranked"

# Candidate cannot view applicants
status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/applications/jobs/$JOB1_ID/applications/ -H "Authorization: Bearer $CAN_AT")
assert "GET applicants/ (as candidate) — 403" "403" "$status"

# Unauthenticated cannot view applicants
status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/applications/jobs/$JOB1_ID/applications/)
assert "GET applicants/ (unauthenticated) — 401" "401" "$status"

# Update status — shortlist candidate
r=$(curl -s -X PATCH $BASE/applications/$APP1_ID/status/ -H "Authorization: Bearer $EMP_AT" -H "$H" -d '{"status":"shortlisted"}')
assert "PATCH status — shortlisted" "shortlisted" "$(json_f "status" "$r")"

# Update status — reject candidate2
r=$(curl -s -X PATCH $BASE/applications/$APP2_ID/status/ -H "Authorization: Bearer $EMP_AT" -H "$H" -d '{"status":"rejected"}')
assert "PATCH status — rejected" "rejected" "$(json_f "status" "$r")"

# Invalid status value
status=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH $BASE/applications/$APP1_ID/status/ -H "Authorization: Bearer $EMP_AT" -H "$H" -d '{"status":"invalid_status"}')
assert "PATCH status (invalid value) — 400" "400" "$status"

# My applications (candidate)
r_my=$(curl -s $BASE/applications/me/ -H "Authorization: Bearer $CAN_AT")
my_count=$(echo "$r_my" | plen)
assert "GET /api/applications/me/ — count" "1" "$my_count"
my_title=$(echo "$r_my" | pfirst "job_title")
assert "GET /api/applications/me/ — job_title" "Senior Python Developer (Updated)" "$my_title"

# Employer cannot access my-applications
status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/applications/me/ -H "Authorization: Bearer $EMP_AT")
assert "GET /api/applications/me/ (as employer) — 403" "403" "$status"

echo ""
echo "============================================"
echo " 5b. AUTO-APPLY FLOW"
echo "============================================"

# Register and login a new candidate for auto-apply test
curl -s -X POST $BASE/auth/register/ -H "$H" -d '{"email":"can3@test.com","password":"Test@1234","role":"candidate","first_name":"Charlie","last_name":"Brown"}' > /dev/null
r=$(curl -s -X POST $BASE/auth/login/ -H "$H" -d '{"email":"can3@test.com","password":"Test@1234"}')
CAN3_AT=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('access',''))" 2>/dev/null)

# Create more jobs so there are 5+ to apply to
r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
  -d '{"title":"Frontend React Developer","description":"React TypeScript frontend role","required_skills":"React,TypeScript,CSS","location":"Remote"}')
JOB3_ID=$(json_f "id" "$r")
r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
  -d '{"title":"DevOps Engineer","description":"AWS Docker Kubernetes","required_skills":"AWS,Docker,Kubernetes","location":"Bangalore"}')
JOB4_ID=$(json_f "id" "$r")
r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
  -d '{"title":"Data Scientist","description":"ML Python TensorFlow","required_skills":"Python,TensorFlow,Machine Learning","location":"Hyderabad"}')
JOB5_ID=$(json_f "id" "$r")
r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" \
  -d '{"title":"Backend Go Developer","description":"Go PostgreSQL microservices","required_skills":"Go,PostgreSQL,Docker","location":"Pune"}')
JOB6_ID=$(json_f "id" "$r")

# Set skills on can3 and get recommendations
curl -s -X PUT $BASE/candidates/me/ -H "Authorization: Bearer $CAN3_AT" -H "$H" \
  -d '{"skills":"Python,React,TypeScript,Docker,AWS,PostgreSQL","experience_years":4,"education":"B.Tech"}' > /dev/null

rec_r=$(curl -s "$BASE/jobs/recommendations/" -H "Authorization: Bearer $CAN3_AT")
rec_count=$(echo "$rec_r" | python3 -c "
import sys,json
data=json.load(sys.stdin)
items = data.get('results',data) if isinstance(data,dict) else data
print(len(items))
" 2>/dev/null || echo "0")
assert "Recommendations returned" "True" "$(python3 -c "print(int('$rec_count') >= 3)" 2>/dev/null || echo "False")"

# Auto-apply: get top 3 recommendations and apply to each
top3=$(echo "$rec_r" | python3 -c "
import sys,json
data=json.load(sys.stdin)
items = data.get('results',data) if isinstance(data,dict) else data
print(' '.join(str(j['id']) for j in items[:3]))
" 2>/dev/null)
apply_count=0
for jid in $top3; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/applications/jobs/$jid/apply/" -H "Authorization: Bearer $CAN3_AT")
  if [ "$code" = "201" ]; then ((apply_count++)); fi
done
assert "Auto-apply created applications" "3" "$apply_count"

# Verify can3 has correct number of applications
r_my3=$(curl -s $BASE/applications/me/ -H "Authorization: Bearer $CAN3_AT")
my3_count=$(echo "$r_my3" | plen)
assert "Auto-apply — my applications count" "3" "$my3_count"

echo ""
echo "============================================"
echo " 6. NOTIFICATION ENDPOINTS"
echo "============================================"

r=$(curl -s $BASE/notifications/ -H "Authorization: Bearer $CAN_AT")
notif_count=$(echo "$r" | plen)
# Alice got shortlisted notification (only hers)
assert "GET /api/notifications/ (Alice) — count" "1" "$notif_count"
assert_contains "GET /api/notifications/ (Alice) — shortlisted" "shortlisted" "$r"

# Bob got rejected notification
r_bob=$(curl -s $BASE/notifications/ -H "Authorization: Bearer $CAN2_AT")
bob_count=$(echo "$r_bob" | plen)
assert "GET /api/notifications/ (Bob) — count" "1" "$bob_count"
assert_contains "GET /api/notifications/ (Bob) — rejected" "rejected" "$r_bob"

nid=$(echo "$r" | pfirst "id")
if [[ -n "$nid" ]]; then
    r=$(curl -s -X PUT $BASE/notifications/$nid/read/ -H "Authorization: Bearer $CAN_AT")
    assert "PUT /api/notifications/$nid/read/ — status" "read" "$(json_f "status" "$r")"
fi

r=$(curl -s -X PUT $BASE/notifications/read-all/ -H "Authorization: Bearer $CAN_AT")
assert "PUT /api/notifications/read-all/ — status" "all read" "$(json_f "status" "$r")"

# Employer notifications
r=$(curl -s $BASE/notifications/ -H "Authorization: Bearer $EMP_AT")
emp_notif_count=$(echo "$r" | plen)
assert "GET /api/notifications/ (employer) — 0" "0" "$emp_notif_count"

echo ""
echo "============================================"
echo " 7. ADMIN ENDPOINTS"
echo "============================================"

r=$(curl -s $BASE/admin/stats/ -H "Authorization: Bearer $ADM_AT")
assert "Admin stats — total_users" "5" "$(json_f "total_users" "$r")"
assert "Admin stats — total_jobs" "6" "$(json_f "total_jobs" "$r")"
assert "Admin stats — total_applications" "5" "$(json_f "total_applications" "$r")"
assert "Admin stats — shortlisted" "1" "$(json_f "applications_by_status.shortlisted" "$r")"
assert "Admin stats — rejected" "1" "$(json_f "applications_by_status.rejected" "$r")"

r=$(curl -s $BASE/admin/users/ -H "Authorization: Bearer $ADM_AT")
assert_contains "Admin list users — admin present" "admin@test.com" "$r"
assert_contains "Admin list users — employer present" "emp@test.com" "$r"
assert_contains "Admin list users — candidate present" "can@test.com" "$r"

# Non-admin cannot access admin endpoints
status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/admin/users/ -H "Authorization: Bearer $EMP_AT")
assert "GET /api/admin/users/ (as employer) — 403" "403" "$status"

status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/admin/stats/ -H "Authorization: Bearer $CAN_AT")
assert "GET /api/admin/stats/ (as candidate) — 403" "403" "$status"

status=$(curl -s -o /dev/null -w "%{http_code}" $BASE/admin/users/)
assert "GET /api/admin/users/ (unauthenticated) — 401" "401" "$status"

echo ""
echo "============================================"
echo " 8. SECURITY TESTS"
echo "============================================"

echo "  -- 401 on protected endpoints (no auth) --"
for ep in \
    "$BASE/auth/me/" \
    "$BASE/employers/me/" \
    "$BASE/candidates/me/" \
    "$BASE/applications/me/" \
    "$BASE/notifications/" \
    "$BASE/applications/jobs/$JOB1_ID/applications/"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$ep")
    if [[ "$code" == "401" ]]; then
        echo "  PASS | 401 (no auth) $ep"; ((PASS++))
    else
        echo "  FAIL | expected 401 got $code $ep"; ((FAIL++))
    fi
done

echo "  -- 403 on role mismatch --"
for entry in \
    "POST~$BASE/jobs/~$CAN_AT" \
    "GET~$BASE/applications/jobs/$JOB1_ID/applications/~$CAN_AT" \
    "GET~$BASE/admin/users/~$EMP_AT" \
    "GET~$BASE/applications/me/~$EMP_AT" \
    "GET~$BASE/employers/me/~$CAN_AT" \
    "PUT~$BASE/candidates/me/~$EMP_AT"; do
    IFS='~' read -r method url token <<< "$entry"
    if [[ "$method" == "POST" || "$method" == "PUT" || "$method" == "PATCH" ]]; then
        code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" -H "Authorization: Bearer $token" -H "$H" -d '{}')
    else
        code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" -H "Authorization: Bearer $token")
    fi
    if [[ "$code" == "403" || "$code" == "401" ]]; then
        echo "  PASS | $code (role mismatch) $method $url"; ((PASS++))
    else
        echo "  FAIL | expected 403 got $code $method $url"; ((FAIL++))
    fi
done

# Invalid JWT token
code=$(curl -s -o /dev/null -w "%{http_code}" $BASE/auth/me/ -H "Authorization: Bearer invalidtoken123")
assert "GET /api/auth/me/ (invalid token) — 401" "401" "$code"

# SQL injection attempt on login
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/auth/login/ -H "$H" -d '{"email":"\" OR 1=1 --","password":"x"}')
assert "SQL injection attempt — 401" "401" "$status"

# XSS attempt on job creation
r=$(curl -s -X POST $BASE/jobs/ -H "Authorization: Bearer $EMP_AT" -H "$H" -d '{"title":"<script>alert(1)</script>","description":"test","required_skills":"x"}')
assert "XSS attempt — title preserved" "<script>alert(1)</script>" "$(json_f "title" "$r")"
curl -s -X DELETE "$BASE/jobs/$(json_f "id" "$r")/" -H "Authorization: Bearer $EMP_AT" > /dev/null

# Mass assignment — candidate trying to set role=admin must fail
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/auth/register/ -H "$H" -d '{"email":"hacker@test.com","password":"Test@1234","role":"admin"}')
assert "Mass assignment — role=admin rejected" "400" "$code"

echo ""
echo "============================================"
echo " 9. ADMIN TOGGLE USER (must be last, deactivates candidate)"
echo "============================================"
r=$(curl -s -X PUT "$BASE/admin/users/$id_can/toggle/" -H "Authorization: Bearer $ADM_AT")
assert "Admin toggle — status" "toggled" "$(json_f "status" "$r")"
assert "Admin toggle — is_active" "False" "$(json_f "is_active" "$r")"
# Verify deactivated user cannot login
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/auth/login/ -H "$H" -d '{"email":"can@test.com","password":"Test@1234"}')
assert "Deactivated user login — 401" "401" "$status"

echo ""
echo "============================================"
echo " 10. JOB DELETE (SOFT DELETE)"
echo "============================================"
status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE $BASE/jobs/$JOB2_ID/ -H "Authorization: Bearer $EMP_AT")
assert "DELETE /api/jobs/$JOB2_ID/ — 204" "204" "$status"

r=$(curl -s $BASE/jobs/$JOB2_ID/ -H "Authorization: Bearer $EMP_AT")
assert "Job after delete — status=closed" "closed" "$(json_f "status" "$r")"

r=$(curl -s "$BASE/jobs/?search=Junior")
closed_hidden=$(echo "$r" | python3 -c "
import sys,json
from collections.abc import Mapping
d=json.load(sys.stdin)
items = d.get('results',d) if isinstance(d, Mapping) else d
print('hidden' if len(items)==0 else 'visible')
" 2>/dev/null || echo "unknown")
assert "Closed job hidden from public listing" "hidden" "$closed_hidden"

echo ""
echo "============================================"
echo " RESULTS"
echo "============================================"
echo "  PASSED: $PASS"
echo "  FAILED: $FAIL"
echo "============================================"

# cleanup
fuser -k 8000/tcp 2>/dev/null 1>&2 || true
fuser -k 8001/tcp 2>/dev/null 1>&2 || true

exit $FAIL
