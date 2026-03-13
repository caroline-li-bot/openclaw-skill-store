"use client";

import { useState } from "react";

export default function SubmitPage() {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    repositoryUrl: "",
    category: "",
    authorName: "",
    authorEmail: "",
    readmeContent: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const categories = [
    { id: "ai-content", name: "AI Content" },
    { id: "research", name: "Research" },
    { id: "automation", name: "Automation" },
    { id: "coding", name: "Coding" },
    { id: "data-analysis", name: "Data Analysis" },
    { id: "social-media", name: "Social Media" },
    { id: "productivity", name: "Productivity" },
    { id: "security", name: "Security" },
    { id: "other", name: "Other" },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate submission
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsSubmitting(false);
    setSubmitSuccess(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (submitSuccess) {
    return (
      <div className="max-w-3xl mx-auto text-center py-12">
        <div className="text-6xl mb-6">🎉</div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Skill Submitted!</h1>
        <p className="text-lg text-gray-600 mb-8">
          Thank you for contributing to the OpenClaw Skill Store. Your skill is now being reviewed and security scanned.
          We'll notify you via email once it's published.
        </p>
        <div className="bg-green-50 p-6 rounded-xl border border-green-200 mb-8">
          <h3 className="font-semibold text-green-900 mb-2">What happens next?</h3>
          <ol className="text-left text-green-800 space-y-2">
            <li>1. Automated security scan (usually takes 1-2 minutes)</li>
            <li>2. Manual review by our team (if needed)</li>
            <li>3. Skill published to the store within 24 hours</li>
          </ol>
        </div>
        <a
          href="/skills"
          className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          Browse All Skills
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Submit Your Skill</h1>
        <p className="text-lg text-gray-600">
          Share your OpenClaw skill with the community. All submissions undergo automated security scanning before publication.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-xl border border-gray-200">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Skill Name *
          </label>
          <input
            type="text"
            id="name"
            name="name"
            required
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="e.g., PDF Summarizer"
            value={formData.name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Short Description *
          </label>
          <textarea
            id="description"
            name="description"
            required
            rows={3}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Briefly describe what your skill does..."
            value={formData.description}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="repositoryUrl" className="block text-sm font-medium text-gray-700 mb-2">
            GitHub Repository URL *
          </label>
          <input
            type="url"
            id="repositoryUrl"
            name="repositoryUrl"
            required
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="https://github.com/your-username/your-skill"
            value={formData.repositoryUrl}
            onChange={handleChange}
          />
          <p className="text-sm text-gray-500 mt-1">
            Your repository must contain a SKILL.md file in the root directory.
          </p>
        </div>

        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select
            id="category"
            name="category"
            required
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            value={formData.category}
            onChange={handleChange}
          >
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="authorName" className="block text-sm font-medium text-gray-700 mb-2">
              Author Name *
            </label>
            <input
              type="text"
              id="authorName"
              name="authorName"
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Your name"
              value={formData.authorName}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="authorEmail" className="block text-sm font-medium text-gray-700 mb-2">
              Author Email *
            </label>
            <input
              type="email"
              id="authorEmail"
              name="authorEmail"
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="your@email.com"
              value={formData.authorEmail}
              onChange={handleChange}
            />
            <p className="text-sm text-gray-500 mt-1">
              We'll notify you when your skill is published.
            </p>
          </div>
        </div>

        <div>
          <label htmlFor="readmeContent" className="block text-sm font-medium text-gray-700 mb-2">
            README Content (Optional)
          </label>
          <textarea
            id="readmeContent"
            name="readmeContent"
            rows={8}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Paste your README content here (or we'll fetch it from GitHub)..."
            value={formData.readmeContent}
            onChange={handleChange}
          />
        </div>

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">Security Scan Requirements</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• No dangerous shell commands (rm -rf, sudo, etc.)</li>
            <li>• No hardcoded API keys or secrets</li>
            <li>• Network calls must be documented and necessary</li>
            <li>• File system access must be limited to temporary directories</li>
          </ul>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? "Submitting..." : "Submit Skill"}
        </button>
      </form>
    </div>
  );
}
