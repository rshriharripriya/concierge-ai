-- Migration: Populate Expert Profiles
-- Date: 2024-12-16
-- Purpose: Initial expert data with 15 tax and financial specialists
-- Note: Update avatar URLs to match your Supabase project

-- ============================================
-- STEP 1: Update existing 5 experts with avatars
-- ============================================

UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/sarah_chen.jpg'
WHERE email = 'sarah@concierge.ai';

UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/emily_thompson.jpg'
WHERE email = 'emily@concierge.ai';

UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/david_kim.jpg'
WHERE email = 'david@concierge.ai';

UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/marcus_rodriguez.jpg'
WHERE email = 'marcus@concierge.ai';

UPDATE experts
SET avatar_url = 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/lisa_patel.jpg'
WHERE email = 'lisa@concierge.ai';

-- ============================================
-- STEP 2: Add 10 new experts
-- ============================================

INSERT INTO experts (name, email, specialties, bio, avatar_url, availability, performance_metrics) VALUES

-- Estate Planning Specialist
('Jennifer Washington', 'jennifer@concierge.ai', 
 '["tax", "estate_planning", "trusts"]',
 'Estate planning attorney and tax strategist with 15+ years helping families minimize estate taxes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/jennifer_washington.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Startup & VC Tax Expert
('Alex Martinez', 'alex@concierge.ai',
 '["tax", "startup", "equity_compensation"]',
 'Former Big 4 tax consultant specializing in startup taxation, equity comp, and venture capital structures',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/alex_martinez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Real Estate Tax Specialist
('Michael O''Brien', 'michael@concierge.ai',
 '["tax", "real_estate", "1031_exchange"]',
 'Real estate tax specialist with expertise in 1031 exchanges, rental property, and real estate professional status',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/michael_obrien.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Non-Profit & Tax-Exempt Specialist
('Dr. Rachel Green', 'rachel@concierge.ai',
 '["tax", "nonprofit", "501c3"]',
 'PhD in taxation specializing in non-profit organizations, 501(c)(3) compliance, and charitable giving strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/rachel_green.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Retirement & 401k Expert
('James Liu', 'james@concierge.ai',
 '["tax", "retirement", "401k", "ira"]',
 'Retirement planning specialist focusing on 401(k), IRA conversions, and tax-efficient withdrawal strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/james_liu.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Freelance & Gig Economy Tax
('Nina Patel', 'nina@concierge.ai',
 '["tax", "freelance", "gig_economy", "estimated_tax"]',
 'Tax advisor for freelancers, gig workers, and independent contractors with focus on quarterly estimated taxes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/nina_patel.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Multi-State Tax Specialist
('Robert Taylor', 'robert@concierge.ai',
 '["tax", "multi_state", "apportionment"]',
 'Multi-state tax expert helping remote workers and businesses navigate complex state tax obligations',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/robert_taylor.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Healthcare & Medical Tax
('Dr. Priya Sharma', 'priya@concierge.ai',
 '["tax", "healthcare", "medical_deductions", "hsa"]',
 'CPA and former physician specializing in healthcare provider taxation, medical deductions, and HSA strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/priya_sharma.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Divorce & Family Tax
('Amanda Foster', 'amanda@concierge.ai',
 '["tax", "divorce", "alimony", "child_support"]',
 'Family law tax specialist focusing on divorce tax implications, alimony, child support, and filing status changes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/amanda_foster.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- IRS Audit Defense
('Carlos Mendez', 'carlos@concierge.ai',
 '["tax", "audit", "irs_representation", "tax_resolution"]',
 'Former IRS agent now helping taxpayers with audit defense, tax resolution, and IRS representation',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/carlos_mendez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}')

ON CONFLICT (email) DO NOTHING;

-- ============================================
-- Verification
-- ============================================
SELECT 
  COUNT(*) as total_experts,
  COUNT(CASE WHEN avatar_url IS NOT NULL THEN 1 END) as experts_with_avatars
FROM experts;
