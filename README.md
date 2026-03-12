# OpenClaw Skill Store

A modern, secure, and user-friendly marketplace for OpenClaw AI agent skills. This project aims to be the App Store for AI agent skills, solving the discovery, security, and installation challenges in the current OpenClaw ecosystem.

## ✨ Features

### 🎯 Skill Discovery
- **Category browsing**: AI Content, Research, Automation, Coding, Data Analysis, Social Media
- **Advanced search**: Keyword search with category and tool filters
- **Rankings**: Most Installed, Trending This Week, Highest Rated, Newest Skills
- **Rich skill pages**: Detailed descriptions, usage examples, repository links, installation commands

### 🛡️ Security Scanner (Core Differentiator)
- Automated static code analysis for all skills
- Scans for:
  - Dangerous shell commands
  - Suspicious network calls (curl/wget)
  - File system access patterns
  - API token and credential leaks
  - Exec command usage
- 0-10 security score
- Clear risk labeling: Safe / Needs Review / Dangerous

### 🚀 One-Click Install
- Direct installation via `openclaw install skill-name`
- No manual GitHub cloning or file copying required
- Automatic dependency management

### 🎮 Skill Demos
- Test skills directly in the browser before installing
- Interactive demo environments for common skill types
- Example outputs and use cases

### 🧩 Workflow Templates
- Pre-built agent workflows for common use cases
- YouTube Automation, Research Agent, Coding Agent, and more
- Compatibility graph showing skill interoperability

### 🤖 AI-Native Search
- Natural language query support
- Smart recommendations based on use case
- Context-aware skill suggestions

## 🏗️ Architecture

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Radix UI** - Accessible component library

### Backend
- **FastAPI** - Modern Python API framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Meilisearch** - Full-text search engine

### Infrastructure
- **Vercel** - Frontend hosting and deployment
- **Fly.io** - Backend API hosting
- **GitHub Actions** - CI/CD pipelines
- **Scheduled crawlers** - GitHub skill data synchronization

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 15+
- Meilisearch 1.7+

### Frontend Development
```bash
# Install dependencies
cd openclaw-skill-store
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Backend Development
```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

## 🚢 Deployment

### Vercel Deployment
1. Fork this repository
2. Connect your repository to Vercel
3. Set the following environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   ```
4. Deploy!

### Backend Deployment
The backend can be deployed to any platform that supports Python applications:
- Fly.io (recommended)
- Railway
- Render
- AWS EC2
- Google Cloud Run

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

### Adding Your Skill
1. Ensure your skill repository is public on GitHub
2. Follow the [Skill Packaging Guidelines](docs/SKILL_GUIDELINES.md)
3. Submit your skill via the [Submit Skill](https://openclaw-skill-store.vercel.app/submit) page
4. Our automated scanner will review and approve your skill

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - The core AI agent platform
- [ClawHub](https://clawhub.com) - The original skill registry
- All our contributors and skill developers
