# Factory ERP Deployment Guide

This guide provides step-by-step instructions for deploying the Factory ERP system to production.

## Prerequisites

- GitHub account
- Supabase account
- Vercel account
- Basic understanding of environment variables

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create a new organization (if needed)
4. Click "New Project"
5. Fill in project details:
   - Name: `factory-erp`
   - Database Password: Generate a strong password
   - Region: Choose closest to your users
6. Click "Create new project"
7. Wait for project initialization (2-3 minutes)

### 1.2 Configure Database

1. In your Supabase dashboard, go to "SQL Editor"
2. Click "New query"
3. Copy and paste the entire contents of `init_db.sql`
4. Click "Run" to execute the script
5. Verify tables are created in "Table Editor"

### 1.3 Set Up Authentication

1. Go to "Authentication" > "Settings"
2. Configure email settings (optional for testing)
3. Go to "Authentication" > "Users"
4. Click "Add user" and create test accounts:
   - Email: `admin@factory.com`
   - Password: `pass123`
   - User Metadata: `{"role": "admin", "section_id": null}`
   
   - Email: `staff1@factory.com`
   - Password: `pass123`
   - User Metadata: `{"role": "staff", "section_id": 1}`
   
   - Email: `staff2@factory.com`
   - Password: `pass123`
   - User Metadata: `{"role": "staff", "section_id": 2}`

### 1.4 Get API Keys

1. Go to "Settings" > "API"
2. Copy the following values:
   - Project URL
   - Project API keys > anon public

## Step 2: GitHub Setup

### 2.1 Create Repository

1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name: `factory-erp`
4. Make it public or private
5. Don't initialize with README (we have our own)
6. Click "Create repository"

### 2.2 Upload Code

```bash
# In your local factory_erp directory
git init
git add .
git commit -m "Initial commit: Factory ERP system"
git branch -M main
git remote add origin https://github.com/yourusername/factory-erp.git
git push -u origin main
```

## Step 3: Vercel Deployment

### 3.1 Connect Repository

1. Go to [vercel.com](https://vercel.com)
2. Sign up/login with GitHub
3. Click "New Project"
4. Import your `factory-erp` repository
5. Configure project:
   - Framework Preset: "Other"
   - Root Directory: `./` (default)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

### 3.2 Set Environment Variables

In Vercel project settings, add these environment variables:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SECRET_KEY=your-random-secret-key-here
```

To generate a secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### 3.3 Deploy

1. Click "Deploy"
2. Wait for deployment (2-3 minutes)
3. Get your deployment URL: `https://factory-erp-xxx.vercel.app`

## Step 4: Testing Deployment

### 4.1 Basic Functionality Test

1. Visit your Vercel URL
2. Should redirect to login page
3. Try logging in with test accounts
4. Verify role-based redirects work

### 4.2 Staff Dashboard Test

1. Login as `staff1@factory.com`
2. Fill out production form
3. Submit and verify success message
4. Try attendance and downtime forms

### 4.3 Admin Dashboard Test

1. Login as `admin@factory.com`
2. Check summary cards show data
3. Verify charts load (may be empty initially)
4. Check requisition approval functionality

## Step 5: Production Configuration

### 5.1 Custom Domain (Optional)

1. In Vercel project settings, go to "Domains"
2. Add your custom domain
3. Configure DNS records as instructed
4. Wait for SSL certificate provisioning

### 5.2 Environment Optimization

For production, consider:
- Using Supabase Pro for better performance
- Setting up proper email templates in Supabase Auth
- Configuring Row Level Security (RLS) policies
- Setting up monitoring and alerts

### 5.3 User Management

1. Remove test accounts or change passwords
2. Create real user accounts
3. Set up proper user metadata for roles and sections
4. Configure email confirmation if needed

## Step 6: Maintenance

### 6.1 Updates

To update the application:
1. Make changes locally
2. Test with `python test_local.py`
3. Commit and push to GitHub
4. Vercel will auto-deploy

### 6.2 Database Backups

1. In Supabase dashboard, go to "Settings" > "Database"
2. Enable automatic backups
3. Consider setting up additional backup strategies

### 6.3 Monitoring

Monitor your application:
- Vercel Analytics for performance
- Supabase Dashboard for database metrics
- Error tracking in Vercel Functions logs

## Troubleshooting

### Common Deployment Issues

1. **Build Failures**
   - Check Python version in `runtime.txt`
   - Verify all dependencies in `requirements.txt`
   - Check Vercel build logs

2. **Database Connection Issues**
   - Verify environment variables are set correctly
   - Check Supabase project is active
   - Ensure database tables exist

3. **Authentication Problems**
   - Verify Supabase Auth is enabled
   - Check user metadata format
   - Ensure JWT configuration is correct

4. **CORS Issues**
   - Verify Flask-CORS is installed
   - Check CORS configuration in app.py

### Performance Optimization

1. **Database Optimization**
   - Add indexes for frequently queried columns
   - Use connection pooling if needed
   - Monitor query performance

2. **Frontend Optimization**
   - Minify CSS/JS files
   - Optimize images
   - Use CDN for static assets

3. **Vercel Optimization**
   - Monitor function execution time
   - Optimize cold start performance
   - Use appropriate regions

## Security Checklist

- [ ] Environment variables are set securely
- [ ] Test accounts have strong passwords
- [ ] Supabase RLS policies are configured
- [ ] HTTPS is enabled (automatic with Vercel)
- [ ] Input validation is working
- [ ] Authentication is properly implemented
- [ ] Admin access is restricted

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Review Supabase logs
3. Test locally first
4. Check environment variables
5. Verify database schema

---

**Congratulations! Your Factory ERP system is now deployed and ready for production use.**

