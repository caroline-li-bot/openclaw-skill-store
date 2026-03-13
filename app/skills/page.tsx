"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const categories = [
  { id: "all", name: "All Categories" },
  { id: "ai-content", name: "AI Content" },
  { id: "research", name: "Research" },
  { id: "automation", name: "Automation" },
  { id: "coding", name: "Coding" },
  { id: "data-analysis", name: "Data Analysis" },
  { id: "social-media", name: "Social Media" },
  { id: "productivity", name: "Productivity" },
  { id: "security", name: "Security" },
];

const sortOptions = [
  { value: "downloads", name: "Most Installed" },
  { value: "rating", name: "Highest Rated" },
  { value: "newest", name: "Newest" },
  { value: "security", name: "Security Score" },
];

const mockSkills = [
  {
    id: "pdf-summarizer",
    name: "PDF Summarizer",
    description: "Summarize PDF documents with AI, extract key insights and information",
    author: "openclaw",
    downloads: 12456,
    rating: 4.8,
    securityScore: 9.2,
    category: "Research",
    updatedAt: "2026-03-10",
  },
  {
    id: "web-scraper",
    name: "Web Scraper",
    description: "Extract data from websites with intelligent parsing and anti-blocking",
    author: "community",
    downloads: 9872,
    rating: 4.6,
    securityScore: 8.7,
    category: "Automation",
    updatedAt: "2026-03-11",
  },
  {
    id: "code-reviewer",
    name: "Code Reviewer",
    description: "Automated code review with best practices and security checks",
    author: "dev-team",
    downloads: 8543,
    rating: 4.9,
    securityScore: 9.5,
    category: "Coding",
    updatedAt: "2026-03-12",
  },
  {
    id: "youtube-transcriber",
    name: "YouTube Transcriber",
    description: "Download and transcribe YouTube videos with timestamps and summaries",
    author: "media-team",
    downloads: 7621,
    rating: 4.5,
    securityScore: 7.8,
    category: "AI Content",
    updatedAt: "2026-03-09",
  },
  {
    id: "github-assistant",
    name: "GitHub Assistant",
    description: "Manage GitHub issues, PRs, and repositories automatically",
    author: "openclaw",
    downloads: 24567,
    rating: 4.9,
    securityScore: 9.3,
    category: "Coding",
    updatedAt: "2026-03-12",
  },
  {
    id: "email-assistant",
    name: "Email Assistant",
    description: "Automatically sort, reply to, and organize emails",
    author: "productivity-team",
    downloads: 21345,
    rating: 4.7,
    securityScore: 8.9,
    category: "Automation",
    updatedAt: "2026-03-11",
  },
];

const getSecurityBadge = (score: number) => {
  if (score >= 9) return "bg-green-100 text-green-800";
  if (score >= 7) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
};

export default function SkillsPage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedSort, setSelectedSort] = useState("downloads");
  const [searchQuery, setSearchQuery] = useState("");
  const [skills, setSkills] = useState(mockSkills);

  // Filter skills
  const filteredSkills = skills.filter((skill) => {
    const matchesSearch = skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.author.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "all" || skill.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSearch && matchesCategory;
  });

  // Sort skills
  const sortedSkills = [...filteredSkills].sort((a, b) => {
    switch (selectedSort) {
      case "downloads":
        return b.downloads - a.downloads;
      case "rating":
        return b.rating - a.rating;
      case "newest":
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      case "security":
        return b.securityScore - a.securityScore;
      default:
        return 0;
    }
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Browse Skills</h1>
        <p className="text-lg text-gray-600">
          Discover thousands of pre-built skills for your OpenClaw agents.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search skills by name, description, or author..."
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sort By
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={selectedSort}
              onChange={(e) => setSelectedSort(e.target.value)}
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedSkills.map((skill) => (
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
            <div className="flex flex-wrap gap-3 mt-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                👤 {skill.author}
              </span>
              <span className="flex items-center gap-1">
                ⬇️ {skill.downloads.toLocaleString()}
              </span>
              <span className="flex items-center gap-1">
                ⭐ {skill.rating}
              </span>
              <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                {skill.category}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {sortedSkills.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No skills found</h3>
          <p className="text-gray-600">Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  );
}
