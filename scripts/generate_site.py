#!/usr/bin/env python3
"""
Generate a static website from trending AI skill/agent repositories data.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def get_html_template():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub AI Agent/Skill 热门项目</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <style>
        :root {
            --primary: #646cff;
            --bg-dark: #0d1117;
            --bg-card: #161b22;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --border-color: #30363d;
            --accent-green: #238636;
            --accent-blue: #58a6ff;
        }
        
        * { box-sizing: border-box; }
        
        body {
            background: var(--bg-dark);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            text-align: center;
            padding: 3rem 1rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--accent-blue), var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--accent-blue);
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .filters {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .filter-btn {
            padding: 0.5rem 1rem;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-secondary);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .filter-btn:hover, .filter-btn.active {
            background: var(--accent-blue);
            color: white;
            border-color: var(--accent-blue);
        }
        
        .search-box {
            max-width: 500px;
            margin: 0 auto 2rem;
        }
        
        .search-box input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-primary);
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--accent-blue);
        }
        
        .repo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        
        .repo-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .repo-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
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
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .repo-info {
            flex: 1;
            min-width: 0;
        }
        
        .repo-name {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0 0 0.25rem 0;
        }
        
        .repo-name a {
            color: var(--accent-blue);
            text-decoration: none;
        }
        
        .repo-name a:hover {
            text-decoration: underline;
        }
        
        .repo-owner {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .repo-desc {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .repo-meta {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .repo-meta span {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .stars { color: #f1e05a; }
        .forks { color: var(--accent-blue); }
        .issues { color: var(--accent-green); }
        
        .repo-topics {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        
        .topic {
            padding: 0.2rem 0.6rem;
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent-blue);
            border-radius: 12px;
            font-size: 0.75rem;
        }
        
        .language-dot {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.25rem;
        }
        
        .lang-javascript { background: #f1e05a; }
        .lang-python { background: #3572A5; }
        .lang-typescript { background: #2b7489; }
        .lang-go { background: #00ADD8; }
        .lang-rust { background: #dea584; }
        .lang-java { background: #b07219; }
        .lang-cpp { background: #f34b7d; }
        .lang-ruby { background: #701516; }
        .lang-default { background: var(--text-secondary); }
        
        footer {
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
        }
        
        .no-results {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            header h1 { font-size: 1.8rem; }
            .repo-grid { grid-template-columns: 1fr; }
            .stats { gap: 1rem; }
            .stat-value { font-size: 1.4rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 GitHub AI Agent/Skill 热门项目</h1>
            <p>每日自动更新，发现最热门的AI智能体和技能项目</p>
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
        </header>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="搜索项目名称、描述或主题...">
        </div>
        
        <div class="filters">
            <button class="filter-btn active" data-filter="all">全部</button>
            <button class="filter-btn" data-filter="python">Python</button>
            <button class="filter-btn" data-filter="javascript">JavaScript</button>
            <button class="filter-btn" data-filter="typescript">TypeScript</button>
            <button class="filter-btn" data-filter="go">Go</button>
            <button class="filter-btn" data-filter="rust">Rust</button>
        </div>
        
        <div class="repo-grid" id="repoGrid">
            __REPO_CARDS__
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            没有找到匹配的项目
        </div>
    </div>
    
    <footer>
        <p>数据来源: GitHub API | 自动更新: GitHub Actions</p>
        <p>由 Trae AI Skill 生成</p>
    </footer>
    
    <script>
        const repos = __REPOS_JSON__;
        
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
        
        function renderRepos(reposToRender) {
            const grid = document.getElementById('repoGrid');
            const noResults = document.getElementById('noResults');
            
            if (reposToRender.length === 0) {
                grid.style.display = 'none';
                noResults.style.display = 'block';
                return;
            }
            
            grid.style.display = 'grid';
            noResults.style.display = 'none';
            
            grid.innerHTML = reposToRender.map(repo => `
                <div class="repo-card" data-language="${repo.language || 'unknown'}">
                    <div class="repo-header">
                        <img class="repo-avatar" src="${repo.owner.avatar_url}" alt="${repo.owner.login}">
                        <div class="repo-info">
                            <h3 class="repo-name">
                                <a href="${repo.html_url}" target="_blank">${repo.name}</a>
                            </h3>
                            <div class="repo-owner">by ${repo.owner.login}</div>
                        </div>
                    </div>
                    <p class="repo-desc">${repo.description || '暂无描述'}</p>
                    <div class="repo-meta">
                        <span class="stars">⭐ ${formatNumber(repo.stargazers_count)}</span>
                        <span class="forks">🍴 ${formatNumber(repo.forks_count)}</span>
                        <span class="issues">❗ ${formatNumber(repo.open_issues_count)}</span>
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
        
        function filterRepos() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
            
            let filtered = repos;
            
            if (activeFilter !== 'all') {
                filtered = filtered.filter(r => 
                    r.language && r.language.toLowerCase() === activeFilter
                );
            }
            
            if (searchTerm) {
                filtered = filtered.filter(r =>
                    r.name.toLowerCase().includes(searchTerm) ||
                    (r.description && r.description.toLowerCase().includes(searchTerm)) ||
                    (r.topics && r.topics.some(t => t.toLowerCase().includes(searchTerm))) ||
                    r.owner.login.toLowerCase().includes(searchTerm)
                );
            }
            
            renderRepos(filtered);
        }
        
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filterRepos();
            });
        });
        
        document.getElementById('searchInput').addEventListener('input', filterRepos);
        
        renderRepos(repos);
    </script>
</body>
</html>
'''

def format_number(num: int) -> str:
    if num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)

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
    <div class="repo-card" data-language="{repo.get("language", "unknown")}">
        <div class="repo-header">
            <img class="repo-avatar" src="{repo["owner"]["avatar_url"]}" alt="{repo["owner"]["login"]}">
            <div class="repo-info">
                <h3 class="repo-name">
                    <a href="{repo["html_url"]}" target="_blank">{repo["name"]}</a>
                </h3>
                <div class="repo-owner">by {repo["owner"]["login"]}</div>
            </div>
        </div>
        <p class="repo-desc">{repo.get("description") or "暂无描述"}</p>
        <div class="repo-meta">
            <span class="stars">⭐ {format_number(repo["stargazers_count"])}</span>
            <span class="forks">🍴 {format_number(repo["forks_count"])}</span>
            <span class="issues">❗ {format_number(repo["open_issues_count"])}</span>
            {lang_html}
        </div>
        {topics_html}
    </div>
    '''

def generate_site(data: dict, output_dir: str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    repos = data.get("repositories", [])
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
    
    repos_json = json.dumps(repos, ensure_ascii=False)
    repo_cards = "".join(generate_repo_card_html(r) for r in repos)
    
    html = get_html_template()
    html = html.replace("__TOTAL_COUNT__", str(len(repos)))
    html = html.replace("__TOTAL_STARS__", f"{total_stars:,}")
    html = html.replace("__FETCHED_DATE__", fetched_date)
    html = html.replace("__REPO_CARDS__", repo_cards)
    html = html.replace("__REPOS_JSON__", repos_json)
    
    index_path = output_path / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Generated site with {len(repos)} repositories", file=sys.stderr)
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
