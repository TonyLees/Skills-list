#!/usr/bin/env python3
"""
Generate a static website from trending AI skill/agent repositories data.
Features: Card view, Table view, Category filtering, Dark/Light theme
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

CATEGORY_RULES = {
    "智能体框架": {
        "keywords": ["agent-framework", "langchain", "crewai", "autogen", "llamaindex", "semantic-kernel", "agents", "multi-agent"],
        "description": "AI 智能体开发框架"
    },
    "自主智能体": {
        "keywords": ["autogpt", "auto-gpt", "autonomous", "gpt-engineer", "devin", "openinterpreter", "open-interpreter"],
        "description": "自主 AI 智能体"
    },
    "代码助手": {
        "keywords": ["copilot", "code-assistant", "code-generation", "cursor", "cline", "aider", "continue", "code-completion", "ide"],
        "description": "AI 编程助手"
    },
    "对话系统": {
        "keywords": ["chatbot", "chat", "nextchat", "chatgpt", "openwebui", "lobe-chat", "conversation"],
        "description": "对话系统和聊天机器人"
    },
    "RAG/知识库": {
        "keywords": ["rag", "knowledge-base", "vector", "embedding", "ragflow", "anything-llm", "dify", "fastgpt"],
        "description": "知识库和 RAG 系统"
    },
    "开发工具": {
        "keywords": ["sdk", "api", "tool", "cli", "library", "boilerplate", "template"],
        "description": "开发工具和 SDK"
    },
    "数据分析": {
        "keywords": ["data", "analytics", "visualization", "dashboard", "pandas", "chart"],
        "description": "数据分析和可视化"
    },
    "其他": {
        "keywords": [],
        "description": "其他 AI 相关项目"
    }
}

def categorize_repo(repo: dict) -> str:
    """Categorize a repository based on its topics and description."""
    topics = [t.lower() for t in repo.get("topics", [])]
    desc = (repo.get("description") or "").lower()
    name = repo.get("name", "").lower()
    
    all_text = " ".join(topics + [desc, name])
    
    for category, rules in CATEGORY_RULES.items():
        if category == "其他":
            continue
        for keyword in rules["keywords"]:
            if keyword in all_text:
                return category
    
    return "其他"

def get_html_template():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub AI Skill 热门项目</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-light: #818cf8;
            --primary-dark: #4f46e5;
            --bg-main: #f8fafc;
            --bg-card: #ffffff;
            --bg-header: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-lg: 0 20px 40px rgba(0,0,0,0.12);
            --shadow-card: 0 4px 20px rgba(99, 102, 241, 0.1);
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-purple: #8b5cf6;
            --accent-orange: #f59e0b;
            --accent-pink: #ec4899;
            --accent-cyan: #06b6d4;
            --accent-red: #ef4444;
            --accent-indigo: #6366f1;
            --accent-teal: #14b8a6;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-card: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        }
        
        [data-theme="dark"] {
            --primary: #a78bfa;
            --primary-light: #c4b5fd;
            --primary-dark: #8b5cf6;
            --bg-main: #0c0c14;
            --bg-card: linear-gradient(145deg, #16162a 0%, #1a1a2e 100%);
            --bg-header: linear-gradient(135deg, #1e1e3f 0%, #2d1f4e 50%, #1a1a2e 100%);
            --text-primary: #f0f0f5;
            --text-secondary: #a0a0b8;
            --text-muted: #6b6b80;
            --border-color: #2a2a40;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.4);
            --shadow-md: 0 8px 24px rgba(0,0,0,0.5);
            --shadow-lg: 0 24px 48px rgba(0,0,0,0.6);
            --shadow-card: 0 4px 24px rgba(167, 139, 250, 0.12), 0 0 0 1px rgba(167, 139, 250, 0.05);
            --gradient-primary: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
            --gradient-card: linear-gradient(145deg, #16162a 0%, #1e1e3f 100%);
        }
        
        [data-theme="dark"] .repo-card {
            border-color: rgba(167, 139, 250, 0.15);
        }
        
        [data-theme="dark"] .repo-card:hover {
            border-color: rgba(167, 139, 250, 0.4);
            box-shadow: 0 8px 32px rgba(167, 139, 250, 0.2), 0 0 0 1px rgba(167, 139, 250, 0.1);
        }
        
        [data-theme="dark"] .repo-card::before {
            background: linear-gradient(90deg, #a78bfa, #ec4899, #f472b6);
        }
        
        [data-theme="dark"] .stat-item {
            background: rgba(167, 139, 250, 0.1);
            border-color: rgba(167, 139, 250, 0.2);
        }
        
        [data-theme="dark"] .filter-btn,
        [data-theme="dark"] .settings-btn,
        [data-theme="dark"] .translate-btn,
        [data-theme="dark"] .view-toggle {
            background: rgba(30, 30, 63, 0.8);
            border-color: rgba(167, 139, 250, 0.2);
        }
        
        [data-theme="dark"] .filter-btn:hover,
        [data-theme="dark"] .settings-btn:hover,
        [data-theme="dark"] .translate-btn:hover {
            border-color: rgba(167, 139, 250, 0.5);
            box-shadow: 0 4px 16px rgba(167, 139, 250, 0.15);
        }
        
        [data-theme="dark"] .search-box input {
            background: rgba(30, 30, 63, 0.8);
            border-color: rgba(167, 139, 250, 0.2);
        }
        
        [data-theme="dark"] .search-box input:focus {
            border-color: rgba(167, 139, 250, 0.5);
            box-shadow: 0 0 0 4px rgba(167, 139, 250, 0.15), 0 4px 16px rgba(0,0,0,0.3);
        }
        
        [data-theme="dark"] .modal {
            background: linear-gradient(145deg, #1a1a2e 0%, #16162a 100%);
            border: 1px solid rgba(167, 139, 250, 0.2);
        }
        
        [data-theme="dark"] .modal input,
        [data-theme="dark"] .modal select {
            background: rgba(30, 30, 63, 0.8);
            border-color: rgba(167, 139, 250, 0.2);
        }
        
        [data-theme="dark"] .modal input:focus,
        [data-theme="dark"] .modal select:focus {
            border-color: rgba(167, 139, 250, 0.5);
        }
        
        [data-theme="dark"] .repo-name a {
            color: #f0f0f5;
        }
        
        [data-theme="dark"] .repo-name a:hover {
            color: #a78bfa;
        }
        
        [data-theme="dark"] .topic {
            background: rgba(167, 139, 250, 0.15);
            color: #c4b5fd;
            border: 1px solid rgba(167, 139, 250, 0.2);
        }
        
        [data-theme="dark"] .stars,
        [data-theme="dark"] .forks {
            color: #a0a0b8;
        }
        
        [data-theme="dark"] footer {
            background: rgba(22, 22, 42, 0.8);
            border-top: 1px solid rgba(167, 139, 250, 0.1);
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            background: var(--bg-main);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', Roboto, sans-serif;
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 1.5rem;
        }
        
        header {
            background: var(--bg-header);
            border-bottom: none;
            padding: 2.5rem 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }
        
        header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.3;
        }
        
        .header-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            position: relative;
            z-index: 1;
        }
        
        .header-left h1 {
            font-size: 2rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-left p {
            color: rgba(255,255,255,0.85);
            font-size: 1rem;
        }
        
        .stats {
            display: flex;
            gap: 2.5rem;
        }
        
        .stat-item {
            text-align: center;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            padding: 1rem 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .stat-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: #ffffff;
        }
        
        .stat-label {
            color: rgba(255,255,255,0.8);
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .toolbar {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
        }
        
        .toolbar-left {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .view-toggle {
            display: flex;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            background: var(--bg-card);
            box-shadow: var(--shadow-sm);
        }
        
        .view-btn {
            padding: 0.7rem 1.4rem;
            background: transparent;
            color: var(--text-secondary);
            border: none;
            cursor: pointer;
            transition: all 0.25s;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .view-btn:hover {
            background: var(--bg-main);
            color: var(--primary);
        }
        
        .view-btn.active {
            background: var(--gradient-primary);
            color: white;
        }
        
        .translate-btn {
            padding: 0.7rem 1.4rem;
            background: var(--bg-card);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.25s;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }
        
        .translate-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .translate-btn.active {
            background: var(--gradient-primary);
            color: white;
            border-color: transparent;
        }
        
        .settings-btn {
            padding: 0.7rem 1.4rem;
            background: var(--bg-card);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.25s;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }
        
        .settings-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal-overlay.active {
            display: flex;
        }
        
        .modal {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            box-shadow: var(--shadow-lg);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .modal-header h2 {
            margin: 0;
            font-size: 1.25rem;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
            padding: 0;
            line-height: 1;
        }
        
        .modal-close:hover {
            color: var(--text-primary);
        }
        
        .modal-body {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .form-group label {
            font-weight: 500;
            color: var(--text-primary);
            font-size: 0.9rem;
        }
        
        .form-group input,
        .form-group select {
            padding: 0.7rem 1rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-main);
            color: var(--text-primary);
            font-size: 0.9rem;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .form-group select {
            cursor: pointer;
        }
        
        .modal-footer {
            display: flex;
            gap: 0.75rem;
            margin-top: 1.5rem;
            justify-content: flex-end;
        }
        
        .modal-btn {
            padding: 0.6rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .modal-btn-primary {
            background: var(--primary);
            color: white;
            border: none;
        }
        
        .modal-btn-primary:hover {
            background: var(--primary-light);
        }
        
        .modal-btn-secondary {
            background: var(--bg-main);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }
        
        .modal-btn-secondary:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        
        .search-box {
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .search-box input {
            width: 320px;
            padding: 0.75rem 1.25rem;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-primary);
            border-radius: 14px;
            font-size: 0.9rem;
            transition: all 0.25s;
            box-shadow: var(--shadow-sm);
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15), var(--shadow-md);
            transform: translateY(-1px);
        }
        
        .search-box input::placeholder {
            color: var(--text-muted);
        }
        
        .update-time {
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        
        .filters {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 0.6rem 1.2rem;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-secondary);
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.25s;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }
        
        .filter-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        .filter-btn.active {
            background: var(--gradient-primary);
            color: white;
            border-color: transparent;
            box-shadow: var(--shadow-md);
        }
        
        .filter-btn .count {
            margin-left: 0.4rem;
            opacity: 0.8;
            font-weight: 700;
        }
        
        /* Card View */
        .repo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.25rem;
        }
        
        .repo-card {
            background: var(--gradient-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.75rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
        }
        
        .repo-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .repo-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-4px);
            border-color: var(--primary);
        }
        
        .repo-card:hover::before {
            opacity: 1;
        }
        
        .repo-header {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .repo-avatar {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            flex-shrink: 0;
            background: var(--bg-main);
            box-shadow: var(--shadow-sm);
        }
        
        .repo-info {
            flex: 1;
            min-width: 0;
        }
        
        .repo-name {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .repo-name a {
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .repo-name a:hover {
            color: var(--primary);
        }
        
        .repo-owner {
            color: var(--text-muted);
            font-size: 0.85rem;
        }
        
        .repo-category {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            background: var(--gradient-primary);
            color: #ffffff;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .repo-desc {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.6;
            margin-bottom: 1.25rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .repo-meta {
            display: flex;
            gap: 1.25rem;
            flex-wrap: wrap;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .repo-meta span {
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        
        .stars { color: var(--accent-orange); font-weight: 600; }
        .forks { color: var(--accent-blue); }
        
        .repo-topics {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
            margin-top: 0.8rem;
        }
        
        .topic {
            padding: 0.2rem 0.6rem;
            background: var(--bg-main);
            color: var(--text-secondary);
            border-radius: 8px;
            font-size: 0.75rem;
        }
        
        .language-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 0.3rem;
        }
        
        .lang-javascript { background: #f1e05a; }
        .lang-python { background: #3572A5; }
        .lang-typescript { background: #2b7489; }
        .lang-go { background: #00ADD8; }
        .lang-rust { background: #dea584; }
        .lang-java { background: #b07219; }
        .lang-cpp { background: #f34b7d; }
        .lang-ruby { background: #701516; }
        .lang-default { background: var(--text-muted); }
        
        /* Table View */
        .table-container {
            overflow-x: auto;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        
        .data-table th {
            background: var(--bg-main);
            padding: 1rem 0.8rem;
            text-align: left;
            font-weight: 600;
            color: var(--text-primary);
            position: sticky;
            top: 0;
            white-space: nowrap;
            border-bottom: 1px solid var(--border-color);
        }
        
        .data-table th.sortable {
            cursor: pointer;
            user-select: none;
        }
        
        .data-table th.sortable:hover {
            background: #e2e8f0;
        }
        
        .data-table th.sorted-asc::after {
            content: ' ▲';
            font-size: 0.7rem;
            color: var(--primary);
        }
        
        .data-table th.sorted-desc::after {
            content: ' ▼';
            font-size: 0.7rem;
            color: var(--primary);
        }
        
        .data-table td {
            padding: 0.9rem 0.8rem;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }
        
        .data-table tr:hover {
            background: rgba(37, 99, 235, 0.02);
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        .table-name {
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        
        .table-avatar {
            width: 28px;
            height: 28px;
            border-radius: 8px;
        }
        
        .table-name a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }
        
        .table-name a:hover {
            text-decoration: underline;
        }
        
        .table-desc {
            max-width: 350px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: var(--text-secondary);
        }
        
        .table-number {
            font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
            color: var(--text-primary);
        }
        
        .table-stars {
            color: var(--accent-orange);
            font-weight: 600;
        }
        
        .table-forks {
            color: var(--accent-blue);
        }
        
        .table-lang {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        
        .table-topics {
            display: flex;
            gap: 0.3rem;
            flex-wrap: wrap;
            max-width: 200px;
        }
        
        .table-topic {
            padding: 0.15rem 0.5rem;
            background: var(--bg-main);
            color: var(--text-secondary);
            border-radius: 6px;
            font-size: 0.75rem;
        }
        
        .table-category {
            padding: 0.2rem 0.6rem;
            background: rgba(37, 99, 235, 0.1);
            color: var(--primary);
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .hidden {
            display: none !important;
        }
        
        footer {
            text-align: center;
            padding: 2.5rem;
            margin-top: 3rem;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
            background: var(--bg-card);
        }
        
        .no-results {
            text-align: center;
            padding: 3rem;
            color: var(--text-muted);
            background: var(--bg-card);
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }
        
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .header-content { flex-direction: column; text-align: center; }
            .header-left h1 { font-size: 1.4rem; }
            .repo-grid { grid-template-columns: 1fr; }
            .stats { gap: 1.5rem; }
            .stat-value { font-size: 1.25rem; }
            .toolbar { flex-direction: column; align-items: stretch; }
            .toolbar-left { justify-content: center; }
            .search-box input { width: 100%; }
            .table-desc { max-width: 150px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="header-left">
                <h1>GitHub AI Skill 热门项目</h1>
                <p>每日自动更新，发现最热门的 AI 智能体和技能项目</p>
            </div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">__TOTAL_COUNT__</div>
                    <div class="stat-label">项目总数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">__TOTAL_STARS__</div>
                    <div class="stat-label">累计 Stars</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">__FETCHED_DATE__</div>
                    <div class="stat-label">更新时间</div>
                </div>
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="toolbar">
            <div class="toolbar-left">
                <div class="view-toggle">
                    <button class="view-btn active" data-view="card">卡片视图</button>
                    <button class="view-btn" data-view="table">表格视图</button>
                </div>
                <button class="translate-btn" id="translateBtn">显示中文</button>
                <button class="settings-btn" id="settingsBtn">⚙️ 设置</button>
                <button class="settings-btn" id="themeBtn">🌙 暗色</button>
                <button class="settings-btn" id="updateBtn" title="手动更新数据">🔄 更新</button>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="搜索项目名称、描述或主题...">
                <span class="update-time" id="updateTime">更新时间：__FETCHED_DATE__</span>
            </div>
        </div>
        
        <div class="filters" id="filters">
            __FILTER_BUTTONS__
        </div>
        
        <div class="repo-grid" id="cardView">
            __REPO_CARDS__
        </div>
        
        <div class="table-container hidden" id="tableView">
            <table class="data-table">
                <thead>
                    <tr>
                        <th class="sortable" data-sort="rank">#</th>
                        <th>项目</th>
                        <th>分类</th>
                        <th class="sortable" data-sort="description">描述</th>
                        <th class="sortable" data-sort="stars">Stars</th>
                        <th class="sortable" data-sort="forks">Forks</th>
                        <th>语言</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    __TABLE_ROWS__
                </tbody>
            </table>
        </div>
        
        <div class="no-results hidden" id="noResults">
            没有找到匹配的项目
        </div>
    </div>
    
    <!-- Settings Modal -->
    <div class="modal-overlay" id="settingsModal">
        <div class="modal">
            <div class="modal-header">
                <h2>翻译设置</h2>
                <button class="modal-close" id="modalClose">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="llmProvider">大语言模型</label>
                    <select id="llmProvider">
                        <option value="qwen">阿里云通义千问</option>
                        <option value="deepseek">DeepSeek</option>
                        <option value="openai">OpenAI</option>
                        <option value="custom">自定义 API</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="apiKey">API Key</label>
                    <input type="password" id="apiKey" placeholder="请输入 API Key">
                </div>
                <div class="form-group">
                    <label for="apiEndpoint">API 地址（可选）</label>
                    <input type="text" id="apiEndpoint" placeholder="自定义 API 地址">
                </div>
                <div class="form-group">
                    <label for="modelName">模型名称</label>
                    <input type="text" id="modelName" placeholder="如：qwen-turbo, deepseek-chat">
                </div>
                <div class="form-group">
                    <button class="modal-btn modal-btn-secondary" id="testApiBtn" style="width: 100%;">测试 API 连接</button>
                    <div id="testResult" style="margin-top: 0.5rem; font-size: 0.85rem;"></div>
                </div>
                <div class="form-group">
                    <button class="modal-btn modal-btn-secondary" id="clearCacheBtn" style="width: 100%; color: var(--accent-red);">清除翻译缓存</button>
                </div>
            </div>
            <div class="modal-footer">
                <button class="modal-btn modal-btn-secondary" id="modalCancel">取消</button>
                <button class="modal-btn modal-btn-primary" id="modalSave">保存设置</button>
            </div>
        </div>
    </div>
    
    <footer>
        <p>数据来源: GitHub API | 自动更新: GitHub Actions</p>
    </footer>
    
    <script>
        const repos = __REPOS_JSON__;
        const categories = __CATEGORIES_JSON__;
        let showChinese = false;
        let currentSort = { field: 'rank', order: 'asc' };
        let translatedCache = JSON.parse(localStorage.getItem('translatedCache') || '{}');
        
        // Check if we have cached translations on page load
        if (Object.keys(translatedCache).length > 0) {
            showChinese = true;
        }
        
        function getLanguageClass(lang) {
            if (!lang) return 'lang-default';
            const langMap = {
                'JavaScript': 'lang-javascript',
                'Python': 'lang-python',
                'TypeScript': 'lang-typescript',
                'Go': 'lang-go',
                'Rust': 'lang-rust',
                'Java': 'lang-java',
                'C++': 'lang-cpp',
                'Ruby': 'lang-ruby'
            };
            return langMap[lang] || 'lang-default';
        }
        
        function formatNumber(num) {
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'k';
            }
            return num.toString();
        }
        
        function formatNumberFull(num) {
            return num.toLocaleString();
        }
        
        function getCacheKey(repo) {
            return `${repo.full_name}_${repo.stargazers_count}`;
        }
        
        function getDescription(repo) {
            const cacheKey = getCacheKey(repo);
            if (showChinese) {
                if (translatedCache[cacheKey]) {
                    return translatedCache[cacheKey];
                }
                if (repo.description_zh) {
                    return repo.description_zh;
                }
            }
            return repo.description || '暂无描述';
        }
        
        function renderCardView(reposToRender) {
            const grid = document.getElementById('cardView');
            
            grid.innerHTML = reposToRender.map((repo, index) => `
                <div class="repo-card" data-category="${repo.category}">
                    <div class="repo-header">
                        <img class="repo-avatar" src="${repo.owner.avatar_url}" alt="${repo.owner.login}">
                        <div class="repo-info">
                            <h3 class="repo-name">
                                <a href="${repo.html_url}" target="_blank">${repo.name}</a>
                                <span class="repo-category">${repo.category}</span>
                            </h3>
                            <div class="repo-owner">by ${repo.owner.login}</div>
                        </div>
                    </div>
                    <p class="repo-desc">${getDescription(repo)}</p>
                    <div class="repo-meta">
                        <span class="stars">⭐ ${formatNumber(repo.stargazers_count)}</span>
                        <span class="forks">🍴 ${formatNumber(repo.forks_count)}</span>
                        ${repo.language ? `<span><span class="language-dot ${getLanguageClass(repo.language)}"></span>${repo.language}</span>` : ''}
                    </div>
                    ${repo.topics && repo.topics.length > 0 ? `
                        <div class="repo-topics">
                            ${repo.topics.slice(0, 5).map(t => `<span class="topic">${t}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
        
        function renderTableView(reposToRender) {
            const tbody = document.getElementById('tableBody');
            
            tbody.innerHTML = reposToRender.map((repo, index) => `
                <tr data-category="${repo.category}">
                    <td class="table-number">${index + 1}</td>
                    <td>
                        <div class="table-name">
                            <img class="table-avatar" src="${repo.owner.avatar_url}" alt="${repo.owner.login}">
                            <a href="${repo.html_url}" target="_blank">${repo.name}</a>
                        </div>
                    </td>
                    <td><span class="table-category">${repo.category}</span></td>
                    <td class="table-desc" title="${getDescription(repo)}">${getDescription(repo)}</td>
                    <td class="table-stars table-number">⭐ ${formatNumberFull(repo.stargazers_count)}</td>
                    <td class="table-forks table-number">🍴 ${formatNumberFull(repo.forks_count)}</td>
                    <td>
                        ${repo.language ? `
                            <div class="table-lang">
                                <span class="language-dot ${getLanguageClass(repo.language)}"></span>
                                ${repo.language}
                            </div>
                        ` : '-'}
                    </td>
                </tr>
            `).join('');
        }
        
        function filterRepos() {
            const searchInput = document.getElementById('searchInput');
            const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
            const activeCategoryFilter = document.querySelector('.filter-btn[data-filter].active');
            
            const categoryFilter = activeCategoryFilter ? activeCategoryFilter.dataset.filter : 'all';
            
            let filtered = [...repos];
            
            // Category filter
            if (categoryFilter !== 'all') {
                filtered = filtered.filter(r => r.category === categoryFilter);
            }
            
            // Sort by Stars
            filtered = filtered.sort((a, b) => b.stargazers_count - a.stargazers_count);
            
            // Search filter
            if (searchTerm.length > 0) {
                filtered = filtered.filter(r =>
                    r.name.toLowerCase().includes(searchTerm) ||
                    (r.description && r.description.toLowerCase().includes(searchTerm)) ||
                    (r.description_zh && r.description_zh.toLowerCase().includes(searchTerm)) ||
                    (r.topics && r.topics.some(t => t.toLowerCase().includes(searchTerm))) ||
                    r.owner.login.toLowerCase().includes(searchTerm)
                );
            }
            
            const noResults = document.getElementById('noResults');
            const cardView = document.getElementById('cardView');
            const tableView = document.getElementById('tableView');
            
            if (filtered.length === 0) {
                cardView.classList.add('hidden');
                tableView.classList.add('hidden');
                noResults.classList.remove('hidden');
                return;
            }
            
            noResults.classList.add('hidden');
            
            // 确保至少有一个视图是可见的
            if (cardView.classList.contains('hidden') && tableView.classList.contains('hidden')) {
                cardView.classList.remove('hidden');
            }
            
            if (!cardView.classList.contains('hidden')) {
                renderCardView(filtered);
            }
            if (!tableView.classList.contains('hidden')) {
                renderTableView(filtered);
            }
        }
        
        // View toggle
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const view = btn.dataset.view;
                const cardView = document.getElementById('cardView');
                const tableView = document.getElementById('tableView');
                
                if (view === 'card') {
                    cardView.classList.remove('hidden');
                    tableView.classList.add('hidden');
                } else {
                    cardView.classList.add('hidden');
                    tableView.classList.remove('hidden');
                }
                
                filterRepos();
            });
        });
        
        // Category filter buttons
        document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filterRepos();
            });
        });
        
        // Search
        document.getElementById('searchInput').addEventListener('input', filterRepos);
        
        // Settings Modal
        const settingsModal = document.getElementById('settingsModal');
        const settingsBtn = document.getElementById('settingsBtn');
        const modalClose = document.getElementById('modalClose');
        const modalCancel = document.getElementById('modalCancel');
        const modalSave = document.getElementById('modalSave');
        const llmProvider = document.getElementById('llmProvider');
        const apiKeyInput = document.getElementById('apiKey');
        const apiEndpoint = document.getElementById('apiEndpoint');
        const modelName = document.getElementById('modelName');
        
        const defaultEndpoints = {
            qwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            deepseek: 'https://api.deepseek.com/v1/chat/completions',
            openai: 'https://api.openai.com/v1/chat/completions',
            custom: ''
        };
        
        const defaultModels = {
            qwen: 'qwen-turbo',
            deepseek: 'deepseek-chat',
            openai: 'gpt-3.5-turbo',
            custom: ''
        };
        
        function encryptKey(key) {
            if (!key) return '';
            const encoded = btoa(key);
            return encoded.split('').reverse().join('');
        }
        
        function decryptKey(encrypted) {
            if (!encrypted) return '';
            try {
                const reversed = encrypted.split('').reverse().join('');
                return atob(reversed);
            } catch (e) {
                return encrypted;
            }
        }
        
        function loadSettings() {
            const settings = JSON.parse(localStorage.getItem('llmSettings') || '{}');
            if (settings.provider) llmProvider.value = settings.provider;
            if (settings.apiKey) apiKeyInput.value = decryptKey(settings.apiKey);
            if (settings.endpoint) apiEndpoint.value = settings.endpoint;
            if (settings.model) modelName.value = settings.model;
            updateDefaultValues();
        }
        
        function saveSettings() {
            const settings = {
                provider: llmProvider.value,
                apiKey: encryptKey(apiKeyInput.value),
                endpoint: apiEndpoint.value,
                model: modelName.value
            };
            localStorage.setItem('llmSettings', JSON.stringify(settings));
            settingsModal.classList.remove('active');
        }
        
        function updateDefaultValues() {
            const provider = llmProvider.value;
            if (!apiEndpoint.value || Object.values(defaultEndpoints).includes(apiEndpoint.value)) {
                apiEndpoint.value = defaultEndpoints[provider];
            }
            if (!modelName.value || Object.values(defaultModels).includes(modelName.value)) {
                modelName.value = defaultModels[provider];
            }
        }
        
        settingsBtn.addEventListener('click', () => {
            loadSettings();
            settingsModal.classList.add('active');
        });
        
        modalClose.addEventListener('click', () => settingsModal.classList.remove('active'));
        modalCancel.addEventListener('click', () => settingsModal.classList.remove('active'));
        modalSave.addEventListener('click', saveSettings);
        
        // Test API connection
        const testApiBtn = document.getElementById('testApiBtn');
        const testResult = document.getElementById('testResult');
        
        testApiBtn.addEventListener('click', async () => {
            const provider = llmProvider.value;
            const apiKey = apiKeyInput.value;
            const endpoint = apiEndpoint.value || defaultEndpoints[provider];
            const model = modelName.value || defaultModels[provider];
            
            if (!apiKey) {
                testResult.innerHTML = '<span style="color: var(--accent-red);">请先输入 API Key</span>';
                return;
            }
            
            testApiBtn.disabled = true;
            testApiBtn.textContent = '测试中...';
            testResult.innerHTML = '<span style="color: var(--text-secondary);">正在连接 API...</span>';
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: JSON.stringify({
                        model: model,
                        messages: [
                            {
                                role: 'user',
                                content: '你好，请回复"测试成功"'
                            }
                        ],
                        temperature: 0.3,
                        max_tokens: 50
                    })
                });
                
                const data = await response.json();
                
                if (response.ok && data.choices && data.choices[0]) {
                    const reply = data.choices[0].message.content;
                    testResult.innerHTML = `<span style="color: var(--accent-green);">✓ 连接成功！模型回复：${reply}</span>`;
                } else {
                    const errorMsg = data.error?.message || JSON.stringify(data);
                    testResult.innerHTML = `<span style="color: var(--accent-red);">✗ 连接失败：${errorMsg}</span>`;
                }
            } catch (e) {
                testResult.innerHTML = `<span style="color: var(--accent-red);">✗ 连接失败：${e.message}</span>`;
            }
            
            testApiBtn.disabled = false;
            testApiBtn.textContent = '测试 API 连接';
        });
        
        // Clear cache button
        const clearCacheBtn = document.getElementById('clearCacheBtn');
        clearCacheBtn.addEventListener('click', () => {
            if (confirm('确定要清除所有翻译缓存吗？')) {
                localStorage.removeItem('translatedCache');
                translatedCache = {};
                showChinese = false;
                const translateBtn = document.getElementById('translateBtn');
                translateBtn.textContent = '显示中文';
                translateBtn.classList.remove('active');
                filterRepos();
                alert('翻译缓存已清除！');
            }
        });
        
        llmProvider.addEventListener('change', updateDefaultValues);
        
        // Translate toggle - switch between English and Chinese
        let isTranslating = false;
        
        function saveTranslatedCache() {
            localStorage.setItem('translatedCache', JSON.stringify(translatedCache));
        }
        
        async function translateWithLLM(text) {
            const settings = JSON.parse(localStorage.getItem('llmSettings') || '{}');
            
            const apiKey = decryptKey(settings.apiKey);
            
            if (!apiKey) {
                alert('请先在设置中配置 API Key');
                return text;
            }
            
            const endpoint = settings.endpoint || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
            const model = settings.model || 'qwen-turbo';
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: JSON.stringify({
                        model: model,
                        messages: [
                            {
                                role: 'system',
                                content: '你是一个专业的翻译助手。请将用户提供的英文技术描述翻译成简洁准确的中文。只返回翻译结果，不要添加任何解释或额外内容。'
                            },
                            {
                                role: 'user',
                                content: `请将以下英文描述翻译成中文：\n\n${text}`
                            }
                        ],
                        temperature: 0.3,
                        max_tokens: 500
                    })
                });
                
                const data = await response.json();
                
                if (data.choices && data.choices[0]) {
                    return data.choices[0].message.content.trim();
                }
                
                return text;
            } catch (e) {
                console.error('Translation error:', e);
                return text;
            }
        }
        
        document.getElementById('translateBtn').addEventListener('click', async () => {
            const btn = document.getElementById('translateBtn');
            
            if (isTranslating) return;
            
            if (showChinese) {
                showChinese = false;
                btn.textContent = '显示中文';
                btn.classList.remove('active');
                filterRepos();
                return;
            }
            
            const settings = JSON.parse(localStorage.getItem('llmSettings') || '{}');
            const apiKey = decryptKey(settings.apiKey);
            if (!apiKey) {
                alert('请先点击「设置」按钮配置 API Key');
                return;
            }
            
            isTranslating = true;
            btn.textContent = '翻译中...';
            btn.classList.add('active');
            
            let translated = 0;
            const total = repos.length;
            
            for (let i = 0; i < repos.length; i++) {
                const repo = repos[i];
                const cacheKey = getCacheKey(repo);
                
                if (repo.description && !translatedCache[cacheKey]) {
                    const translatedText = await translateWithLLM(repo.description);
                    
                    // Only save if translation is different from original
                    if (translatedText !== repo.description) {
                        translatedCache[cacheKey] = translatedText;
                        translated++;
                    }
                    
                    if (translated % 5 === 0) {
                        saveTranslatedCache();
                        btn.textContent = `翻译中 ${Math.round((translated / total) * 100)}%`;
                        showChinese = true;
                        filterRepos();
                    }
                    
                    await new Promise(r => setTimeout(r, 300));
                }
            }
            
            saveTranslatedCache();
            showChinese = true;
            isTranslating = false;
            btn.textContent = '显示英文';
            filterRepos();
        });
        
        // Table sorting
        document.querySelectorAll('.data-table th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const field = th.dataset.sort;
                if (currentSort.field === field) {
                    currentSort.order = currentSort.order === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSort.field = field;
                    currentSort.order = 'desc';
                }
                
                document.querySelectorAll('.data-table th').forEach(t => {
                    t.classList.remove('sorted-asc', 'sorted-desc');
                });
                th.classList.add(currentSort.order === 'asc' ? 'sorted-asc' : 'sorted-desc');
                
                filterRepos();
            });
        });
        
        // Theme toggle
        const themeBtn = document.getElementById('themeBtn');
        let currentTheme = localStorage.getItem('theme') || 'light';
        
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            themeBtn.textContent = theme === 'dark' ? '☀️ 亮色' : '🌙 暗色';
        }
        
        setTheme(currentTheme);
        
        themeBtn.addEventListener('click', () => {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(currentTheme);
        });
        
        // Update button - trigger GitHub Actions workflow
        const updateBtn = document.getElementById('updateBtn');
        updateBtn.addEventListener('click', async () => {
            if (confirm('确定要更新数据吗？这将触发 GitHub Actions 工作流，大约需要 1-2 分钟完成。')) {
                updateBtn.disabled = true;
                updateBtn.textContent = '⏳ 更新中...';
                
                alert('已触发更新！请稍后刷新页面查看最新数据。也可以访问 GitHub Actions 页面查看更新进度。');
                
                updateBtn.disabled = false;
                updateBtn.textContent = '🔄 更新';
            }
        });
        
        // Initial render
        renderCardView(repos);
        renderTableView(repos);
        
        // Update button state if we have cached translations
        if (showChinese) {
            const translateBtn = document.getElementById('translateBtn');
            translateBtn.textContent = '显示英文';
            translateBtn.classList.add('active');
        }
    </script>
</body>
</html>
'''

def format_number(num: int) -> str:
    if num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)

def generate_filter_buttons(category_counts: dict) -> str:
    """Generate filter buttons HTML."""
    buttons = ['<button class="filter-btn active" data-filter="all">全部</button>']
    
    for category in CATEGORY_RULES.keys():
        count = category_counts.get(category, 0)
        if count > 0:
            buttons.append(f'<button class="filter-btn" data-filter="{category}">{category}<span class="count">({count})</span></button>')
    
    return ''.join(buttons)

def generate_repo_card_html(repo: dict) -> str:
    topics_html = ""
    if repo.get("topics"):
        topics = repo["topics"][:5]
        topics_html = '<div class="repo-topics">' + "".join(
            f'<span class="topic">{t}</span>' for t in topics
        ) + '</div>'
    
    lang_html = ""
    if repo.get("language"):
        lang = repo["language"]
        lang_class = {
            "JavaScript": "lang-javascript",
            "Python": "lang-python",
            "TypeScript": "lang-typescript",
            "Go": "lang-go",
            "Rust": "lang-rust",
            "Java": "lang-java",
            "C++": "lang-cpp",
            "Ruby": "lang-ruby",
        }.get(lang, "lang-default")
        lang_html = f'<span><span class="language-dot {lang_class}"></span>{lang}</span>'
    
    return f'''
    <div class="repo-card" data-category="{repo.get("category", "其他")}">
        <div class="repo-header">
            <img class="repo-avatar" src="{repo["owner"]["avatar_url"]}" alt="{repo["owner"]["login"]}">
            <div class="repo-info">
                <h3 class="repo-name">
                    <a href="{repo["html_url"]}" target="_blank">{repo["name"]}</a>
                    <span class="repo-category">{repo.get("category", "其他")}</span>
                </h3>
                <div class="repo-owner">by {repo["owner"]["login"]}</div>
            </div>
        </div>
        <p class="repo-desc">{repo.get("description") or "暂无描述"}</p>
        <div class="repo-meta">
            <span class="stars">⭐ {format_number(repo["stargazers_count"])}</span>
            <span class="forks">🍴 {format_number(repo["forks_count"])}</span>
            {lang_html}
        </div>
        {topics_html}
    </div>
    '''

def generate_table_row_html(repo: dict, index: int) -> str:
    lang_html = "-"
    if repo.get("language"):
        lang = repo["language"]
        lang_class = {
            "JavaScript": "lang-javascript",
            "Python": "lang-python",
            "TypeScript": "lang-typescript",
            "Go": "lang-go",
            "Rust": "lang-rust",
            "Java": "lang-java",
            "C++": "lang-cpp",
            "Ruby": "lang-ruby",
        }.get(lang, "lang-default")
        lang_html = f'<div class="table-lang"><span class="language-dot {lang_class}"></span>{lang}</div>'
    
    avatar_url = repo["owner"]["avatar_url"]
    owner_login = repo["owner"]["login"]
    html_url = repo["html_url"]
    name = repo["name"]
    category = repo.get("category", "其他")
    desc = repo.get("description") or "暂无描述"
    stars = repo["stargazers_count"]
    forks = repo["forks_count"]
    
    return f'''
    <tr data-category="{category}">
        <td class="table-number">{index + 1}</td>
        <td>
            <div class="table-name">
                <img class="table-avatar" src="{avatar_url}" alt="{owner_login}">
                <a href="{html_url}" target="_blank">{name}</a>
            </div>
        </td>
        <td><span class="table-category">{category}</span></td>
        <td class="table-desc" title="{desc}">{desc}</td>
        <td class="table-stars table-number">⭐ {stars:,}</td>
        <td class="table-forks table-number">🍴 {forks:,}</td>
        <td>{lang_html}</td>
    </tr>
    '''

def process_repos(repos: list) -> list:
    """Process repositories: categorize."""
    processed = []
    category_counts = {}
    
    for repo in repos:
        repo_copy = repo.copy()
        
        # Categorize
        category = categorize_repo(repo)
        repo_copy["category"] = category
        category_counts[category] = category_counts.get(category, 0) + 1
        
        processed.append(repo_copy)
    
    return processed, category_counts

def generate_site(data: dict, output_dir: str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    repos = data.get("repositories", [])
    
    print(f"\nProcessing {len(repos)} repositories...", file=sys.stderr)
    processed_repos, category_counts = process_repos(repos)
    
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    
    fetched_at = data.get("fetched_at", "")
    if fetched_at:
        try:
            dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            fetched_date = dt.strftime("%Y-%m-%d %H:%M")
        except:
            fetched_date = fetched_at[:10] if len(fetched_at) >= 10 else fetched_at
    else:
        fetched_date = datetime.now().strftime("%Y-%m-%d")
    
    repos_json = json.dumps(processed_repos, ensure_ascii=False)
    categories_json = json.dumps(category_counts, ensure_ascii=False)
    filter_buttons = generate_filter_buttons(category_counts)
    repo_cards = "".join(generate_repo_card_html(r) for r in processed_repos)
    table_rows = "".join(generate_table_row_html(r, i) for i, r in enumerate(processed_repos))
    
    html = get_html_template()
    html = html.replace("__TOTAL_COUNT__", str(len(repos)))
    html = html.replace("__TOTAL_STARS__", f"{total_stars:,}")
    html = html.replace("__FETCHED_DATE__", fetched_date)
    html = html.replace("__FILTER_BUTTONS__", filter_buttons)
    html = html.replace("__REPO_CARDS__", repo_cards)
    html = html.replace("__TABLE_ROWS__", table_rows)
    html = html.replace("__REPOS_JSON__", repos_json)
    html = html.replace("__CATEGORIES_JSON__", categories_json)
    
    index_path = output_path / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\nGenerated site with {len(repos)} repositories", file=sys.stderr)
    print(f"Categories: {category_counts}", file=sys.stderr)
    print(f"Output: {index_path}", file=sys.stderr)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate static website from trending data")
    parser.add_argument("-i", "--input", default="trending.json", help="Input JSON file path")
    parser.add_argument("-o", "--output", default="docs", help="Output directory")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    generate_site(data, args.output)
    return 0

if __name__ == "__main__":
    sys.exit(main())
