# Agentic AI with Microsoft Agent Framework

## Overview

This repository contains the complete hands-on lab material for learning **Agentic AI** using the **Microsoft Agent Framework**, **Azure AI Foundry**, and **Azure OpenAI**.

The course is organized into four learning days, followed by notebooks, datasets, architecture examples, and capstone projects.

Participants will learn how to design, build, orchestrate, and deploy intelligent AI agents using enterprise-ready patterns.

---

# Course Structure

```
.
├── DAY1
├── DAY2
├── DAY3
├── DAY4
├── Datasets
├── NoteBooks
└── capstone-Projects
```

---

# Repository Contents

## DAY 1 – Agentic AI Foundations & Environment Setup

Topics Covered

- Introduction to Agentic AI
- AI Agents vs Chatbots
- Agent Framework Overview
- Azure AI Foundry
- Azure OpenAI
- Development Environment Setup
- First AI Agent
- DevUI Introduction
- Prompt Engineering Basics

Files

- DAY-1-Agentic_Ai_Foundations___Setup.pdf
- Readme.md

---

## DAY 2 – Workflow Patterns & RAG

Topics Covered

- Sequential Workflows
- Parallel Workflows
- Conditional Routing
- Fan-Out / Fan-In
- Orchestrator Pattern
- Retrieval Augmented Generation (RAG)
- Vector Search
- Knowledge Grounding

Files

- DAy-2-Architecture_Patterns___RAG_Agents__A1_.pdf
- readme.md

---

## DAY 3 – Multi-Agent Systems

Topics Covered

- Multi-Agent Collaboration
- Agent-to-Agent Communication
- Tool Calling
- Memory
- Context Sharing
- Planning Agents
- Reflection
- Agent Coordination

Files

- readme.md

---

## DAY 4 – Enterprise Agentic AI

Topics Covered

- Enterprise AI Architecture
- Azure AI Foundry Deployment
- Responsible AI
- Monitoring
- Evaluation
- Security
- Production Deployment
- Capstone Preparation

Files

- readme.md

---

# Datasets

The Datasets folder contains enterprise sample documents used throughout the labs.

Included datasets

- HR Policy Documents
- Employee Records
- IT Support Knowledge Base
- IT Usage Policy
- Professional Etiquette Guide

These datasets are used for

- RAG
- Search
- Knowledge Grounding
- Enterprise Agents

---

# Notebooks

Jupyter notebooks are provided for all practical exercises.

Examples include

## A2A (Agent-to-Agent)

- a2a_client.ipynb
- a2a_server.ipynb

Demonstrates

- Agent Communication
- Message Passing
- Collaboration

---

## Mini Projects

Hands-on implementation of

- Sequential Workflows
- Parallel Workflows
- Orchestrator Pattern
- Multi-Agent Systems

---

# Capstone Projects

Enterprise-level projects combining all concepts learned during the course.

Examples include

- HR Assistant
- IT Helpdesk Agent
- Vacation Planner
- Enterprise Knowledge Assistant
- Multi-Agent Orchestrator

---

# Prerequisites

- Python 3.11+
- Visual Studio Code
- Git
- Azure Subscription
- Azure AI Foundry Project
- Azure OpenAI Deployment
- Azure CLI

---

# Required Python Packages

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

```env
AI_FOUNDRY_PROJECT_ENDPOINT=<your_project_endpoint>

AI_FOUNDRY_DEPLOYMENT_NAME=<deployment_name>

AZURE_TENANT_ID=<tenant_id>
```

---

# Running the Labs

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run notebooks

```bash
jupyter notebook
```

Run DevUI samples

```bash
python orchestrator-devui.py
```

or

```bash
python parallel-workflow.py
```

---

# Learning Outcomes

By the end of this course, participants will be able to

- Understand Agentic AI concepts
- Build AI agents
- Design workflow orchestration
- Implement RAG
- Develop multi-agent systems
- Connect external tools
- Deploy using Azure AI Foundry
- Monitor enterprise AI applications

---

# Technologies Used

- Microsoft Agent Framework
- Azure AI Foundry
- Azure OpenAI
- Python
- Jupyter Notebook
- DevUI
- Azure CLI
- Vector Search
- RAG
- Agent Orchestration

---

# License

This repository is intended for educational and corporate training purposes.

© AVYUKTi Tech Private Limited
