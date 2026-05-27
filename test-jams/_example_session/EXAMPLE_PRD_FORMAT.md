# Example: PRD-Based Test Case Format

This example shows how test cases are generated from PRD content with full traceability.

## Input Format

### User Provides:

**PRD URL**: 
```
https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD
```

**PRD Contents**:
```
Title: SMS Scheduling Feature

Section: Overview
This feature allows users to schedule SMS messages for future delivery...

Section: User Stories
1. As a marketer, I want to schedule SMS campaigns in advance
2. As a user, I want to edit scheduled messages before they send
3. As a user, I want to cancel scheduled messages

Section: Acceptance Criteria
- Users must be able to schedule SMS up to 30 days in advance
- System must send scheduled messages within 1 minute of scheduled time
- Users must receive confirmation when message is scheduled
- Users can view all scheduled messages in a dashboard

Section: Technical Requirements
- New API endpoint: POST /messages/schedule
- Database table: scheduled_messages
- Background job processor for sending scheduled messages
- Rate limiting: 100 scheduled messages per hour per account
```

## Generated Test Cases (Example CSV)

```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,PRD Reference
TC-001,Functional Testing,[PRD: SMS Scheduling Feature] [User Stories] Schedule SMS campaign in advance,P0,Manual,SMS Scheduling,Verify marketer can schedule SMS campaigns for future delivery,"User logged in; SMS plan active; Valid phone numbers available","1. Navigate to SMS dashboard
2. Click 'Schedule New Campaign'
3. Enter campaign details
4. Select future date/time (within 30 days)
5. Click 'Schedule'
6. Verify confirmation message","- Campaign scheduled successfully
- Confirmation message displayed
- Campaign appears in scheduled messages list","PRD: SMS Scheduling Feature | Section: User Stories | URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD"
TC-002,Functional Testing,[PRD: SMS Scheduling Feature] [User Stories] Edit scheduled message before sending,P1,Manual,SMS Scheduling,Verify user can modify scheduled messages before they are sent,"User logged in; At least one scheduled message exists","1. Navigate to scheduled messages dashboard
2. Select a scheduled message
3. Click 'Edit'
4. Modify message content or schedule time
5. Click 'Save Changes'
6. Verify updates applied","- Message content updated
- Schedule time updated if changed
- Confirmation of changes shown","PRD: SMS Scheduling Feature | Section: User Stories | URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD"
TC-003,Functional Testing,[PRD: SMS Scheduling Feature] [Acceptance Criteria] Schedule up to 30 days in advance,P0,Manual,SMS Scheduling,Verify system allows scheduling up to 30 days in future,"User logged in; SMS plan active","1. Navigate to SMS scheduling
2. Try to schedule for 29 days in future
3. Verify it's accepted
4. Try to schedule for 30 days in future
5. Verify it's accepted
6. Try to schedule for 31 days in future
7. Verify it's rejected","- 29 days: Accepted
- 30 days: Accepted
- 31 days: Rejected with clear error message","PRD: SMS Scheduling Feature | Section: Acceptance Criteria | URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD"
TC-004,Performance Testing,[PRD: SMS Scheduling Feature] [Acceptance Criteria] Send within 1 minute of scheduled time,P0,Automated,SMS Delivery,Verify scheduled messages send within 1 minute of scheduled time,"Scheduled message set up; System time synchronized","1. Schedule message for specific time
2. Monitor system at scheduled time
3. Record actual send time
4. Calculate difference between scheduled and actual","- Message sent within 60 seconds of scheduled time
- No messages sent early
- Timestamp accuracy verified","PRD: SMS Scheduling Feature | Section: Acceptance Criteria | URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD"
TC-005,API Testing,[PRD: SMS Scheduling Feature] [Technical Requirements] POST /messages/schedule endpoint validation,P0,Automated,SMS API,Verify schedule endpoint accepts valid requests and rejects invalid ones,"API credentials available; Valid test data","1. Send POST to /messages/schedule with valid payload
2. Verify 200 response with schedule confirmation
3. Send request with missing required fields
4. Verify 400 Bad Request response
5. Send request with invalid date format
6. Verify appropriate error response","- Valid requests: 200 OK with schedule_id
- Missing fields: 400 with clear error
- Invalid format: 400 with validation error
- Response includes scheduled_time confirmation","PRD: SMS Scheduling Feature | Section: Technical Requirements | URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD"
TC-006,Performance Testing,[PRD: SMS Scheduling Feature] [Technical Requirements] Rate limiting - 100 per hour,P1,Automated,Rate Limiting,Verify rate limiting enforces 100 scheduled messages per hour per account,"Test account available; API access","1. Schedule 99 messages in quick succession
2. Verify all accepted
3. Schedule 100th message
4. Verify accepted
5. Attempt 101st message within same hour
6. Verify rejected with 429 status","- First 100 messages: Accepted
- 101st message: 429 Too Many Requests
- Error message explains rate limit
- Retry-After header present","PRD: SMS Scheduling Feature | Section: Technical Requirements | URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature-PRD"
```

## Key Benefits of PRD Reference Column

1. **Traceability**: Every test case clearly links back to specific PRD section
2. **Validation**: Product can verify test cases match requirements
3. **Coverage Analysis**: Easy to see which PRD sections are well-tested
4. **Gap Identification**: Quickly identify PRD sections without test coverage
5. **Change Management**: When PRD changes, find affected test cases instantly

## Test Name Format

**Structure**: `[PRD: Title] [Section Name] Test Case Description`

**Examples**:
- `[PRD: SMS Scheduling Feature] [User Stories] Schedule SMS campaign in advance`
- `[PRD: Payment Integration] [Acceptance Criteria] Process credit card payment`
- `[PRD: Dashboard Redesign] [Technical Requirements] Load dashboard in under 2 seconds`

This format makes it immediately clear:
- ✅ Test is from a PRD (not a PR)
- ✅ Which PRD document
- ✅ Which section of the PRD
- ✅ What the test validates

