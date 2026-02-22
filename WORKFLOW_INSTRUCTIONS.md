# Dream Axis Lead Bot - Workflow Instructions

## 📋 Overview

This WhatsApp bot collects lead information for truck and trailer driving jobs in Europe. It handles GDPR consent, multilingual support, and stores data in Google Sheets.

---

## 🔄 Complete Conversation Flow

### Stage 1: First Contact & Language Detection

1) When a user sends their **first message**, automatically detect their language from the message content.
2) Supported languages: English (en), Polish (pl), German (de), Spanish (es), Ukrainian (uk), Hindi (hi), Malayalam (ml).
3) Store the detected language for all future messages with this user.
4) Immediately proceed to **Stage 2: GDPR Consent**.

---

### Stage 2: Welcome Message & GDPR Consent Collection

**Step 1: Send Welcome Message (First Message)**

Send a welcome message in the user's detected language:

| Language | Welcome Message |
|----------|-----------------|
| English | "👋 Welcome to Dream Axis Travel Solutions! We help connect skilled drivers with truck and trailer driving opportunities across Europe. We're excited to assist you on your journey!" |
| Polish | "👋 Witamy w Dream Axis Travel Solutions! Pomagamy łączyć wykwalifikowanych kierowców z możliwościami pracy jako kierowca ciężarówki i naczepy w całej Europie. Z przyjemnością pomożemy Ci w Twojej podróży!" |
| German | "👋 Willkommen bei Dream Axis Travel Solutions! Wir helfen qualifizierten Fahrern, LKW- und Anhängerfahrmöglichkeiten in ganz Europa zu finden. Wir freuen uns, Sie auf Ihrem Weg zu unterstützen!" |
| Spanish | "👋 ¡Bienvenido a Dream Axis Travel Solutions! Ayudamos a conectar conductores calificados con oportunidades de conducción de camiones y remolques en toda Europa. ¡Estamos emocionados de ayudarte en tu camino!" |

**Step 2: Send GDPR Consent Message (Second Message - immediately after welcome)**

Send the GDPR consent message in the user's detected language:
   ```
   Before we continue, we need your permission to process your personal data.
   
   Dream Axis Travel Solutions will use your information only for recruitment 
   related to truck and trailer driving jobs in Europe.
   
   Your data will be stored securely and you may request deletion at any time 
   by replying DELETE.
   
   Reply YES to agree or NO to stop.
   ```

**Step 3: Wait for the user's response:**
   - **If YES** (or language-equivalent: TAK, JA, SÍ, ТАК, हाँ, അതെ):
     - Record consent timestamp
     - Send confirmation: "Thank you for your consent. Let's proceed with collecting your information."
     - Proceed to **Stage 3: Lead Data Collection**
   
   - **If NO** (or language-equivalent: NIE, NEIN, НІ, नहीं, ഇല്ല):
     - Send confirmation: "Understood. Your data will not be processed. You can contact us again if you change your mind."
     - End conversation and clear conversation state
     - Do NOT create any record in Google Sheets
   
   - **If invalid response**:
     - Resend the consent message
     - Wait for valid YES/NO response

---

### Stage 3: Lead Data Collection

**Collect information in this order, ONE question at a time:**

| Step | Bot Field | Sheet Column | Question Example | Validation |
|------|-----------|--------------|------------------|------------|
| 1 | `full_name` | `Full Name` (E) | "What is your full name?" | Required, non-empty |
| 2 | `email` | `Email` (G) | "What is your email address?" | Valid email format |
| 3 | `phone` | `Phone Number` (F) | "What is your phone number with country code?" | Valid phone (7-15 digits) |
| 4 | `location` | `Place/Location` (D) | "Where are you currently located?" | Required, non-empty |

**Auto-populated fields (not collected from user):**

| Sheet Column | Value | When Set |
|--------------|-------|----------|
| `User ID` (A) | WhatsApp phone number | On first contact |
| `Timestamp` (B) | Current UTC timestamp | On lead save |
| `Service Type` (C) | "Truck/Trailer Driver" (default) | On lead save |
| `Status` (H) | "New" | On lead save |
| `Channel` (K) | "WhatsApp" | On lead save |
| `consent_status` (L) | "Granted" | After YES response |
| `consent_timestamp` (M) | Current UTC timestamp | After YES response |
| `consent_version` (N) | "v1.0" | After YES response |
| `consent_text` (O) | Full consent message | After YES response |
| `Platform` (P) | "WhatsApp Business API" | On lead save |

**Collection Rules:**

1) Ask for **one piece of information at a time**.
2) Wait for the user's reply before asking the next question.
3) Use OpenAI to extract data from natural language responses.
4) If the user provides multiple pieces of information in one message, extract all of them.
5) Always ask questions in the user's detected language.
6) Validate each field before moving to the next question.
7) If validation fails, ask the user to provide the information again.
8) **Send reminder if no response within 10 minutes** (see Stage 3.1 below).

---

### Stage 3.1: Reminder System (No Response Handling)

**Purpose:** Prevent leads from abandoning the conversation halfway.

**Reminder Logic:**

1) After sending any question, start a **10-minute timer**.

2) If user responds within 10 minutes:
   - Cancel the timer
   - Process the response normally
   - Start new timer for next question

3) If user does NOT respond within 10 minutes:
   - Send a **friendly reminder message**
   - Reset timer for another 10 minutes (optional: for 2nd reminder)

4) **Reminder message examples (in user's language):**

   | Language | Reminder Message |
   |----------|------------------|
   | English | "Hi! Just checking in - are you still there? We'd love to help you find a driving job in Europe. 😊" |
   | Polish | "Cześć! Sprawdzamy tylko - czy nadal tam jesteś? Chętnie pomożemy Ci znaleźć pracę kierowcy w Europie. 😊" |
   | German | "Hallo! Wir wollten nur nachfragen - sind Sie noch da? Wir helfen Ihnen gerne, einen Fahrerjob in Europa zu finden. 😊" |
   | Spanish | "¡Hola! Solo verificamos - ¿sigues ahí? Nos encantaría ayudarte a encontrar un trabajo de conductor en Europa. 😊" |

5) **Maximum reminders:** Send up to **2 reminders** (at 10 min and 20 min).

6) **After 2nd reminder (30 minutes total):**
   - Mark conversation as "Abandoned" in state
   - Optionally: Save partial lead data with Status = "Incomplete"
   - Stop sending reminders

**Reminder Schedule:**

| Time | Action |
|------|--------|
| 0 min | Bot sends question |
| 10 min | 1st Reminder: "Hi! Just checking in..." |
| 20 min | 2nd Reminder: "We're still here if you'd like to continue..." |
| 30 min | Stop reminders, mark as abandoned |

**State Tracking for Reminders:**

```json
{
  "phone": "917736053341",
  "last_message_time": "2024-01-15T10:30:00Z",
  "reminder_count": 0,
  "last_question": "What is your email address?",
  "stage": "collection"
}
```

---

### Stage 4: Save Lead & Notify

After collecting **ALL required fields** (full_name, email, phone, location):

1) **Create lead record for Google Sheets → `Leads` sheet:**

   | Column | Field | Value |
   |--------|-------|-------|
   | A | `User ID` | WhatsApp phone number |
   | B | `Timestamp` | Current UTC timestamp |
   | C | `Service Type` | "Truck/Trailer Driver" (default) |
   | D | `Place/Location` | Collected `location` |
   | E | `Full Name` | Collected `full_name` |
   | F | `Phone Number` | Collected `phone` |
   | G | `Email` | Collected `email` |
   | H | `Status` | "New" |
   | I | `Documents` | "" (empty) |
   | J | `Notes` | "" (empty) |
   | K | `Channel` | "WhatsApp" |
   | L | `consent_status` | "Granted" |
   | M | `consent_timestamp` | Consent timestamp |
   | N | `consent_version` | "v1.0" |
   | O | `consent_text` | Full consent text shown |
   | P | `Platform` | "WhatsApp Business API" |

2) **Save to Google Sheets** using **Add Row** operation on `Leads` sheet.

3) **Log consent to `Consent_Log` sheet:**

   | Column | Value |
   |--------|-------|
   | A | WhatsApp phone number |
   | B | Current timestamp |
   | C | "Granted" |
   | D | "v1.0" |
   | E | Full consent text |
   | F | "WhatsApp" |

4) **Send email notification** to admin with lead details.

5) **Send confirmation to user**:
   ```
   Thank you! Your information has been recorded. We'll be in touch soon.
   ```

6) Clear conversation state for this phone number.

---

## 🗑️ GDPR Delete Request Handling

**At any point in the conversation**, if the user sends "DELETE" (or language equivalent):

1) **Search `Leads` sheet** for row where `User ID` (Column A) matches WhatsApp phone number.

2) **If found:**
   - Delete the row from `Leads` sheet
   - **Log deletion to `Consent_Log` sheet:**
     | Column | Value |
     |--------|-------|
     | A | WhatsApp phone number |
     | B | Current timestamp |
     | C | "Deleted" |
     | D | "v1.0" |
     | E | "User requested deletion" |
     | F | "WhatsApp" |
   - Send confirmation: "Your data has been successfully deleted from our records."
   - Clear conversation state

3) **If not found:**
   - Send: "No records found for this phone number."

---

## 📊 Google Sheets Structure

### Spreadsheet: Dream Axis Leads

The spreadsheet contains **4 sheets**:
- **Leads** (main lead data)
- **Appointment** (appointment bookings)
- **Consent_Log** (consent audit trail)
- **FAQ** (frequently asked questions)

---

### Sheet: `Leads` (Primary Data Storage)

| Column | Field Name | Data to Store | Read/Write |
|--------|------------|---------------|------------|
| A | `User ID` | WhatsApp phone number (unique identifier) | **Read** (for lookup), **Write** (new lead) |
| B | `Timestamp` | Record creation time (UTC ISO format) | **Write** |
| C | `Service Type` | Type of service/job interested in (e.g., "Truck Driver", "Trailer Driver") | **Write** |
| D | `Place/Location` | User's current location/country | **Write** |
| E | `Full Name` | User's full name | **Write** |
| F | `Phone Number` | Phone number provided by user | **Write** |
| G | `Email` | User's email address | **Write** |
| H | `Status` | Lead status: "New", "Contacted", "Qualified", "Converted" | **Write** (default: "New") |
| I | `Documents` | Document links/status (if any) | **Write** (optional) |
| J | `Notes` | Additional notes about the lead | **Write** (optional) |
| K | `Channel` | Source channel: "WhatsApp" | **Write** |
| L | `consent_status` | "Granted" or "Denied" | **Write** |
| M | `consent_timestamp` | When consent was given (UTC) | **Write** |
| N | `consent_version` | Version of consent text: "v1.0" | **Write** |
| O | `consent_text` | Full consent text shown to user | **Write** |
| P | `Platform` | Platform used: "WhatsApp Business API" | **Write** |

---

### Sheet: `Consent_Log` (GDPR Audit Trail)

| Column | Field Name | Data to Store | Read/Write |
|--------|------------|---------------|------------|
| A | `User ID` | WhatsApp phone number | **Write** |
| B | `Timestamp` | When consent action occurred | **Write** |
| C | `Action` | "Granted", "Denied", "Deleted" | **Write** |
| D | `consent_version` | Version of consent text | **Write** |
| E | `consent_text` | Full consent text shown | **Write** |
| F | `IP/Channel` | "WhatsApp" | **Write** |

---

### Sheet: `Appointment` (If booking appointments)

| Column | Field Name | Data to Store | Read/Write |
|--------|------------|---------------|------------|
| A | `User ID` | WhatsApp phone number | **Read/Write** |
| B | `Timestamp` | Appointment booking time | **Write** |
| C | `Appointment Date` | Scheduled appointment date | **Write** |
| D | `Appointment Time` | Scheduled appointment time | **Write** |
| E | `Status` | "Pending", "Confirmed", "Cancelled" | **Read/Write** |
| F | `Notes` | Appointment notes | **Write** |

---

## 🔄 Google Sheets Operations

### Operation 1: Check if User Exists (READ)
- **Sheet:** `Leads`
- **Action:** Search/Lookup
- **Match Column:** `User ID` (Column A)
- **Match Value:** WhatsApp phone number
- **Purpose:** Check if returning user

### Operation 2: Add New Lead (WRITE)
- **Sheet:** `Leads`
- **Action:** Append Row / Add Row
- **Fields to write:**
  ```
  User ID: {{ $json.phone }}
  Timestamp: {{ $now.toISO() }}
  Service Type: "Truck/Trailer Driver"
  Place/Location: {{ $json.lead_data.location }}
  Full Name: {{ $json.lead_data.full_name }}
  Phone Number: {{ $json.lead_data.phone }}
  Email: {{ $json.lead_data.email }}
  Status: "New"
  Documents: ""
  Notes: ""
  Channel: "WhatsApp"
  consent_status: "Granted"
  consent_timestamp: {{ $json.consent_timestamp }}
  consent_version: "v1.0"
  consent_text: {{ $json.consent_text }}
  Platform: "WhatsApp Business API"
  ```

### Operation 3: Update Existing Lead (WRITE)
- **Sheet:** `Leads`
- **Action:** Update Row
- **Match Column:** `User ID` (Column A)
- **Match Value:** WhatsApp phone number
- **Fields to update:** Any changed fields

### Operation 4: Delete Lead - GDPR Request (DELETE)
- **Sheet:** `Leads`
- **Action:** Delete Row
- **Match Column:** `User ID` (Column A)
- **Match Value:** WhatsApp phone number

### Operation 5: Log Consent Action (WRITE)
- **Sheet:** `Consent_Log`
- **Action:** Append Row
- **Fields:**
  ```
  User ID: {{ $json.phone }}
  Timestamp: {{ $now.toISO() }}
  Action: "Granted" / "Denied" / "Deleted"
  consent_version: "v1.0"
  consent_text: {{ $json.consent_text }}
  IP/Channel: "WhatsApp"
  ```

---

## 📋 Field Mapping: Bot Data → Google Sheets

| Bot Collects | Maps To Sheet Column | Sheet |
|--------------|---------------------|-------|
| WhatsApp phone | `User ID` (A) | Leads |
| Current timestamp | `Timestamp` (B) | Leads |
| "Truck/Trailer Driver" (default) | `Service Type` (C) | Leads |
| location | `Place/Location` (D) | Leads |
| full_name | `Full Name` (E) | Leads |
| phone (user provided) | `Phone Number` (F) | Leads |
| email | `Email` (G) | Leads |
| "New" (default) | `Status` (H) | Leads |
| "" (empty) | `Documents` (I) | Leads |
| "" (empty) | `Notes` (J) | Leads |
| "WhatsApp" | `Channel` (K) | Leads |
| "Granted" | `consent_status` (L) | Leads |
| consent timestamp | `consent_timestamp` (M) | Leads |
| "v1.0" | `consent_version` (N) | Leads |
| full consent text | `consent_text` (O) | Leads |
| "WhatsApp Business API" | `Platform` (P) | Leads |

---

## 🌐 Multilingual Support

### Supported Languages & Keywords

| Language | Code | YES Keywords | NO Keywords | DELETE |
|----------|------|--------------|-------------|--------|
| English | en | YES, Y, AGREE, CONSENT | NO, N, DECLINE, STOP | DELETE |
| Polish | pl | TAK, T, ZGODA, WYRAŻAM | NIE, N, ODMAWIAĆ, ZATRZYMAĆ | USUŃ |
| German | de | JA, J, ZUSTIMMEN, EINVERSTANDEN | NEIN, N, ABLEHNEN, STOPPEN | LÖSCHEN |
| Spanish | es | SÍ, SI, ACEPTAR, CONSENTIR | NO, DETENER, PARAR | ELIMINAR |
| Ukrainian | uk | ТАК, Т, ПОГОДЖУЮСЬ, ЗГОДА | НІ, Н, ВІДМОВЛЯЮСЬ, ЗУПИНИТИ | ВИДАЛИТИ |
| Hindi | hi | YES, Y, सहमति, हाँ | NO, N, नहीं, रोकें | हटाएँ |
| Malayalam | ml | YES, Y, സമ്മതിക്കുന്നു, അതെ | NO, N, ഇല്ല, നിർത്തുക | ഇല്ലാതാക്കുക |

---

## 🔀 n8n Workflow Structure

### Node 1: WhatsApp Trigger
- Receives incoming WhatsApp messages
- Extracts: phone, message_text, message_id, timestamp

### Node 2: Check User Exists (Google Sheets - Lookup)
- **Sheet:** `Leads`
- **Operation:** Lookup / Get Many
- **Filter:** `User ID` (Column A) = WhatsApp phone number
- **Purpose:** Check if returning user, get conversation state

### Node 3: Language Detection (if new user)
- Use OpenAI or language detection API
- Store detected language_code

### Node 4: Route by Stage
- **IF new user (first message)** → Send Welcome + Consent
- **IF stage = "consent"** → Go to Consent Handler
- **IF stage = "collection"** → Go to Collection Handler

### Node 5: Send Welcome Message (for new users only)
- **Type:** WhatsApp Send Message
- **Trigger:** First message from new user
- **Message (by language):**
  ```
  English: "👋 Welcome to Dream Axis Travel Solutions! We help connect skilled drivers with truck and trailer driving opportunities across Europe. We're excited to assist you on your journey!"
  
  Polish: "👋 Witamy w Dream Axis Travel Solutions! Pomagamy łączyć wykwalifikowanych kierowców z możliwościami pracy jako kierowca ciężarówki i naczepy w całej Europie. Z przyjemnością pomożemy Ci w Twojej podróży!"
  
  German: "👋 Willkommen bei Dream Axis Travel Solutions! Wir helfen qualifizierten Fahrern, LKW- und Anhängerfahrmöglichkeiten in ganz Europa zu finden. Wir freuen uns, Sie auf Ihrem Weg zu unterstützen!"
  
  Spanish: "👋 ¡Bienvenido a Dream Axis Travel Solutions! Ayudamos a conectar conductores calificados con oportunidades de conducción de camiones y remolques en toda Europa. ¡Estamos emocionados de ayudarte en tu camino!"
  ```
- **Then:** Immediately send GDPR consent message (Node 6)

### Node 6: Send GDPR Consent Message
- **Type:** WhatsApp Send Message
- **Trigger:** After welcome message OR when user gives invalid consent response
- **Message:** GDPR consent text in user's language
- **Then:** Wait for user response

### Node 7: Consent Handler
- Check if message is YES/NO/invalid
- **IF YES**: 
  - Update state to "collection"
  - Send confirmation
  - Proceed to first question
- **IF NO**: 
  - Log to `Consent_Log` sheet (Action: "Denied")
  - Send denial confirmation
  - Clear state
- **IF invalid**: Go back to Node 6 (resend consent text)

### Node 8: Collection Handler
- Use OpenAI to extract data from user message
- Update lead_data with extracted fields
- Validate required fields
- **IF all fields collected**: Save lead, notify admin, send confirmation
- **IF fields missing**: Generate next question, send to user

### Node 9: Save to Google Sheets (Add Row)
- **Sheet:** `Leads`
- **Operation:** Append / Add Row
- **Columns to write:**
  ```
  User ID (A): {{ $json.phone }}
  Timestamp (B): {{ $now.toISO() }}
  Service Type (C): "Truck/Trailer Driver"
  Place/Location (D): {{ $json.lead_data.location }}
  Full Name (E): {{ $json.lead_data.full_name }}
  Phone Number (F): {{ $json.lead_data.phone }}
  Email (G): {{ $json.lead_data.email }}
  Status (H): "New"
  Documents (I): ""
  Notes (J): ""
  Channel (K): "WhatsApp"
  consent_status (L): "Granted"
  consent_timestamp (M): {{ $json.consent_timestamp }}
  consent_version (N): "v1.0"
  consent_text (O): {{ $json.consent_text }}
  Platform (P): "WhatsApp Business API"
  ```

### Node 10: Log Consent (Google Sheets - Add Row)
- **Sheet:** `Consent_Log`
- **Operation:** Append / Add Row
- **Columns:**
  ```
  User ID (A): {{ $json.phone }}
  Timestamp (B): {{ $now.toISO() }}
  Action (C): "Granted" / "Denied" / "Deleted"
  consent_version (D): "v1.0"
  consent_text (E): {{ $json.consent_text }}
  IP/Channel (F): "WhatsApp"
  ```

### Node 11: Send Email Notification
- Send to admin email(s)
- Include all lead details from `Leads` sheet

### Node 12: WhatsApp Send Message
- Send responses back to user
- Use user's detected language

### Node 13: Delete Lead (for DELETE requests)
- **Sheet:** `Leads`
- **Operation:** Delete Row
- **Filter:** `User ID` (Column A) = WhatsApp phone number
- **Then:** Log to `Consent_Log` with Action = "Deleted"

---

## ⏰ Reminder Workflow (Separate n8n Workflow)

### Purpose
Send reminder messages to users who haven't responded within 10 minutes to prevent lead abandonment.

### Reminder Workflow Nodes

#### Node R1: Schedule Trigger (Every 5 minutes)
- **Type:** Schedule Trigger / Cron
- **Interval:** Every 5 minutes
- **Purpose:** Check for inactive conversations

#### Node R2: Get Active Conversations (Google Sheets - Lookup)
- **Sheet:** `Leads` or separate `Active_Conversations` sheet
- **Filter:** 
  - `Status` = "In Progress" AND
  - `last_message_time` < (now - 10 minutes) AND
  - `reminder_count` < 2

#### Node R3: Loop Through Inactive Users
- **Type:** Split In Batches
- **Purpose:** Process each inactive conversation

#### Node R4: Check Reminder Count
- **IF** `reminder_count` = 0 → Send 1st reminder
- **IF** `reminder_count` = 1 → Send 2nd reminder
- **IF** `reminder_count` >= 2 → Mark as abandoned

#### Node R5: Send Reminder (WhatsApp)
- **1st Reminder (10 min):**
  ```
  Hi! Just checking in - are you still there? 
  We'd love to help you find a driving job in Europe. 😊
  ```
- **2nd Reminder (20 min):**
  ```
  We're still here whenever you're ready to continue! 
  Just reply to pick up where we left off. 🚛
  ```

#### Node R6: Update Reminder Count (Google Sheets)
- **Sheet:** `Leads` or `Active_Conversations`
- **Operation:** Update Row
- **Update:** 
  - `reminder_count` = `reminder_count` + 1
  - `last_reminder_time` = now

#### Node R7: Mark as Abandoned (if 2nd reminder sent)
- **Sheet:** `Leads`
- **Operation:** Update Row
- **Filter:** `User ID` = phone
- **Update:** `Status` = "Incomplete"
- **Optional:** Save partial data collected so far

### Reminder Messages by Language

| Language | 1st Reminder | 2nd Reminder |
|----------|--------------|--------------|
| English (en) | "Hi! Just checking in - are you still there? We'd love to help you find a driving job in Europe. 😊" | "We're still here whenever you're ready to continue! Just reply to pick up where we left off. 🚛" |
| Polish (pl) | "Cześć! Sprawdzamy tylko - czy nadal tam jesteś? Chętnie pomożemy Ci znaleźć pracę kierowcy w Europie. 😊" | "Nadal tu jesteśmy, kiedy będziesz gotowy kontynuować! Po prostu odpowiedz, aby wrócić do rozmowy. 🚛" |
| German (de) | "Hallo! Wir wollten nur nachfragen - sind Sie noch da? Wir helfen Ihnen gerne, einen Fahrerjob in Europa zu finden. 😊" | "Wir sind immer noch hier, wenn Sie bereit sind weiterzumachen! Antworten Sie einfach, um fortzufahren. 🚛" |
| Spanish (es) | "¡Hola! Solo verificamos - ¿sigues ahí? Nos encantaría ayudarte a encontrar un trabajo de conductor en Europa. 😊" | "¡Seguimos aquí cuando estés listo para continuar! Solo responde para retomar donde lo dejamos. 🚛" |

---

## ⚙️ State Management

### Conversation State Structure
```json
{
  "phone": "917736053341",
  "language_code": "en",
  "stage": "consent | collection",
  "consent_given": false,
  "consent_timestamp": null,
  "last_message_time": "2024-01-15T10:30:00Z",
  "last_question": "What is your email address?",
  "reminder_count": 0,
  "lead_data": {
    "full_name": null,
    "email": null,
    "phone": null,
    "location": null
  }
}
```

### State Transitions
```
[New User] → consent → (YES) → collection → (all fields) → [Complete]
                     → (NO)  → [End]

[Any Stage] → (DELETE) → [Delete & End]

[Collection Stage - No Response]:
  → (10 min) → 1st Reminder → (response) → Continue collection
                            → (10 min)  → 2nd Reminder → (response) → Continue
                                                       → (10 min)  → [Abandoned/Incomplete]
```

### Reminder State Updates
| Event | Update |
|-------|--------|
| User sends message | `last_message_time` = now, `reminder_count` = 0 |
| 1st reminder sent | `reminder_count` = 1 |
| 2nd reminder sent | `reminder_count` = 2 |
| No response after 2nd | `Status` = "Incomplete" |

---

## 🔐 Security & Compliance

### GDPR Requirements
1. ✅ Explicit consent before collecting data
2. ✅ Clear explanation of data usage
3. ✅ Right to deletion (DELETE command)
4. ✅ Consent tracking (timestamp, version)
5. ✅ Multilingual consent texts

### Data Security
1. ✅ Webhook signature verification
2. ✅ HTTPS for all communications
3. ✅ Secure storage in Google Sheets
4. ✅ Admin-only email notifications

---

## 📝 Sample Conversation Flow

```
USER: Hello, I'm looking for truck driving jobs in Europe

BOT:  👋 Welcome to Dream Axis Travel Solutions! We help connect skilled 
      drivers with truck and trailer driving opportunities across Europe. 
      We're excited to assist you on your journey!

BOT:  Before we continue, we need your permission to process your personal data.
      
      Dream Axis Travel Solutions will use your information only for recruitment 
      related to truck and trailer driving jobs in Europe.
      
      Your data will be stored securely and you may request deletion at any time 
      by replying DELETE.
      
      Reply YES to agree or NO to stop.

USER: YES
BOT:  Thank you for your consent. Let's proceed with collecting your information.
BOT:  What is your full name?

USER: My name is John Smith
BOT:  Thank you, John. What is your email address?

USER: john.smith@example.com
BOT:  Great! What is your phone number with country code?

USER: +48 123 456 789
BOT:  Thanks! Where are you currently located?

USER: I'm in Warsaw, Poland
BOT:  Thank you! Your information has been recorded. We'll be in touch soon.

[Lead saved to Google Sheets, Admin notified via email]
```

---

## 🚨 Error Handling

| Error | Action |
|-------|--------|
| Invalid email format | Ask user to provide valid email |
| Invalid phone format | Ask user to provide phone with country code |
| Google Sheets error | Send error message, notify admin |
| OpenAI API error | Use fallback questions, notify admin |
| WhatsApp send error | Log error, retry once |

---

## 📧 Email Notification Template

**Subject:** New Lead from WhatsApp - {full_name}

**Body:**
```
New lead received from WhatsApp Lead Bot

Name: {full_name}
Email: {email}
Phone: {phone}
Location: {location}
Language: {language_code}

Consent: {consent_status}
Consent Time: {consent_timestamp}

WhatsApp: {whatsapp_phone}
Timestamp: {timestamp}
```

---

## 🔧 Configuration Required

### Environment Variables
```bash
# WhatsApp Cloud API
WHATSAPP_API_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_APP_SECRET=your_app_secret

# OpenAI
OPENAI_API_KEY=your_openai_key

# Google Sheets
GOOGLE_SHEET_NAME=Dream Axis Leads
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ADMIN_EMAILS=admin1@company.com,admin2@company.com
```

---

## ✅ Checklist for n8n Implementation

### Main Workflow
- [ ] WhatsApp Trigger node configured with webhook URL
- [ ] Conversation state storage (Google Sheets or database)
- [ ] Language detection logic
- [ ] Consent flow with YES/NO handling
- [ ] OpenAI integration for data extraction
- [ ] Sequential question asking (one at a time)
- [ ] Field validation before proceeding
- [ ] Google Sheets "Add Row" for new leads
- [ ] Email notification to admin
- [ ] DELETE command handling at any stage
- [ ] Error handling and fallbacks
- [ ] Multilingual message support
- [ ] Track `last_message_time` for each conversation

### Reminder Workflow (Separate)
- [ ] Schedule Trigger (every 5 minutes)
- [ ] Query for inactive conversations (>10 min no response)
- [ ] Check reminder count (max 2 reminders)
- [ ] Send reminder in user's language
- [ ] Update reminder count in state
- [ ] Mark as "Incomplete" after 2nd reminder with no response
- [ ] Multilingual reminder messages configured

---

## 📌 Key Rules Summary

1. **Always** get GDPR consent before collecting any data
2. **Never** create a Google Sheets row until all data is collected
3. **Always** ask one question at a time
4. **Always** wait for user response before next question
5. **Always** use the user's detected language
6. **Always** handle DELETE requests at any stage
7. **Always** validate email and phone formats
8. **Always** notify admin via email when lead is complete
9. **Never** store data if user says NO to consent
10. **Always** include consent timestamp and version in records
11. **Always** send a reminder after 10 minutes of no response
12. **Never** send more than 2 reminders per conversation
13. **Always** reset reminder count when user responds
14. **Always** mark lead as "Incomplete" after 2 unanswered reminders

