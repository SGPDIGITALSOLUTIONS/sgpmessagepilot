# SGP MessagePilot - Preflight Checks

## Overview
This document contains a comprehensive list of checks to ensure SGP MessagePilot is functioning correctly. Use this checklist whenever making changes or troubleshooting issues.

---

## 🔧 **Critical Code Integrity Checks**

### 1. **Tuple Unpacking Validation** ⚠️ *Recently Fixed*
**Issue:** "not enough values to unpack (expected 2, got 1)" error
**Root Cause:** Variable scope issues with `warnings` in `process_uploaded_file()`

**Checks:**
- [ ] Verify `warnings = []` is initialized at function scope in `process_uploaded_file()`
- [ ] Confirm all return statements in `process_uploaded_file()` return proper tuples `(dict, status_code)`
- [ ] Validate `validate_file_content()` returns `(errors, warnings)` tuple
- [ ] Check upload route properly unpacks: `response, status_code = result`

**Search Commands:**
```bash
# Check for tuple unpacking patterns
grep -n ".*,.*=.*" app/app.py
# Verify return statements return tuples
grep -n "return.*," app/app.py
```

### 2. **Function Return Consistency**
**Checks:**
- [ ] All backend functions return consistent data types
- [ ] Error paths return proper HTTP status codes
- [ ] Success paths include all required fields
- [ ] No functions return `None` unexpectedly

### 3. **Variable Scope Issues**
**Checks:**
- [ ] Variables used across exception blocks are properly scoped
- [ ] No undefined variable references in error handlers
- [ ] Loop variables don't leak outside intended scope

---

## 🗂️ **File Structure & Dependencies**

### 4. **Required Files Exist**
**Checks:**
- [ ] `app/app.py` - Main application
- [ ] `app/templates/index.html` - Frontend template
- [ ] `app/templates/privacy.html` - Privacy policy
- [ ] `app/templates/terms.html` - Terms of service
- [ ] `requirements.txt` - Python dependencies
- [ ] `README.md` - Documentation
- [ ] `ROADMAP.md` - Development roadmap

### 5. **Directory Structure**
**Checks:**
- [ ] `app/uploads/` exists for temporary file storage
- [ ] `app/logs/` exists for application logging
- [ ] `data/source/` exists for source data
- [ ] Proper permissions on upload directories

### 6. **Dependencies**
**Verify Required Packages:**
- [ ] `Flask==3.0.0`
- [ ] `pandas==2.1.4`
- [ ] `openpyxl==3.1.2`
- [ ] `python-dotenv==1.0.0`
- [ ] `Werkzeug==3.0.1`

**Check Command:**
```bash
pip list | grep -E "(Flask|pandas|openpyxl|python-dotenv|Werkzeug)"
```

---

## 🛡️ **GDPR Compliance & Privacy**

### 7. **Platform Consent Management** ⚠️ *GDPR Critical*
**Purpose:** Ensure platform-specific consent is properly collected and managed

**Consent Collection Checks:**
- [ ] Home page displays platform selection with clear consent requirements
- [ ] WhatsApp consent modal requires 3 specific consents:
  - [ ] Data processing consent for WhatsApp messaging
  - [ ] WhatsApp Terms of Service compliance confirmation  
  - [ ] Privacy Policy agreement
- [ ] All consent checkboxes must be checked before proceeding
- [ ] Consent modal cannot be bypassed or closed without agreement
- [ ] Consent data includes timestamp and user agent for audit trail

**Consent Storage & Validation:**
- [ ] Consent stored in localStorage with structured data format
- [ ] Consent includes platform identifier (`platform-consent-whatsapp`)
- [ ] Consent expires after 24 hours for security
- [ ] WhatsApp page validates consent before allowing access
- [ ] Expired/missing consent redirects to home page
- [ ] No access to protected functionality without valid consent

**Search Commands:**
```bash
# Check consent modal implementation
grep -n "consent-" app/templates/index.html
grep -n "platform-consent" app/templates/whatsapp.html

# Verify consent validation
grep -n "checkPlatformConsent" app/templates/whatsapp.html
```

### 8. **Data Processing Transparency** ⚠️ *GDPR Article 13/14*
**Purpose:** Ensure users are fully informed about data processing

**Privacy Information Checks:**
- [ ] Clear explanation of WhatsApp-specific privacy measures
- [ ] Clipboard method described (messages copied, only phone shared)
- [ ] URL data exposure prevented (no PII in browser history)
- [ ] Message preview functionality explained
- [ ] No persistent storage policy stated
- [ ] Privacy policy easily accessible from all consent points

**Privacy Method Implementation:**
- [ ] Privacy-preserving methods active by default
- [ ] No direct URL method available (removed for privacy)
- [ ] Auto-detection prioritizes privacy-first approaches
- [ ] Clipboard method prevents data exposure in URLs
- [ ] Manual copy modal available as fallback

### 9. **Data Minimization & Purpose Limitation** ⚠️ *GDPR Article 5*
**Purpose:** Ensure minimal data processing for legitimate purposes only

**Data Processing Scope:**
- [ ] Only necessary contact data processed (names, phones, locations)
- [ ] Processing limited to WhatsApp message generation purpose
- [ ] No data stored permanently on server
- [ ] No unnecessary data collected or retained
- [ ] Data processed in memory only, deleted after use

**Purpose Limitation Checks:**
- [ ] Data used only for stated WhatsApp messaging purpose
- [ ] No secondary use of contact data
- [ ] No data sharing with third parties
- [ ] No profiling or automated decision making
- [ ] Clear purpose statement in consent and privacy policy

### 10. **Data Subject Rights Implementation** ⚠️ *GDPR Articles 15-22*
**Purpose:** Ensure all GDPR rights are supported and documented

**Rights Documentation:**
- [ ] Right to access (Article 15) - How users can request data
- [ ] Right to rectification (Article 16) - How to correct data
- [ ] Right to erasure (Article 17) - Data deletion procedures
- [ ] Right to restrict processing (Article 18) - Processing limitations
- [ ] Right to data portability (Article 20) - Data export options
- [ ] Right to object (Article 21) - Opt-out mechanisms
- [ ] Rights related to automated decision making (Article 22)

**Contact Information:**
- [ ] Data Protection Officer (DPO) contact details provided
- [ ] Clear complaint procedure to supervisory authority (ICO)
- [ ] Response timeframes documented (1 month standard)
- [ ] Identity verification procedures for rights requests

### 11. **Legal Basis & Compliance Documentation** ⚠️ *GDPR Article 6*
**Purpose:** Ensure valid legal basis for all data processing

**Legal Basis Validation:**
- [ ] Consent (Article 6(1)(a)) - Platform-specific consents active
- [ ] Legitimate Interest (Article 6(1)(f)) - Business operations documented
- [ ] Contract Performance (Article 6(1)(b)) - Service delivery basis
- [ ] Legal basis clearly communicated to users
- [ ] Withdrawal of consent mechanisms available

**Compliance Indicators:**
- [ ] "FULLY GDPR COMPLIANT" status displayed prominently
- [ ] Compliance score shows 100% across all areas
- [ ] GDPR compliance badges visible on all pages
- [ ] Privacy policy includes comprehensive GDPR section
- [ ] Terms of service align with GDPR requirements

### 12. **Privacy by Design Implementation** ⚠️ *GDPR Article 25*
**Purpose:** Verify privacy-first technical architecture

**Technical Privacy Measures:**
- [ ] Privacy-preserving WhatsApp integration methods
- [ ] No PII exposure in URLs or browser history
- [ ] Clipboard-based messaging to minimize data sharing
- [ ] Auto-detection prioritizes most private methods
- [ ] HTTPS enforced for clipboard API security
- [ ] Client-side data processing where possible

**Privacy Impact Assessment:**
- [ ] Risk assessment completed for data processing activities
- [ ] Privacy risks identified and mitigated
- [ ] Regular review schedule for privacy measures
- [ ] Documentation of privacy design decisions

### 13. **Consent Banner & Cookie Compliance**
**Purpose:** Ensure proper consent management for all tracking

**GDPR Consent Banner:**
- [ ] ~~GDPR banner removed from WhatsApp page~~ ✅ (Replaced by platform consent)
- [ ] Platform-specific consent replaces generic GDPR banner
- [ ] No unnecessary cookie consent (if no tracking cookies used)
- [ ] LocalStorage usage disclosed in privacy policy
- [ ] No consent fatigue - single comprehensive consent flow

### 14. **Data Breach Procedures** ⚠️ *GDPR Article 33/34*
**Purpose:** Ensure proper breach notification procedures

**Breach Response Checks:**
- [ ] 72-hour notification procedure to supervisory authority
- [ ] Data subject notification procedures for high-risk breaches
- [ ] Breach logging and documentation procedures
- [ ] Impact assessment procedures for breaches
- [ ] Contact information for reporting breaches

**Prevention Measures:**
- [ ] No persistent data storage reduces breach risk
- [ ] Secure data transmission (HTTPS)
- [ ] Input validation prevents data corruption
- [ ] Error handling prevents data exposure in logs
- [ ] Phone number masking in logs and debug output

### 15. **Cross-Border Data Transfer Compliance**
**Purpose:** Ensure GDPR compliance for international data transfers

**Transfer Safeguards:**
- [ ] No international data transfers (UK-based processing)
- [ ] Or: Adequate safeguards documented for any transfers
- [ ] Standard Contractual Clauses if applicable
- [ ] Data localization requirements met
- [ ] Third-party processor agreements in place

**Testing Commands:**
```bash
# Check privacy policy content
grep -n -i "gdpr\|data protection\|privacy" app/templates/privacy.html

# Verify consent implementation
grep -n "consent" app/templates/index.html app/templates/whatsapp.html

# Check for data minimization
grep -n "localStorage\|sessionStorage" app/templates/*.html

# Verify no permanent storage
grep -n "database\|persistent\|store" app/app.py
```

---

## 🔒 **Security & Configuration**

### 16. **Security Headers**
**Checks:**
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] Content Security Policy configured
- [ ] Cache control headers set

### 17. **File Upload Security**
**Checks:**
- [ ] File type validation (only .xlsx, .xls, .csv)
- [ ] File size limits enforced (16MB max)
- [ ] Secure filename handling with `secure_filename()`
- [ ] Temporary files properly cleaned up
- [ ] No path traversal vulnerabilities

### 18. **Data Privacy**
**Checks:**
- [ ] Phone numbers masked in logs
- [ ] PII filtering active in logging
- [ ] No sensitive data in debug output
- [ ] Proper data sanitization

---

## 🎯 **Functionality Checks**

### 19. **File Processing Pipeline**
**Core Functions:**
- [ ] `process_uploaded_file()` - Main processing logic
- [ ] `clean_dataframe()` - Data cleaning
- [ ] `validate_file_content()` - Data validation
- [ ] `process_phone_number()` - Phone formatting
- [ ] `create_message()` - Message generation

**Validation Steps:**
- [ ] Excel/CSV files read correctly
- [ ] Required columns present
- [ ] Phone number validation working
- [ ] UK phone formatting applied
- [ ] Empty/invalid data handled gracefully

### 19a. **Whitespace & Empty Cell Handling + NaN/JSON Safety** ⚠️ *Critical Data Integrity*
**Purpose:** Ensure robust handling of various empty/whitespace scenarios and prevent JSON serialization errors

**Data Cleaning Checks:**
- [ ] `clean_dataframe()` function properly strips whitespace from string columns
- [ ] Empty strings (`''`) converted to `pd.NA`
- [ ] Whitespace-only strings (spaces, tabs) converted to `pd.NA`
- [ ] Various null representations handled: `'nan'`, `'none'`, `'null'`, `'N/A'`, `'NA'`
- [ ] Phone number cleaning removes non-numeric characters
- [ ] Empty phone numbers properly converted to `pd.NA`

**NaN/JSON Safety Checks:** ⚠️ *Recently Fixed*
- [ ] `safe_get_value()` helper function exists and handles pandas NaN values
- [ ] All result object creation uses `safe_get_value()` instead of direct `row.get()`
- [ ] No pandas `NaN` values reach JSON serialization
- [ ] Default values provided for all missing/NaN fields
- [ ] Message generation safely handles NaN values

**Validation Steps:**
- [ ] Test file with leading/trailing spaces in names
- [ ] Test file with empty cells in required columns
- [ ] Test file with whitespace-only cells
- [ ] Test file with various null representations
- [ ] Test file with mixed empty/valid phone formats
- [ ] Test file upload produces valid JSON response (no "Unexpected token 'N'" errors)
- [ ] Test contacts with NaN location values
- [ ] Test message generation with missing data fields

**Search Commands:**
```bash
# Check whitespace handling implementation
grep -n "strip()" app/app.py
grep -n "replace.*pd.NA" app/app.py
grep -n "^\s*$" app/app.py

# Verify phone number cleaning
grep -n "filter.*str.isdigit" app/app.py

# Check NaN/JSON safety implementation
grep -n "safe_get_value" app/app.py
grep -n "pd.isna" app/app.py

# Verify result creation uses safe methods
grep -n "result = {" app/app.py -A 10
```

**Test Data Scenarios:**
```
# Example problematic data patterns to test:
- "  John  " (spaces around name)
- "" (empty string)
- "   " (whitespace only)
- "N/A" / "NA" / "null" / "none"
- "07123 456 789" (phone with spaces)
- "+44(0)7123-456-789" (phone with formatting)
- Cells with pandas NaN values (from Excel import)
- Mixed data types in same column
```

**Expected Behavior:**
- [ ] Whitespace stripped from all string fields
- [ ] Empty/whitespace cells show as "N/A" or skipped appropriately
- [ ] Phone numbers cleaned to digits only
- [ ] Contacts with no valid phone numbers excluded gracefully
- [ ] Warning messages generated for problematic data
- [ ] **JSON responses always valid (no NaN values)**
- [ ] **Frontend receives clean, consistent data types**
- [ ] **No "Unexpected token" JSON parsing errors**

### 20. **Error Handling**
**Backend Checks:**
- [ ] File not found errors
- [ ] Invalid file format errors
- [ ] Empty file errors
- [ ] Parser errors for corrupted files
- [ ] Memory errors for large files

**Frontend Checks:**
- [ ] Network errors handled
- [ ] Server error responses processed
- [ ] User-friendly error messages
- [ ] Error dismissal functionality

### 21. **Frontend-Backend Integration**
**Checks:**
- [ ] File upload AJAX working
- [ ] Response structure validation
- [ ] Contact list rendering
- [ ] Message template system
- [ ] WhatsApp link generation
- [ ] Warning display functionality

### 21a. **Merge Fields UI/UX Validation** ⚠️ *User Experience Critical*
**Purpose:** Ensure merge fields are properly displayed and functional for user interaction

**Merge Fields Display Checks:**
- [ ] Merge fields container renders after successful file upload
- [ ] All expected merge fields appear: `{first_name}`, `{last_name}`, `{full_name}`, `{location}`, `{engagement_date}`, `{volunteer_url}`
- [ ] Merge fields are clickable and styled correctly
- [ ] Tooltips/descriptions show on hover (if implemented)
- [ ] Merge fields section is visible and accessible

**Merge Fields Functionality Checks:**
- [ ] Clicking merge field inserts it into message textarea at cursor position
- [ ] Multiple merge fields can be inserted
- [ ] Merge fields work with existing text in message box
- [ ] Cursor position maintained after insertion
- [ ] No JavaScript errors in browser console when using merge fields

**Backend Integration Checks:**
- [ ] `merge_fields` array properly returned from `/upload` endpoint
- [ ] Frontend receives and processes merge fields data correctly
- [ ] `renderMergeFields()` function executes without errors
- [ ] Merge fields data structure matches frontend expectations

**Manual Testing Steps:**
1. [ ] Upload a valid file with contacts
2. [ ] Verify merge fields container appears below "Available Merge Fields" heading
3. [ ] Click each merge field and verify it appears in message textarea
4. [ ] Type custom text and insert merge fields to test cursor positioning
5. [ ] Check browser developer console for JavaScript errors

**Search Commands:**
```bash
# Check merge fields backend implementation
grep -n "merge_fields" app/app.py
grep -n "renderMergeFields" app/templates/index.html

# Verify merge fields structure
grep -n "field.*description" app/app.py -A 2 -B 2

# Check frontend rendering
grep -n "merge-fields" app/templates/index.html -A 5 -B 5
```

**Expected Merge Fields:**
```javascript
[
  {field: '{first_name}', description: "Contact's first name"},
  {field: '{last_name}', description: "Contact's last name"}, 
  {field: '{full_name}', description: "Contact's full name"},
  {field: '{location}', description: "Contact's location"},
  {field: '{engagement_date}', description: "Last engagement date"},
  {field: '{volunteer_url}', description: "Volunteering site URL"}
]
```

**Common Issues to Check:**
- [ ] Merge fields not appearing (JavaScript error or data not received)
- [ ] Merge fields not clickable (CSS/event handler issues)
- [ ] Merge fields not inserting (insertMergeField function broken)
- [ ] Merge fields container not visible (CSS display issues)

---

## 🚀 **Performance & Scalability**

### 22. **File Processing Performance**
**Checks:**
- [ ] Large file handling (test with 1000+ contacts)
- [ ] Memory usage reasonable
- [ ] Processing time acceptable
- [ ] Progress indication for long operations

### 23. **Logging & Debugging**
**Checks:**
- [ ] Debug logging comprehensive
- [ ] Log rotation configured
- [ ] Error tracking detailed
- [ ] Performance metrics logged

---

## 🧪 **Testing Scenarios**

### 24. **File Upload Tests**
**Test Cases:**
- [ ] Valid Excel file with all columns
- [ ] Valid CSV file with mixed data
- [ ] File with missing required columns
- [ ] Empty file
- [ ] Corrupted file
- [ ] Oversized file (>16MB)
- [ ] File with special characters in names
- [ ] File with invalid phone numbers

### 25. **Edge Cases**
**Scenarios:**
- [ ] All contacts have missing phone numbers
- [ ] Mixed valid/invalid phone formats
- [ ] Unicode characters in names
- [ ] Very long text in fields
- [ ] Duplicate contacts
- [ ] Empty rows in spreadsheet

### 26. **Browser Compatibility**
**Test In:**
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if on Mac)
- [ ] Edge
- [ ] Mobile browsers

---

## 🛠️ **Quick Diagnostic Commands**

### Server Status
```bash
# Check if server is running
netstat -an | findstr :5000

# Check Python processes
tasklist | findstr python.exe
```

### Code Quality
```bash
# Search for tuple unpacking
grep -n ", .* =" app/app.py

# Check return statements
grep -n "return" app/app.py

# Find exception handling
grep -n "except" app/app.py
```

### File Structure
```bash
# Verify directory structure
ls -la app/
ls -la app/templates/
ls -la app/logs/
```

### Log Analysis
```bash
# Check recent errors
tail -50 app/logs/app.log | grep -i error

# Monitor real-time logs
tail -f app/logs/debug.log
```

---

## 🚨 **Recent Fixes Applied**

### **NaN/JSON Serialization Fix (Latest)**
**Date:** June 5, 2025  
**Issue:** `Unexpected token 'N', ..."ocation": NaN, "... is not valid JSON`  
**Solution:** 
- Added `safe_get_value()` helper function to handle pandas NaN values
- Updated all result creation to use safe value extraction
- Enhanced message generation with NaN-safe value handling
- Ensured all JSON responses are valid (no NaN values)

**Files Modified:**
- `app/app.py` - Added `safe_get_value()` function and updated data processing

**Validation:**
- [x] All pandas NaN values converted to JSON-safe defaults
- [x] Result objects use safe value extraction
- [x] JSON responses always valid
- [x] Frontend receives clean, consistent data
- [x] No "Unexpected token" errors

### **Tuple Unpacking Fix**
**Date:** June 5, 2025  
**Issue:** `ValueError: not enough values to unpack (expected 2, got 1)`  
**Solution:** 
- Initialized `warnings = []` at function scope in `process_uploaded_file()`
- Renamed validation warnings to avoid variable collision
- Added comprehensive debugging for function returns
- Enhanced error logging with execution path tracking

**Files Modified:**
- `app/app.py` - Main application logic
- `app/templates/index.html` - Added missing `dismissError()` function

**Validation:**
- [x] All tuple unpacking now properly handled
- [x] Function returns consistent tuples
- [x] Variable scope issues resolved
- [x] Enhanced debugging active

---

## ✅ **Preflight Checklist Summary**

Before deploying or troubleshooting:

1. **Code Integrity** - All functions return expected data types
2. **Dependencies** - All required packages installed
3. **Security** - Headers and validation active
4. **File Structure** - All directories and files present
5. **Error Handling** - Comprehensive error catching
6. **Logging** - Debug information available
7. **Testing** - Core functionality verified
8. **Performance** - Acceptable response times

**Status:** ✅ **READY FOR OPERATION**

---

*Last Updated: June 5, 2025*  
*Version: 1.1 - Post NaN/JSON Fix + Tuple Unpacking Fix* 