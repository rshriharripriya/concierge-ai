-- Complete 20 Tax Experts Setup
-- All unique experts with correctly matched images
-- URL: https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/

-- ==============================================
-- STEP 1: Clear all test data
-- ==============================================

-- Delete messages first (references conversations)
DELETE FROM messages;

-- Delete conversations (references experts)
DELETE FROM conversations;

-- Now safe to delete experts
DELETE FROM experts;

-- Insert all 20 experts
INSERT INTO experts (name, email, specialties, bio, avatar_url, availability, performance_metrics) VALUES

-- FEMALE EXPERTS (10)
('Emily Thompson', 'emily@concierge.ai',
 ARRAY['bookkeeping', 'quickbooks', 'payroll'],
 'Certified bookkeeper specializing in QuickBooks and payroll services for small businesses',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/emily_thompson.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Jennifer Washington', 'jennifer@concierge.ai',
 ARRAY['tax', 'estate_planning', 'trusts'],
 'Estate planning attorney and tax strategist with 15+ years helping families minimize estate taxes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/jennifer_washington.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Sarah Chen', 'sarah@concierge.ai',
 ARRAY['tax', 'small_business', 'schedule_c'],
 'CPA with 10+ years experience in small business taxation and Schedule C optimization',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/sarah_chen.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Amanda Foster', 'amanda@concierge.ai',
 ARRAY['tax', 'divorce', 'alimony', 'child_support'],
 'Family law tax specialist focusing on divorce tax implications, alimony, and child support',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/amanda_foster.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Lisa Morgan', 'lisa@concierge.ai',
 ARRAY['bookkeeping', 'financial_planning', 'cash_flow'],
 'Financial advisor helping businesses optimize cash flow and long-term financial planning',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/lisa_morgan.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Dr. Patricia Sherman', 'patricia@concierge.ai',
 ARRAY['tax', 'healthcare', 'medical_deductions', 'hsa'],
 'Former physician turned CPA specializing in healthcare provider taxation and medical deductions',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/patricia_sherman.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Nina Brooks', 'nina@concierge.ai',
 ARRAY['tax', 'freelance', 'gig_economy', 'estimated_tax'],
 'Tax advisor for freelancers, gig workers, and independent contractors with focus on quarterly taxes',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/nina_brooks.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Dr. Rachel Green', 'rachel@concierge.ai',
 ARRAY['tax', 'nonprofit', '501c3'],
 'PhD in taxation specializing in non-profit organizations and 501(c)(3) compliance',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/rachel_green.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Katherine Wells', 'katherine@concierge.ai',
 ARRAY['tax', 'education', '529_plans', 'student_loans'],
 'Education tax specialist focusing on 529 plans, student loan deductions, and education credits',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/katherine_wells.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Michelle Stevens', 'michelle@concierge.ai',
 ARRAY['tax', 'senior_tax', 'social_security', 'medicare'],
 'Senior tax specialist helping retirees navigate Social Security, Medicare, and RMDs',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/michelle_stevens.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- MALE EXPERTS (10)
('David Kim', 'david@concierge.ai',
 ARRAY['tax', 'international', 'foreign_income'],
 'International tax consultant with expertise in expat taxation, FBAR, and foreign income',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/david_kim.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Michael O''Brien', 'michael@concierge.ai',
 ARRAY['tax', 'real_estate', '1031_exchange'],
 'Real estate tax specialist with expertise in 1031 exchanges and rental property taxation',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/michael_obrien.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Alex Martinez', 'alex@concierge.ai',
 ARRAY['tax', 'startup', 'equity_compensation'],
 'Former Big 4 consultant specializing in startup taxation and equity compensation',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/alex_martinez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Marcus Rodriguez', 'marcus@concierge.ai',
 ARRAY['tax', 'crypto', 'capital_gains'],
 'Cryptocurrency and digital asset tax specialist focusing on Bitcoin, NFTs, and DeFi',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/marcus_rodriguez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('James Liu', 'james@concierge.ai',
 ARRAY['tax', 'retirement', '401k', 'IRA'],
 'Retirement planning specialist focusing on 401(k), IRA conversions, and withdrawal strategies',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/james_liu.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Robert Taylor', 'robert@concierge.ai',
 ARRAY['tax', 'multi_state', 'apportionment'],
 'Multi-state tax expert helping remote workers navigate complex state tax obligations',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/robert_taylor.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Carlos Mendez', 'carlos@concierge.ai',
 ARRAY['tax', 'audit', 'irs_representation', 'tax_resolution'],
 'Former IRS agent providing audit defense, tax resolution, and IRS representation',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/carlos_mendez.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Nathan Brown', 'nathan@concierge.ai',
 ARRAY['tax', 'manufacturing', 'cost_segregation', 'r_d_credits'],
 'Manufacturing tax specialist focusing on cost segregation and R&D tax credits',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/nathan_brown.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Thomas Anderson', 'thomas@concierge.ai',
 ARRAY['tax', 'agriculture', 'farm_tax', 'conservation'],
 'Agricultural tax specialist with expertise in farm taxation and conservation easements',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/thomas_anderson.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

('Kevin Zhang', 'kevin@concierge.ai',
 ARRAY['tax', 'e_commerce', 'sales_tax', 'nexus'],
 'E-commerce tax specialist helping online sellers with sales tax nexus and compliance',
 'https://vxtedgxcdthcozuovtxx.supabase.co/storage/v1/object/public/Expert%20images/kevin_zhang.jpg',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}');

-- Verification
SELECT name, email, specialties,
  SUBSTRING(avatar_url FROM '([^/]+\.jpg)$') as image
FROM experts 
ORDER BY name;
