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
    const { data: searchResults } = await octokit.rest.search.repos({
      q: "openclaw skill OR openclaw-extension OR openclaw-plugin",
      sort: "stars",
      per_page: 100,
    });

    const processedSkills = [];

    for (const repo of searchResults.items) {
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
        try {
          const { data: skillFile } = await octokit.rest.repos.getContent({
            owner: repo.owner.login,
            repo: repo.name,
            path: "SKILL.md",
          });
          if ('content' in skillFile) {
            const skillContent = atob(skillFile.content);
            // Parse metadata from SKILL.md
            const nameMatch = skillContent.match(/#\s*(.+)/);
            const descMatch = skillContent.match(/description:\s*(.+)/i);
            const categoryMatch = skillContent.match(/category:\s*(.+)/i);
            
            skillMetadata = {
              name: nameMatch ? nameMatch[1].trim() : repo.name,
              description: descMatch ? descMatch[1].trim() : repo.description,
              category: categoryMatch ? categoryMatch[1].trim() : 'Uncategorized',
            };
          }
        } catch (e) {
          // SKILL.md not found, use repo info
        }

        // Security scan
        const securityReport = scanSkillContent(readmeContent + JSON.stringify(skillMetadata));

        // Upsert skill
        const skillData = {
          name: skillMetadata.name || repo.name.replace(/openclaw-|skill-|plugin-/gi, ''),
          description: skillMetadata.description || repo.description || '',
          author: repo.owner.login,
          repository_url: repo.html_url,
          category: skillMetadata.category || 'Uncategorized',
          readme_content: readmeContent,
          security_score: securityReport.score,
          security_risk_level: securityReport.riskLevel,
          security_report: securityReport,
          metadata: {
            stars: repo.stargazers_count,
            forks: repo.forks_count,
            open_issues: repo.open_issues_count,
            last_updated: repo.updated_at,
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
