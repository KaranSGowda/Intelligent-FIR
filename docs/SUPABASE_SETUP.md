# Setting Up Supabase Database for Intelligent FIR System

This guide will walk you through setting up a free PostgreSQL database using Supabase for the Intelligent FIR System.

## Step 1: Create a Supabase Account and Project

1. Go to [Supabase](https://supabase.com/) in your web browser
2. Sign up for a free account (you can use email or sign in with GitHub)
3. After signing in, click on "New Project"
4. Fill in the details:
   - Name: `intelligent-fir-system`
   - Database Password: Create a strong password (make sure to save this)
   - Region: Choose a region closest to your location
   - Pricing Plan: Free tier
5. Click "Create new project"

It will take a few minutes for your database to be set up. Once it's ready, you'll be taken to the project dashboard.

## Step 2: Get Your Database Connection Details

1. In your Supabase project dashboard, go to "Settings" (gear icon) in the left sidebar
2. Click on "Database" 
3. Scroll down to the "Connection string" section
4. You'll see a connection string that looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklm.supabase.co:5432/postgres
   ```
5. Make sure to replace `[YOUR-PASSWORD]` with the database password you created

## Step 3: Update Your .env File

1. Create or edit the `.env` file in your project root directory
2. Add the following content, replacing the placeholders with your actual Supabase connection details:

```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres
```

## Step 4: Install Required Dependencies

Run the following command to install the required dependencies:

```bash
pip install psycopg2-binary python-dotenv
```

## Step 5: Initialize the Database

Run the setup script to initialize your database:

```bash
python setup_online_db.py
```

This script will:
- Verify your database connection
- Create all the necessary tables
- Initialize the legal sections
- Optionally create demo users

## Step 6: Test the Connection

Run the test script to verify your database connection:

```bash
python test_db_connection.py
```

## Step 7: Run the Application

Start the application with:

```bash
python main.py
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Verify that your database password is correct in the `.env` file
2. Check if your IP address is allowed in Supabase (Settings > Database > Network)
3. Make sure you've installed the `psycopg2-binary` package

### Database Initialization Errors

If you encounter errors during database initialization:

1. Check the error message for specific issues
2. Try running the initialization commands manually:

```python
from app import create_app
app = create_app()
with app.app_context():
    from extensions import db
    db.create_all()
    from utils.legal_mapper import initialize_legal_sections
    initialize_legal_sections()
```

### SSL Issues

If you encounter SSL-related errors, you may need to modify your connection string to disable SSL:

```
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres?sslmode=require
```

## Supabase Free Tier Limitations

The Supabase free tier includes:
- 500MB database storage
- 2GB bandwidth
- Up to 50MB of file storage
- Unlimited API requests
- Up to 50,000 monthly active users
- 7-day log retention

These limits should be more than sufficient for development and small-scale usage of the Intelligent FIR System.
