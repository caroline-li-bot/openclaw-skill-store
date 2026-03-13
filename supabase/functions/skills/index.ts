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

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const { searchParams } = new URL(req.url);
  const skillId = searchParams.get("id");

  try {
    if (skillId) {
      // Get single skill
      const { data, error } = await supabase
        .from("skills")
        .select("*, skill_versions(*)")
        .eq("id", skillId)
        .single();

      if (error) throw error;

      // Track view
      await supabase.from("analytics").insert({
        skill_id: skillId,
        event_type: "view",
        ip_address: req.headers.get("x-forwarded-for") || null,
        user_agent: req.headers.get("user-agent") || null,
      });

      return new Response(JSON.stringify({
        success: true,
        data,
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      });
    } else {
      // List skills
      const limit = parseInt(searchParams.get("limit") || "20");
      const offset = parseInt(searchParams.get("offset") || "0");
      const category = searchParams.get("category");
      const sort = searchParams.get("sort") || "installation_count";
      const order = searchParams.get("order") || "desc";

      let dbQuery = supabase
        .from("skills")
        .select("*")
        .range(offset, offset + limit - 1);

      if (category) {
        dbQuery = dbQuery.eq("category", category);
      }

      dbQuery = dbQuery.order(sort, { ascending: order === "asc" });

      const { data, error } = await dbQuery;

      if (error) throw error;

      return new Response(JSON.stringify({
        success: true,
        data,
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      });
    }
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
