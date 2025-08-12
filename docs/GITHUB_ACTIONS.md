# GitHub Actions Setup

This document explains the GitHub Actions workflows that have been set up to replace any Replit-linked actions and provide automated CI/CD for the Intelligent FIR System.

## Overview

The project now includes comprehensive GitHub Actions workflows that provide:

- **Automated Testing** - Run tests on every push and pull request
- **Code Quality Checks** - Linting and style enforcement
- **Security Scanning** - Automated security vulnerability checks
- **Build Verification** - Package building and artifact creation
- **Deployment Automation** - Staging and production deployments

## Workflows

### 1. Test and Lint (`test.yml`)

**Triggers:** Push to main/master/develop, Pull requests to main/master

**What it does:**
- Sets up Python 3.11 environment
- Installs dependencies from `requirements.txt`
- Runs flake8 linting for code quality
- Executes pytest test suite
- Generates coverage reports
- Uploads coverage to Codecov

**Benefits:**
- Catches code quality issues early
- Ensures tests pass before merging
- Provides code coverage metrics

### 2. Full CI/CD Pipeline (`ci-cd.yml`)

**Triggers:** Push to main/master/develop, Pull requests to main/master

**Jobs:**
1. **Test** - Multi-version Python testing (3.11, 3.12)
2. **Security** - Security vulnerability scanning
3. **Build** - Package building and artifact creation
4. **Deploy Staging** - Automatic deployment to staging environment
5. **Deploy Production** - Automatic deployment to production environment
6. **Notify** - Deployment status notifications

## Configuration Files

### `.flake8`
Configures code linting rules:
- Max line length: 127 characters
- Excludes build artifacts and cache directories
- Ignores common false positives

### `pytest.ini`
Configures test execution:
- Test discovery patterns
- Coverage reporting
- Warning filters
- Custom markers for test categorization

## Setup Instructions

### 1. Enable GitHub Actions

1. Go to your GitHub repository
2. Navigate to **Settings** → **Actions** → **General**
3. Ensure "Allow all actions and reusable workflows" is selected
4. Save the settings

### 2. Set Up Secrets (for deployment)

If you plan to use the deployment features, add these secrets in your repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `STAGING_URL` - Your staging environment URL
   - `STAGING_API_KEY` - API key for staging deployment
   - `PRODUCTION_URL` - Your production environment URL
   - `PRODUCTION_API_KEY` - API key for production deployment

### 3. Configure Environments (Optional)

For deployment workflows, you can set up environments:

1. Go to **Settings** → **Environments**
2. Create environments named `staging` and `production`
3. Add environment-specific secrets and protection rules

## Running Tests Locally

Before pushing code, you can run the same checks locally:

```bash
# Install testing dependencies
pip install pytest pytest-cov flake8

# Run linting
flake8 .

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run tests only (without coverage)
pytest tests/ -v
```

## Customization

### Adding New Tests

1. Create test files in the `tests/` directory
2. Follow the naming convention: `test_*.py`
3. Use pytest fixtures and markers as needed

### Modifying Linting Rules

Edit `.flake8` to adjust:
- Line length limits
- Ignored error codes
- Excluded directories

### Adding Deployment Steps

Modify the deployment jobs in `ci-cd.yml`:
- Replace placeholder deployment commands
- Add platform-specific deployment steps
- Configure environment variables

## Troubleshooting

### Common Issues

1. **Tests failing locally but passing in CI**
   - Check for environment-specific dependencies
   - Ensure test database is properly configured

2. **Linting errors**
   - Run `flake8 .` locally to see specific issues
   - Check `.flake8` configuration

3. **Deployment failures**
   - Verify secrets are correctly set
   - Check deployment platform credentials
   - Review deployment logs

### Getting Help

- Check the GitHub Actions tab in your repository for detailed logs
- Review the workflow files in `.github/workflows/`
- Consult the [GitHub Actions documentation](https://docs.github.com/en/actions)

## Migration from Replit

This setup replaces any Replit-linked actions with:

- **Better Integration** - Native GitHub integration
- **More Control** - Customizable workflows
- **Better Security** - GitHub's security features
- **Cost Effective** - Free for public repositories
- **Scalable** - Can handle complex CI/CD pipelines

The workflows are designed to be equivalent to or better than what Replit provided, with additional features like security scanning and comprehensive testing. 