# Snowflake SQL Toolkit

A personal reference repository of **Snowflake-specific SQL queries** for operational visibility, diagnostics, and task scheduling analysis.

This repo exists purely as a **memory aid and speed tool** — a place to quickly grab proven queries when I know *what* I want to do but don’t want to re-derive *how* to do it.

---

## 🎯 Scope

This repository intentionally includes:

- Snowflake `INFORMATION_SCHEMA` queries
- Task scheduling and execution history
- Job monitoring and operational diagnostics
- Metadata and system-level visibility

This repository intentionally **does NOT include**:

- Business logic
- Private schema or table data
- Application-specific datasets
- Anything environment- or company-sensitive

All queries are safe to reuse across Snowflake accounts with minimal edits.

---

## 🧠 Design Philosophy

- **Recall-first**: Optimized for quick lookup, not tutorials
- **Copy–paste ready**: Minimal setup, light parameterization
- **Snowflake-native**: Uses Snowflake functions and syntax freely
- **Readable > clever**: Clear intent beats dense SQL

If it’s here, it’s because I’ve:
- Used it before
- Forgotten it before
- Or don’t want to Google it again

---

## 📂 Organization

Queries are grouped loosely by purpose, such as:

- Task history & scheduling
- Execution state and failures
- Timing and performance checks
- Information schema inspection

Folders and filenames are descriptive rather than rigid — this is a toolbox, not a framework.

---

## ⚠️ Usage Notes

- Review filters and time windows before running
- Some queries may be resource-intensive if unbounded
- Syntax may rely on Snowflake-specific features (e.g., `MAX_BY`, `TASK_HISTORY`)
- Assumes appropriate account or schema-level permissions

---

## 🔁 Maintenance

This repo is expected to evolve organically:
- Queries may be added, renamed, or replaced
- No guarantee of backwards compatibility
- Notes may be terse by design

If it saved future-me 10 minutes, it did its job.

---

## 📝 License

Personal reference use.
Safe to reuse or adapt.

