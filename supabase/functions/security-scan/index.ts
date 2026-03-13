import { serve } from "https://deno.land/std@0.192.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

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

  // Check for exec usage
  const execPattern = /exec\s*\(|spawn\s*\(|child_process/gi;
  const execMatches = content.match(execPattern);
  if (execMatches) {
    issues.push(`Process execution detected: ${execMatches.length} occurrences`);
    score -= 25;
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
    const { content, repository_url } = await req.json();

    const securityReport = scanSkillContent(content);

    // Update skill in database if repository_url is provided
    if (repository_url) {
      await supabase
        .from("skills")
        .update({
          security_score: securityReport.score,
          security_risk_level: securityReport.riskLevel,
          security_report: securityReport,
          updated_at: new Date().toISOString(),
        })
        .eq("repository_url", repository_url);
    }

    return new Response(JSON.stringify({
      success: true,
      data: securityReport,
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
