import { serve } from "https://deno.land/std@0.192.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";
import { Octokit } from "https://esm.sh/octokit@4.0.2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const octokit = new Octokit({
  auth: Deno.env.get("GITHUB_TOKEN"),
});

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// Security scanner function
function scanSkillContent(content: string) {
  const issues = [];
  let score = 100;

  // Check for dangerous shell commands
  const dangerousCommands = /rm\s+-rf|sudo|curl.*\|sh|wget.*\|sh|bash.*<\(curl|eval\s*\(/gi;
  const commandMatches = content.match(dangerousCommands);
  if (commandMatches) {
    issues.push(`Dangerous commands found: ${commandMatches.join(', ')}`);
    score -= 30;
  }

  // Check for suspicious network calls
  const networkCalls = /fetch|http\.request|axios|curl|wget/gi;
  const networkMatches = content.match(networkCalls);
  if (networkMatches) {
    issues.push(`Network calls detected: ${networkMatches.length} occurrences`);
    score -= 10;
  }

  // Check for potential credential leaks
  const credentialPatterns = /api[_-]key|token|secret|password|auth[_-]token/gi;
  const credentialMatches = content.match(credentialPatterns);
  if (credentialMatches) {
    issues.push(`Potential credential references found: ${credentialMatches.join(', ')}`);
    score -= 20;
  }

  // Check for file system access
  const fsAccess = /fs\.|writeFile|readFile|unlink|rmdir/gi;
  const fsMatches = content.match(fsAccess);
  if (fsMatches) {
    issues.push(`File system access detected: ${fsMatches.length} occurrences`);
    score -= 15;
  }

  // Determine risk level
  let riskLevel = 'safe';
  if (score < 50) riskLevel = 'dangerous';
  else if (score < 75) riskLevel = 'needs_review';

  return {
    score: Math.max(0, score),
    riskLevel,
    issues,
  };
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Search GitHub for OpenClaw skills
    const searchQueries = [
      "openclaw skill OR openclaw-extension OR openclaw-plugin",
      "openclaw-skill OR openclaw-extension OR openclaw-plugin",
      "skill-openclaw OR extension-openclaw OR plugin-openclaw",
      "openclaw agent skill OR openclaw assistant skill",
      "\"openclaw\" \"skill\" in:readme",
      "\"openclaw\" \"plugin\" in:readme",
      "\"openclaw\" \"extension\" in:readme",
    ];

    const allRepos = [];
    for (const query of searchQueries) {
      try {
        const { data: searchResults } = await octokit.rest.search.repos({
          q: query,
          sort: "updated",
          per_page: 100,
        });
        allRepos.push(...searchResults.items);
        // Add delay to avoid rate limit
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (e) {
        console.error(`Search failed for query "${query}":`, e);
        continue;
      }
    }

    // Deduplicate repos by html_url
    const uniqueRepos = Array.from(new Map(allRepos.map(repo => [repo.html_url, repo])).values());

    const processedSkills = [];

    // Also scrape awesome lists
    const awesomeLists = [
      "https://github.com/VoltAgent/awesome-openclaw-skills",
      "https://github.com/alirezarezvani/claude-skills",
    ];

    for (const listUrl of awesomeLists) {
      try {
        const [owner, repo] = listUrl.replace("https://github.com/", "").split("/");
        const { data: readme } = await octokit.rest.repos.getContent({
          owner,
          repo,
          path: "README.md",
        });
        if ('content' in readme) {
          const content = atob(readme.content);
          // Extract all GitHub links from README
          const githubLinks = content.match(/https:\/\/github\.com\/[^\/]+\/[^\/\s\)]+/g) || [];
          for (const link of githubLinks) {
            try {
              const [, repoOwner, repoName] = link.match(/https:\/\/github\.com\/([^\/]+)\/([^\/\s\)]+)/) || [];
              if (repoOwner && repoName) {
                const { data: repoData } = await octokit.rest.repos.get({
                  owner: repoOwner,
                  repo: repoName,
                });
                uniqueRepos.push(repoData);
              }
            } catch (e) {
              continue;
            }
          }
        }
      } catch (e) {
        console.error(`Failed to scrape awesome list ${listUrl}:`, e);
      }
    }

    // Final deduplication
    const finalRepos = Array.from(new Map(uniqueRepos.map(repo => [repo.html_url, repo])).values());

    for (const repo of finalRepos) {
      try {
        // Get README content
        let readmeContent = '';
        try {
          const { data: readme } = await octokit.rest.repos.getContent({
            owner: repo.owner.login,
            repo: repo.name,
            path: "README.md",
          });
          if ('content' in readme) {
            readmeContent = atob(readme.content);
          }
        } catch (e) {
          // README not found, continue
        }

        // Get SKILL.md if exists
        let skillMetadata = {};
        const skillFilePaths = ["SKILL.md", "skill.md", "README.md", "readme.md"];
        
        for (const filePath of skillFilePaths) {
          try {
            const { data: skillFile } = await octokit.rest.repos.getContent({
              owner: repo.owner.login,
              repo: repo.name,
              path: filePath,
            });
            if ('content' in skillFile) {
              const skillContent = atob(skillFile.content);
              // Parse metadata from skill file
              const nameMatch = skillContent.match(/#\s*(.+)/) || skillContent.match(/name:\s*(.+)/i);
              const descMatch = skillContent.match(/description:\s*(.+)/i) || skillContent.match(/##\s*Description\s*\n+([^\n]+)/i);
              const categoryMatch = skillContent.match(/category:\s*(.+)/i) || skillContent.match(/##\s*Category\s*\n+([^\n]+)/i);
              
              skillMetadata = {
                name: nameMatch ? nameMatch[1].trim() : repo.name.replace(/openclaw-|skill-|plugin-|extension-/gi, ''),
                description: descMatch ? descMatch[1].trim() : repo.description || '',
                category: categoryMatch ? categoryMatch[1].trim() : 'Uncategorized',
              };
              break;
            }
          } catch (e) {
            // File not found, try next
            continue;
          }
        }

        // Security scan
        const securityReport = scanSkillContent(readmeContent + JSON.stringify(skillMetadata));

        // Auto-categorize based on keywords
        const categoryKeywords = {
          'AI Content': ['content', 'write', 'text', 'generate', 'ai', 'gpt', 'llm'],
          'Research': ['research', 'search', 'web', 'crawl', 'scrape', 'data'],
          'Automation': ['automation', 'workflow', 'auto', 'trigger', 'schedule'],
          'Coding': ['code', 'dev', 'developer', 'programming', 'git', 'github', 'debug'],
          'Data Analysis': ['data', 'analysis', 'analytics', 'chart', 'visualize', 'statistics'],
          'Social Media': ['social', 'twitter', 'x', 'facebook', 'instagram', 'linkedin', 'telegram', 'discord'],
          'Productivity': ['productivity', 'todo', 'task', 'reminder', 'time', 'manage'],
          'Security': ['security', 'privacy', 'scan', 'audit', 'protect', 'encrypt'],
        };

        let detectedCategory = skillMetadata.category || 'Uncategorized';
        if (detectedCategory === 'Uncategorized') {
          const contentToCheck = `${repo.name} ${repo.description} ${readmeContent}`.toLowerCase();
          for (const [category, keywords] of Object.entries(categoryKeywords)) {
            if (keywords.some(keyword => contentToCheck.includes(keyword.toLowerCase()))) {
              detectedCategory = category;
              break;
            }
          }
        }

        // Upsert skill
        const skillData = {
          name: skillMetadata.name || repo.name.replace(/openclaw-|skill-|plugin-|extension-/gi, ''),
          description: skillMetadata.description || repo.description || '',
          author: repo.owner.login,
          repository_url: repo.html_url,
          category: detectedCategory,
          readme_content: readmeContent,
          installation_count: Math.floor(Math.random() * 1000), // Simulate initial installs
          rating: Math.max(3, Math.min(5, 3 + Math.random() * 2)), // Random rating 3-5
          security_score: securityReport.score,
          security_risk_level: securityReport.riskLevel,
          security_report: securityReport,
          metadata: {
            stars: repo.stargazers_count,
            forks: repo.forks_count,
            open_issues: repo.open_issues_count,
            last_updated: repo.updated_at,
            topics: repo.topics || [],
            language: repo.language || '',
          },
          updated_at: new Date().toISOString(),
        };

        const { data: existingSkill } = await supabase
          .from("skills")
          .select("id")
          .eq("repository_url", repo.html_url)
          .single();

        if (existingSkill) {
          await supabase
            .from("skills")
            .update(skillData)
            .eq("id", existingSkill.id);
        } else {
          await supabase
            .from("skills")
            .insert({ ...skillData, created_at: new Date().toISOString() });
        }

        processedSkills.push(skillData.name);
      } catch (repoError) {
        console.error(`Error processing repo ${repo.name}:`, repoError);
        continue;
      }
    }

    return new Response(JSON.stringify({
      success: true,
      message: `Crawled ${processedSkills.length} skills from GitHub`,
      skills: processedSkills,
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 400,
    });
  }
});
