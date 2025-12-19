-- Complete Expert Avatar Mapping
-- Maps your existing images to expert profiles
-- Your Supabase Storage URL: https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/

-- ==============================================
-- STEP 1: Update Existing 5 Experts
-- ==============================================

-- Sarah Chen - Small Business Tax CPA (Female, Professional)
UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/sarah_chen.jpg',
    updated_at = NOW()
WHERE email = 'sarah@concierge.ai';

-- Emily Thompson - Bookkeeper (Female, Friendly)
UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/emily_thompson.jpg',
    updated_at = NOW()
WHERE email = 'emily@concierge.ai';

-- David Kim - International Tax (Male, Experienced)
UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/david_kim.jpg',
    updated_at = NOW()
WHERE email = 'david@concierge.ai';

-- Marcus Rodriguez - Crypto Tax (Male, Modern)
UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/marcus_rodriguez.jpg',
    updated_at = NOW()
WHERE email = 'marcus@concierge.ai';

-- Lisa Patel - Financial Planning (Female, Advisor)
UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/lisa_patel.jpg',
    updated_at = NOW()
WHERE email = 'lisa@concierge.ai';

-- ==============================================
-- STEP 2: Add 10 New Experts with Images
-- ==============================================

INSERT INTO experts (name, email, specialties, bio, avatar_url, availability, performance_metrics) VALUES

-- Jennifer Washington - Estate Planning (Image 6)
('Jennifer Washington', 'jennifer@concierge.ai', 
 '["tax", "estate_planning", "trusts"]',
 'Estate planning attorney and tax strategist with 15+ years helping families minimize estate taxes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/jennifer_washington.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Alex Martinez - Startup Tax (Image 7)
('Alex Martinez', 'alex@concierge.ai',
 '["tax", "startup", "equity_compensation"]',
 'Former Big 4 tax consultant specializing in startup taxation, equity comp, and venture capital structures',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/alex_martinez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Michael O'Brien - Real Estate Tax (Image 8)
('Michael O''Brien', 'michael@concierge.ai',
 '["tax", "real_estate", "1031_exchange"]',
 'Real estate tax specialist with expertise in 1031 exchanges, rental property, and real estate professional status',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/michael_obrien.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Dr. Rachel Green - Non-Profit Tax (Image 9)
('Dr. Rachel Green', 'rachel@concierge.ai',
 '["tax", "nonprofit", "501c3"]',
 'PhD in taxation specializing in non-profit organizations, 501(c)(3) compliance, and charitable giving strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/rachel_green.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- James Liu - Retirement Planning (Image 10)
('James Liu', 'james@concierge.ai',
 '["tax", "retirement", "401k", "ira"]',
 'Retirement planning specialist focusing on 401(k), IRA conversions, and tax-efficient withdrawal strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/james_liu.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Nina Patel - Freelance Tax (Image 11)
('Nina Patel', 'nina@concierge.ai',
 '["tax", "freelance", "gig_economy", "estimated_tax"]',
 'Tax advisor for freelancers, gig workers, and independent contractors with focus on quarterly estimated taxes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/nina_patel.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Robert Taylor - Multi-State Tax (Image 12)
('Robert Taylor', 'robert@concierge.ai',
 '["tax", "multi_state", "apportionment"]',
 'Multi-state tax expert helping remote workers and businesses navigate complex state tax obligations',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/robert_taylor.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Dr. Priya Sharma - Healthcare Tax (Image 15)
('Dr. Priya Sharma', 'priya@concierge.ai',
 '["tax", "healthcare", "medical_deductions", "hsa"]',
 'CPA and former physician specializing in healthcare provider taxation, medical deductions, and HSA strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/priya_sharma.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Amanda Foster - Divorce Tax (Image 16)
('Amanda Foster', 'amanda@concierge.ai',
 '["tax", "divorce", "alimony", "child_support"]',
 'Family law tax specialist focusing on divorce tax implications, alimony, child support, and filing status changes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/amanda_foster.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Carlos Mendez - IRS Audit Defense (Image 17)
('Carlos Mendez', 'carlos@concierge.ai',
 '["tax", "audit", "irs_representation", "tax_resolution"]',
 'Former IRS agent now helping taxpayers with audit defense, tax resolution, and IRS representation',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/carlos_mendez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}');

-- ==============================================
-- VERIFICATION QUERY
-- ==============================================
SELECT 
  name, 
  email, 
  specialties,
  SUBSTRING(avatar_url, LENGTH(avatar_url) - 30, 31) as image_file
FROM experts 
ORDER BY created_at DESC;
