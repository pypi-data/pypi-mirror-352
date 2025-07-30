# Changelog

---

## Version 0.0.7 - 2025-06-04

### Improvements
- **Relationships**: Allow `record.relation_table to` return a list of the relation_table's item related to record.

## Version 0.0.6 - 2025-05-07

### New Features

- **Relationships**: Add support for foreign keys.

### Improvements

- \***\*select\*\***: enable fetch one with `.get` and `.filter` to return a all that matches the condition.

### Bug Fixes

## Version 0.0.5 - 2025-05-02

### New Features

### Improvements

- **Update Method Return**: `.update()` method now returns the updated record as an object of the class.
- **Delete Method Return**: `.delete()` method now returns a boolean indicating whether the deletion was successful.

### Bug Fixes

- **Database Migrations**: Fixed an issue where schema changes could not be applied to the database in the previous version.

## Version 0.0.4 - 2024-11-08

### New Features

- **Table name**: Use class name as the table name.
- **Tables in plural**: create tables in plural, adding "s" at the end when the class name.

### Improvements

- \***\*tablename\*\***: Use `__tablename__` attribute as it is when provided as table name.
- **Return created row**: on `.create()` method return the created row as an object of the class.

### Bug Fixes

---
