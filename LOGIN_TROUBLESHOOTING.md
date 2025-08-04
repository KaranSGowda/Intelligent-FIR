# Login and Registration Troubleshooting Guide

## Quick Fixes

### 1. Clear Browser Cache and Cookies
- Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- Clear browsing data including cookies and cache
- Restart your browser

### 2. Try Different Browser
- Test with Chrome, Firefox, Edge, or Safari
- Some browsers may have compatibility issues

### 3. Check URL
- Make sure you're using: `http://localhost:5000`
- Don't use `https://` unless specifically configured

## Demo Credentials

Use these credentials to test the system:

### Public User
- **Username:** `user`
- **Password:** `password`

### Police Officer
- **Username:** `police`
- **Password:** `password`

### Administrator
- **Username:** `admin`
- **Password:** `password`

## Common Issues and Solutions

### Issue 1: "Incorrect username or password" error
**Solution:**
1. Make sure you're using the exact credentials above
2. Check that caps lock is off
3. Try copying and pasting the credentials

### Issue 2: Page not loading or connection errors
**Solution:**
1. Make sure the application is running: `python app.py`
2. Check that port 5000 is not blocked by firewall
3. Try accessing `http://127.0.0.1:5000` instead of `localhost`

### Issue 3: Form not submitting
**Solution:**
1. Check browser console for JavaScript errors (F12 → Console)
2. Disable browser extensions that might interfere
3. Try disabling JavaScript temporarily

### Issue 4: Registration not working
**Solution:**
1. Make sure all required fields are filled
2. Password must be at least 6 characters
3. Email must be in valid format (e.g., `test@example.com`)
4. Username must be unique

## Technical Debugging

### Check Application Status
```bash
python scripts/check_app_status.py
```

### Check Database
```bash
python scripts/check_db.py
```

### Reset Database (if needed)
```bash
python scripts/setup_sqlite_db.py
```

### Check Application Logs
Look for error messages in the terminal where you ran `python app.py`

## Browser Console Debugging

1. Open browser developer tools (F12)
2. Go to Console tab
3. Try to login and look for any error messages
4. Common errors to look for:
   - JavaScript errors
   - Network errors (404, 500, etc.)
   - CORS errors

## Network Issues

### Check if application is running
```bash
curl http://localhost:5000
```

### Check specific endpoints
```bash
curl http://localhost:5000/login
curl http://localhost:5000/register
```

## Session Issues

If you're getting logged out immediately or sessions aren't persisting:

1. Check that the secret key is set properly
2. Clear browser cookies and try again
3. Try a different browser
4. Check if you have multiple tabs open with different sessions

## Still Having Issues?

If none of the above solutions work:

1. **Check the application logs** in the terminal where you ran `python app.py`
2. **Try the test script**: `python test_login_functionality.py`
3. **Reset the database**: `python scripts/setup_sqlite_db.py`
4. **Restart the application**: Stop the current process and run `python app.py` again

## Contact Support

If you continue to have issues, please provide:
1. Your operating system
2. Browser and version
3. Error messages from browser console
4. Application logs from terminal
5. Steps to reproduce the issue 