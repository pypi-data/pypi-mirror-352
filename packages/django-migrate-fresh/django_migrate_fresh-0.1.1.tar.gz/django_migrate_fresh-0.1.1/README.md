# Django Migrate Fresh

A Django package that provides Laravel-style `migrate:fresh` functionality. This command drops all tables and re-runs all migrations, similar to Laravel's `php artisan migrate:fresh`.

## Installation

```bash
pip install django_migrate_fresh
```

## Usage

Add `django_migrate_fresh` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your apps
    'django_migrate_fresh',
]
```

Run the command:

```bash
python manage.py migrate_fresh
```

### Options

- `--force`: ⚡ Skip confirmation prompt
- `--seed`: 🌱 Run seeders after migration (requires custom seed command)
- `--no-superuser`: 👤 Skip creating default superuser
- `--backup`: 💾 Create database backup before operation
- `--backup-path PATH`: 📁 Custom path for database backup
- `--dry-run`: 🔍 Show what would be done without executing
- `--verbose`: 📝 Show detailed progress information
- `--stats`: 📊 Show performance statistics

### Examples

```bash
# Basic usage with confirmation
python manage.py migrate_fresh

# Force without confirmation
python manage.py migrate_fresh --force

# Create backup and run with seeders
python manage.py migrate_fresh --backup --seed

# Preview what will happen
python manage.py migrate_fresh --dry-run

# Verbose output with performance stats
python manage.py migrate_fresh --verbose --stats --force

# Custom backup location
python manage.py migrate_fresh --backup --backup-path="/path/to/backup.sql"
```

### Environment Variables

- `DJANGO_SUPERUSER_USERNAME`: Default superuser username (default: "admin")
- `DJANGO_SUPERUSER_EMAIL`: Default superuser email (default: "admin@example.com")
- `DJANGO_SUPERUSER_PASSWORD`: Default superuser password (default: "admin123")

## Features

### 🎨 Beautiful Interface

- Cool ASCII art header
- Progress bars and step tracking
- Emoji indicators for different operations
- Colored output for better readability

### 🛡️ Safety Features

- Production environment detection
- Confirmation prompts with detailed warnings
- Database backup option
- Dry run mode to preview changes
- Comprehensive error handling

### 📊 Advanced Monitoring

- Performance timing for each step
- Detailed statistics and summaries
- Verbose mode for debugging
- Step-by-step progress tracking

### 🗄️ Database Support

- PostgreSQL with CASCADE support
- MySQL with foreign key handling
- SQLite compatibility
- Automatic vendor detection

## Warning

⚠️ **This command will DROP ALL TABLES and destroy all data!** Use with caution, especially in production environments.

The command includes built-in protection:

- Detects production environments (when `DEBUG=False`)
- Requires explicit confirmation
- Offers backup creation
- Provides dry-run preview

## Supported Databases

- PostgreSQL
- MySQL
- SQLite

## Documentation

For more detailed documentation, examples, and advanced usage, visit the GitHub repository:

🔗 **https://github.com/sepehr-mohseni/django_migrate_fresh**

## License

MIT License
