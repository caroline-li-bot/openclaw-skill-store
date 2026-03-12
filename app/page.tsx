import Link from "next/link";

const categories = [
  {
    id: "ai-content",
    name: "AI Content",
    description: "Content generation, writing, and creative AI skills",
    icon: "✍️",
    count: 42,
  },
  {
    id: "research",
    name: "Research",
    description: "Paper search, data analysis, and academic tools",
    icon: "🔬",
    count: 38,
  },
  {
    id: "automation",
    name: "Automation",
    description: "Workflow automation, task scheduling, and RPA",
    icon: "🤖",
    count: 56,
  },
  {
    id: "coding",
    name: "Coding",
    description: "Code generation, debugging, and development tools",
    icon: "💻",
    count: 73,
  },
  {
    id: "data-analysis",
    name: "Data Analysis",
    description: "Data processing, visualization, and business intelligence",
    icon: "📊",
    count: 29,
  },
  {
    id: "social-media",
    name: "Social Media",
    description: "Social media management, posting, and analytics",
    icon: "📱",
    count: 24,
  },
];

const trendingSkills = [
  {
    id: "pdf-summarizer",
    name: "PDF Summarizer",
    description: "Summarize PDF documents with AI, extract key insights and information",
    author: "openclaw",
    downloads: 12456,
    stars: 432,
    securityScore: 9.2,
    category: "Research",
  },
  {
    id: "web-scraper",
    name: "Web Scraper",
    description: "Extract data from websites with intelligent parsing and anti-blocking",
    author: "community",
    downloads: 9872,
    stars: 328,
    securityScore: 8.7,
    category: "Automation",
  },
  {
    id: "code-reviewer",
    name: "Code Reviewer",
    description: "Automated code review with best practices and security checks",
    author: "dev-team",
    downloads: 8543,
    stars: 276,
    securityScore: 9.5,
    category: "Coding",
  },
  {
    id: "youtube-transcriber",
    name: "YouTube Transcriber",
    description: "Download and transcribe YouTube videos with timestamps and summaries",
    author: "media-team",
    downloads: 7621,
    stars: 215,
    securityScore: 7.8,
    category: "AI Content",
  },
];

const popularSkills = [
  {
    id: "github-assistant",
    name: "GitHub Assistant",
    description: "Manage GitHub issues, PRs, and repositories automatically",
    author: "openclaw",
    downloads: 24567,
    stars: 892,
    securityScore: 9.3,
    category: "Coding",
  },
  {
    id: "email-assistant",
    name: "Email Assistant",
    description: "Automatically sort, reply to, and organize emails",
    author: "productivity-team",
    downloads: 21345,
    stars: 756,
    securityScore: 8.9,
    category: "Automation",
  },
  {
    id: "slack-bot",
    name: "Slack Bot",
    description: "Custom Slack bot for team automation and notifications",
    author: "community",
    downloads: 18765,
    stars: 623,
    securityScore: 8.5,
    category: "Social Media",
  },
  {
    id: "research-agent",
    name: "Research Agent",
    description: "Automated academic research assistant with paper search and summarization",
    author: "research-team",
    downloads: 15432,
    stars: 547,
    securityScore: 9.1,
    category: "Research",
  },
];

const getSecurityBadge = (score: number) => {
  if (score >= 9) return "bg-success-100 text-success-800";
  if (score >= 7) return "bg-warning-100 text-warning-800";
  return "bg-danger-100 text-danger-800";
};

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-4 py-12">
        <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
          The App Store for <span className="text-primary-600">AI Agent Skills</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Discover, install, and use thousands of pre-built skills for your OpenClaw agents.
          All skills are security-scanned and ready to use with one click.
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <button className="bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors text-lg">
            Browse Skills
          </button>
          <button className="bg-white text-gray-900 px-8 py-3 rounded-lg font-medium border border-gray-300 hover:bg-gray-50 transition-colors text-lg">
            Submit Skill
          </button>
        </div>
        <div className="flex gap-8 justify-center mt-12 text-gray-600">
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900">500+</div>
            <div className="text-sm">Skills Available</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900">100k+</div>
            <div className="text-sm">Total Installs</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900">2k+</div>
            <div className="text-sm">Active Developers</div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Categories</h2>
          <Link href="/categories" className="text-primary-600 font-medium hover:text-primary-700">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <Link
              key={category.id}
              href={`/categories/${category.id}`}
              className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-md transition-all group"
            >
              <div className="flex items-start gap-4">
                <div className="text-4xl">{category.icon}</div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-gray-900 text-lg group-hover:text-primary-600">
                      {category.name}
                    </h3>
                    <span className="text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      {category.count} skills
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mt-1">{category.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Trending Now */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">🔥 Trending This Week</h2>
          <Link href="/trending" className="text-primary-600 font-medium hover:text-primary-700">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {trendingSkills.map((skill) => (
            <Link
              key={skill.id}
              href={`/skills/${skill.id}`}
              className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-md transition-all group"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-gray-900 text-lg group-hover:text-primary-600">
                    {skill.name}
                  </h3>
                  <p className="text-gray-600 text-sm mt-1 line-clamp-2">{skill.description}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getSecurityBadge(skill.securityScore)}`}>
                  {skill.securityScore}/10
                </span>
              </div>
              <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  👤 {skill.author}
                </span>
                <span className="flex items-center gap-1">
                  ⬇️ {skill.downloads.toLocaleString()}
                </span>
                <span className="flex items-center gap-1">
                  ⭐ {skill.stars}
                </span>
                <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                  {skill.category}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Most Popular */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">⭐ Most Popular</h2>
          <Link href="/popular" className="text-primary-600 font-medium hover:text-primary-700">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {popularSkills.map((skill) => (
            <Link
              key={skill.id}
              href={`/skills/${skill.id}`}
              className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-md transition-all group"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-gray-900 text-lg group-hover:text-primary-600">
                    {skill.name}
                  </h3>
                  <p className="text-gray-600 text-sm mt-1 line-clamp-2">{skill.description}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getSecurityBadge(skill.securityScore)}`}>
                  {skill.securityScore}/10
                </span>
              </div>
              <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  👤 {skill.author}
                </span>
                <span className="flex items-center gap-1">
                  ⬇️ {skill.downloads.toLocaleString()}
                </span>
                <span className="flex items-center gap-1">
                  ⭐ {skill.stars}
                </span>
                <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                  {skill.category}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Security Feature */}
      <section className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-2xl p-12 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="text-5xl">🛡️</div>
          <h2 className="text-3xl font-bold text-gray-900">Security First, Always</h2>
          <p className="text-lg text-gray-700">
            Every skill in the store undergoes automated static analysis to detect potential security risks.
            We scan for dangerous shell commands, network calls, file system access, and credential leaks
            before any skill is published.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white p-6 rounded-xl">
              <div className="text-success-600 text-2xl mb-2">✅</div>
              <h3 className="font-semibold text-gray-900 mb-1">Automatic Scanning</h3>
              <p className="text-sm text-gray-600">Every commit is scanned for security issues</p>
            </div>
            <div className="bg-white p-6 rounded-xl">
              <div className="text-success-600 text-2xl mb-2">📊</div>
              <h3 className="font-semibold text-gray-900 mb-1">Security Score</h3>
              <p className="text-sm text-gray-600">0-10 score indicates trustworthiness</p>
            </div>
            <div className="bg-white p-6 rounded-xl">
              <div className="text-success-600 text-2xl mb-2">🔍</div>
              <h3 className="font-semibold text-gray-900 mb-1">Transparent Reports</h3>
              <p className="text-sm text-gray-600">Full details of all findings are public</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
