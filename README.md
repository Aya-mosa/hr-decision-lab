# HR Decision Lab | مختبر قرار الموارد البشرية

A full-stack web application that assesses HR decision-making patterns through realistic, AI-generated workplace scenarios — built for an internal client to evaluate HR professionals and job candidates.

**Live demo:** [app.theagilehr.com](https://app.theagilehr.com)

## Overview

Users (team members or job candidates) are invited by email to complete a series of realistic HR scenarios tailored to their seniority level. Each decision is scored against a set of behavioral archetypes, producing a final report that identifies the user's dominant decision-making pattern versus the target pattern for their level — complete with an AI-generated narrative summary and a shareable result card.

Admins manage the whole flow from a dashboard: sending invite batches (separated by team members vs. candidates), tracking completion status, and reviewing individual and aggregate reports.

## Features

- 🧠 **AI-generated scenarios** — dynamic, schema-validated scenarios generated per session via an LLM (OpenRouter), scoped by seniority level and category
- 📊 **Pattern analysis engine** — rule-based classification of decision archetypes with AI-polished narrative summaries
- ✉️ **Invite-based assessment flow** — admins send batched email invites with optional deadlines; recipients complete the assessment via a unique link, no account required
- 🔐 **Admin dashboard** — gated signup, session-based auth, batch invite creation, status tracking, and per-candidate report access
- 📤 **Result sharing** — users can email their own result to a peer, or download a shareable pattern card
- 🌐 **Fully Arabic (RTL) interface**

## Tech Stack

**Backend**
- FastAPI (Python) — REST API
- SQLAlchemy + PostgreSQL — persistence
- OpenRouter API — LLM scenario generation & report narrative polishing
- Resend — transactional email delivery

**Frontend**
- Next.js (App Router) + React
- Tailwind CSS

**Infrastructure**
- Railway — backend + PostgreSQL hosting
- Vercel — frontend hosting

## Project Structure
