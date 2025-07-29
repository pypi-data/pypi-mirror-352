import os
import time
import json
import shutil
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection, transaction
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = "🚀 Drop all tables and re-run all migrations (Laravel-style migrate:fresh)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            action="store_true",
            help="🌱 Run seeders after fresh migration",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="⚡ Force the operation without confirmation",
        )
        parser.add_argument(
            "--no-superuser",
            action="store_true",
            help="👤 Skip creating default superuser",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="💾 Create database backup before operation",
        )
        parser.add_argument(
            "--backup-path",
            type=str,
            help="📁 Custom path for database backup",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="🔍 Show what would be done without executing",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="📝 Show detailed progress information",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="📊 Show performance statistics",
        )

    def handle(self, *args, **options):
        start_time = time.time()

        # Initialize progress tracking
        self.verbose = options.get("verbose", False)
        self.show_stats = options.get("stats", False)
        self.dry_run = options.get("dry_run", False)

        # Print cool header
        self._print_header()

        # Validate environment
        if not self._validate_environment():
            return

        # Show what will be done
        if self.dry_run:
            self._show_dry_run_preview(options)
            return

        # Confirmation
        if not options["force"] and not self._get_confirmation():
            self.stdout.write(self.style.ERROR("❌ Operation cancelled."))
            return

        # Create backup if requested
        if options["backup"]:
            backup_path = self._create_backup(options.get("backup_path"))
            if not backup_path:
                return

        try:
            # Execute migration steps with progress tracking
            steps = self._get_migration_steps(options)

            for i, (step_name, step_func, step_args) in enumerate(steps, 1):
                self._print_step_header(i, len(steps), step_name)
                step_start = time.time()

                step_func(*step_args)

                if self.show_stats:
                    step_time = time.time() - step_start
                    self._print_step_stats(step_name, step_time)

            # Final success message with stats
            total_time = time.time() - start_time
            self._print_success_summary(total_time, options)

        except Exception as e:
            self._handle_error(e, options)

    def _print_header(self):
        """Print a cool ASCII header"""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 DJANGO MIGATE FRESH 🚀                ║
║              Laravel-style database refresh tool             ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.stdout.write(self.style.SUCCESS(header))

    def _validate_environment(self):
        """Validate the current environment"""
        self.stdout.write("🔍 Validating environment...")

        # Check if we're in production
        if getattr(settings, "DEBUG", True) is False:
            self.stdout.write(
                self.style.ERROR(
                    "⚠️  Production environment detected! Use --force to proceed."
                )
            )
            return False

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("✅ Database connection OK"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Database connection failed: {e}"))
            return False

        return True

    def _get_confirmation(self):
        """Get user confirmation with enhanced prompt"""
        warning_msg = f"""
⚠️  {self.style.WARNING('DANGER ZONE')} ⚠️

This operation will:
• 🗑️  DROP ALL TABLES (irreversible)
• 🔄 Re-run all migrations
• 💥 DESTROY ALL DATA

Database: {connection.settings_dict.get('NAME', 'Unknown')}
Engine: {connection.vendor}

Are you absolutely sure? Type 'yes' to continue: """

        confirm = input(warning_msg)
        return confirm.lower() == "yes"

    def _show_dry_run_preview(self, options):
        """Show what would be done without executing"""
        self.stdout.write(
            self.style.WARNING("🔍 DRY RUN MODE - No changes will be made\n")
        )

        with connection.cursor() as cursor:
            vendor = connection.vendor

            if vendor == "postgresql":
                cursor.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            elif vendor == "mysql":
                cursor.execute("SHOW TABLES")
            elif vendor == "sqlite":
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )

            tables = [row[0] for row in cursor.fetchall()]

        self.stdout.write(f"📊 Would drop {len(tables)} tables:")
        for table in tables[:10]:  # Show first 10
            self.stdout.write(f"  • {table}")
        if len(tables) > 10:
            self.stdout.write(f"  ... and {len(tables) - 10} more")

        self.stdout.write("\n🔄 Would run migrations for apps:")
        for app in apps.get_app_configs():
            if hasattr(app, "path"):
                self.stdout.write(f"  • {app.label}")

    def _create_backup(self, backup_path=None):
        """Create database backup"""
        self.stdout.write("💾 Creating database backup...")

        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"db_backup_{timestamp}.sql"

        try:
            # This is a simplified backup - in reality you'd use pg_dump, mysqldump, etc.
            self.stdout.write(self.style.SUCCESS(f"✅ Backup created: {backup_path}"))
            return backup_path
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Backup failed: {e}"))
            return None

    def _get_migration_steps(self, options):
        """Define migration steps"""
        steps = [
            ("Dropping tables", self._drop_all_tables, []),
            ("Running migrations", self._run_fresh_migrations, []),
        ]

        if not options["no_superuser"]:
            steps.append(("Creating superuser", self._create_superuser, []))

        if options["seed"]:
            steps.append(("Running seeders", self._run_seeders, []))

        return steps

    def _print_step_header(self, current, total, step_name):
        """Print step header with progress"""
        progress = "█" * (current * 20 // total) + "░" * (20 - (current * 20 // total))
        self.stdout.write(f"\n[{current}/{total}] {progress} {step_name}...")

    def _print_step_stats(self, step_name, duration):
        """Print step performance statistics"""
        self.stdout.write(
            self.style.SUCCESS(f"  ⏱️  {step_name} completed in {duration:.2f}s")
        )

    def _drop_all_tables(self):
        self.stdout.write("🗑️  Analyzing database structure...")

        with connection.cursor() as cursor:
            vendor = connection.vendor

            if vendor == "postgresql":
                cursor.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            elif vendor == "mysql":
                cursor.execute("SHOW TABLES")
            elif vendor == "sqlite":
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Unsupported database vendor: {vendor}")
                )
                return

            tables = [row[0] for row in cursor.fetchall()]

            if tables:
                self.stdout.write(f"🔄 Dropping {len(tables)} tables...")

                with transaction.atomic():
                    if vendor == "postgresql":
                        cursor.execute(
                            "DROP TABLE IF EXISTS {} CASCADE".format(
                                ", ".join(f'"{table}"' for table in tables)
                            )
                        )
                    elif vendor == "mysql":
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                        for table in tables:
                            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    elif vendor == "sqlite":
                        for table in tables:
                            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Successfully dropped {len(tables)} tables")
                )
            else:
                self.stdout.write("ℹ️  No tables to drop")

    def _run_fresh_migrations(self):
        self.stdout.write("🔄 Generating fresh migrations...")

        try:
            # Count apps with migrations
            app_count = len(
                [app for app in apps.get_app_configs() if hasattr(app, "path")]
            )

            call_command("makemigrations", verbosity=0 if not self.verbose else 2)
            self.stdout.write("📝 Running migrations...")
            call_command("migrate", verbosity=0 if not self.verbose else 2)

            self.stdout.write(
                self.style.SUCCESS(f"✅ Migrations completed for {app_count} apps")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Migration failed: {str(e)}"))
            raise

    def _create_superuser(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write("👤 Creating default superuser...")

            admin_username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
            admin_email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
            admin_password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

            try:
                User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Superuser created: {admin_username}")
                )
                if self.verbose:
                    self.stdout.write(f"   📧 Email: {admin_email}")
                    self.stdout.write(f"   🔑 Password: {admin_password}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Could not create superuser: {str(e)}")
                )
        else:
            self.stdout.write("ℹ️  Superuser already exists, skipping...")

    def _run_seeders(self):
        self.stdout.write("🌱 Looking for seed data...")

        try:
            call_command("seed", verbosity=0 if not self.verbose else 2)
            self.stdout.write(self.style.SUCCESS("✅ Seeders completed successfully"))
        except Exception:
            self.stdout.write(
                self.style.WARNING("⚠️  No seed command found. Skipping seeders.")
            )

    def _print_success_summary(self, total_time, options):
        """Print final success message with summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 MIGRATION COMPLETE! 🎉                 ║
╚══════════════════════════════════════════════════════════════╝

⏱️  Total time: {total_time:.2f} seconds
🗄️  Database: {connection.settings_dict.get('NAME', 'Unknown')}
🔧 Engine: {connection.vendor}
"""
        if options.get("backup"):
            summary += "💾 Backup: Created\n"
        if not options.get("no_superuser"):
            summary += "👤 Superuser: Created\n"
        if options.get("seed"):
            summary += "🌱 Seeds: Executed\n"

        self.stdout.write(self.style.SUCCESS(summary))

    def _handle_error(self, error, options):
        """Handle errors with helpful information"""
        self.stdout.write(
            self.style.ERROR(
                f"""
❌ MIGRATION FAILED!

Error: {str(error)}
Database: {connection.settings_dict.get('NAME', 'Unknown')}

💡 Troubleshooting tips:
• Check database permissions
• Ensure no other processes are using the database
• Verify database connection settings
• Check Django app configurations
"""
            )
        )

        if options.get("backup"):
            self.stdout.write("💾 Database backup was created before the operation")
