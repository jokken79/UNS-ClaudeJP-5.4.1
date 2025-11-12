# Yukyu (有給休暇) System - Complete Documentation

**Document Date:** 2025-11-12  
**Version:** 1.0  
**Status:** ✅ All Systems Operational  
**Last Updated:** After completing full system analysis and fixes

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Japanese Labor Law Compliance](#japanese-labor-law-compliance)
3. [Architecture](#architecture)
4. [Fixed Issues (2025-11-12)](#fixed-issues-2025-11-12)
5. [API Endpoints Documentation](#api-endpoints-documentation)
6. [Database Schema](#database-schema)
7. [Business Logic](#business-logic)
8. [Frontend Integration](#frontend-integration)
9. [Testing & Verification](#testing--verification)
10. [Troubleshooting](#troubleshooting)
11. [Future Improvements](#future-improvements)

---

## System Overview

### What is Yukyu (有給休暇)?

**Yukyu** (有給休暇, *yūkyū kyūka*) is **paid vacation** under Japanese labor law. The yukyu system in UNS-ClaudeJP manages:

- **Automatic calculation** of yukyu days based on employment duration
- **Balance tracking** across multiple fiscal years
- **Request workflow** (TANTOSHA creates → KEIRI approves)
- **LIFO deduction** (newest yukyus used first)
- **Automatic expiration** after 2 years (時効 - *jikou*)
- **Compliance alerts** for 5-day minimum usage requirement

### Key Terms

| Japanese | Romaji | English | Description |
|----------|--------|---------|-------------|
| 有給休暇 | yūkyū kyūka | Paid vacation | Annual leave with full pay |
| 半休 | hankyū | Half day | 0.5 day vacation (morning/afternoon) |
| 一時帰国 | ichiji kikoku | Temporary return home | Extended leave to visit home country |
| 退社 | taisha | Resignation | Final leave before termination |
| 時効 | jikou | Expiration | 2-year statute of limitations |
| 担当者 | tantōsha | Coordinator | Staff who creates requests |
| 経理 | keiri | Accounting | Staff who approves requests |

### System Components



---

## Japanese Labor Law Compliance

### Yukyu Entitlement Rules

The system automatically calculates yukyu days based on **employment duration** following Japanese labor law (労働基準法):

| Months Worked | Days Entitled | Trigger Event |
|---------------|---------------|---------------|
| 6 months | 10 days | Initial entitlement (最初の付与) |
| 18 months | 11 days | +1 day per year |
| 30 months | 12 days | +1 day per year |
| 42 months | 14 days | +2 days per year |
| 54 months | 16 days | +2 days per year |
| 66 months | 18 days | +2 days per year |
| 78+ months | 20 days | Maximum (上限) |

### Key Legal Requirements

1. **Minimum 5 Days** (年5日の年次有給休暇の取得義務)
   - Employers MUST ensure employees take at least 5 days per year
   - Implemented in April 2019 (Labor Standards Act amendment)
   - System tracks compliance and sends alerts

2. **2-Year Expiration** (時効 - jikou)
   - Unused yukyu expires after 2 years from assignment date
   - System automatically marks expired balances
   - Expired days cannot be recovered

3. **LIFO Deduction** (後入先出法)
   - When approved, newest yukyus are used first
   - Maximizes usage before expiration
   - Protects older yukyus from expiring

---

## Architecture

### Tech Stack

- **Backend:** FastAPI 0.115.6 with Python 3.11+
- **Frontend:** Next.js 16.0.0 with React 19.0.0
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0.36

### File Structure



---

## Fixed Issues (2025-11-12)

This section documents all the issues that were identified and fixed during today's complete analysis.

