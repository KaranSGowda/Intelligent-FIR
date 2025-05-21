# SQLite Database Guide for Intelligent FIR System

This guide provides instructions for setting up, maintaining, and optimizing the SQLite database for your Intelligent FIR System.

## Initial Setup

To set up the SQLite database:

```bash
python setup_sqlite_db.py
```

This script will:
1. Create the SQLite database file (`fir_system.db`) if it doesn't exist
2. Create all necessary tables
3. Initialize legal sections data
4. Optionally create demo users
5. Apply performance optimizations

## Regular Maintenance

### Creating Backups

To create a backup of your database:

```bash
python backup_sqlite_db.py
```

This will create a timestamped backup in the `backups` directory and automatically remove old backups if there are more than 10.

### Database Maintenance

For various maintenance tasks:

```bash
python maintain_sqlite_db.py
```

This interactive script provides options to:
1. Create database backups
2. Vacuum the database to reclaim space
3. Analyze the database to update statistics
4. Check database integrity
5. Display database information

## Performance Optimizations

The setup script applies several optimizations to improve SQLite performance:

1. **WAL Mode**: Write-Ahead Logging mode improves concurrency and reduces blocking
2. **Synchronous Mode**: Set to NORMAL for better performance while maintaining safety
3. **Foreign Keys**: Enabled to maintain data integrity
4. **Memory Storage**: Temporary tables stored in memory for faster operations
5. **Cache Size**: Increased to improve performance for frequently accessed data

## Best Practices

1. **Regular Backups**: Schedule regular backups using `backup_sqlite_db.py`
2. **Vacuum Regularly**: Run the vacuum operation monthly to reclaim space
3. **Check Integrity**: Periodically check database integrity
4. **Limit Concurrent Access**: SQLite works best with limited concurrent write operations
5. **Keep Updated**: Update SQLite to the latest version for bug fixes and performance improvements

## Troubleshooting

### Database Locked Errors

If you encounter "database is locked" errors:
1. Ensure all connections to the database are properly closed
2. Restart the application
3. If problems persist, restore from a backup

### Corruption Issues

If database corruption occurs:
1. Check integrity using the maintenance script
2. Restore from the most recent backup
3. If no backup is available, try running `PRAGMA integrity_check` and `PRAGMA quick_check` in SQLite

### Performance Issues

If the database becomes slow:
1. Run the vacuum operation
2. Analyze the database
3. Check if the database file has grown too large
4. Consider adding indexes to frequently queried columns

## Limitations of SQLite

SQLite is an excellent choice for many applications, but be aware of its limitations:

1. **Concurrency**: Limited support for concurrent write operations
2. **File Size**: While SQLite can handle databases up to 140TB in theory, practical limits are much lower
3. **Network Access**: Not designed for high-volume client/server applications
4. **Write Performance**: May be slower than client/server databases for write-heavy workloads

For most small to medium applications, these limitations won't be an issue, and SQLite offers excellent simplicity, reliability, and zero-configuration benefits.

## Migrating to Another Database

If your application outgrows SQLite, you can migrate to a client/server database like PostgreSQL:

1. Create a backup of your SQLite database
2. Set up a PostgreSQL database
3. Update your `.env` file with the PostgreSQL connection string
4. Use SQLAlchemy's migration tools or a custom script to transfer the data

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite Optimization FAQ](https://www.sqlite.org/faq.html#q19)
- [SQLite Performance Tips](https://www.sqlite.org/speed.html)
