-- Add 10 new tax and financial experts to the database
-- Run this in Supabase SQL Editor
-- Replace 'YOUR_PROJECT_ID' with your actual Supabase project ID
-- Replace 'expert-avatars' with your actual bucket name

INSERT INTO experts (name, email, specialties, bio, avatar_url, availability, performance_metrics) VALUES
-- Expert 6: Estate Planning Specialist
('Jennifer Washington', 'jennifer@concierge.ai', 
 '["tax", "estate_planning", "trusts"]',
 'Estate planning attorney and tax strategist with 15+ years helping families minimize estate taxes',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/jennifer_washington.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 7: Startup & VC Tax Expert
('Alex Martinez', 'alex@concierge.ai',
 '["tax", "startup", "equity_compensation"]',
 'Former Big 4 tax consultant specializing in startup taxation, equity comp, and venture capital structures',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/alex_martinez.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 8: Real Estate Tax Specialist
('Michael O''Brien', 'michael@concierge.ai',
 '["tax", "real_estate", "1031_exchange"]',
 'Real estate tax specialist with expertise in 1031 exchanges, rental property, and real estate professional status',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/michael_obrien.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 9: Non-Profit & Tax-Exempt Specialist
('Dr. Rachel Green', 'rachel@concierge.ai',
 '["tax", "nonprofit", "501c3"]',
 'PhD in taxation specializing in non-profit organizations, 501(c)(3) compliance, and charitable giving strategies',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/rachel_green.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 10: Retirement & 401k Expert  
('James Liu', 'james@concierge.ai',
 '["tax", "retirement", "401k", "ira"]',
 'Retirement planning specialist focusing on 401(k), IRA conversions, and tax-efficient withdrawal strategies',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/james_liu.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 11: Freelance & Gig Economy Tax
('Nina Patel', 'nina@concierge.ai',
 '["tax", "freelance", "gig_economy", "estimated_tax"]',
 'Tax advisor for freelancers, gig workers, and independent contractors with focus on quarterly estimated taxes',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/nina_patel.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 12: Multi-State Tax Specialist
('Robert Taylor', 'robert@concierge.ai',
 '["tax", "multi_state", "apportionment"]',
 'Multi-state tax expert helping remote workers and businesses navigate complex state tax obligations',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/robert_taylor.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 13: Healthcare & Medical Tax
('Dr. Priya Sharma', 'priya@concierge.ai',
 '["tax", "healthcare", "medical_deductions", "hsa"]',
 'CPA and former physician specializing in healthcare provider taxation, medical deductions, and HSA strategies',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/priya_sharma.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 14: Divorce & Family Tax
('Amanda Foster', 'amanda@concierge.ai',
 '["tax", "divorce", "alimony", "child_support"]',
 'Family law tax specialist focusing on divorce tax implications, alimony, child support, and filing status changes',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/amanda_foster.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}'),

-- Expert 15: Tax Audit Defense
('Carlos Mendez', 'carlos@concierge.ai',
 '["tax", "audit", "irs_representation", "tax_resolution"]',
 'Former IRS agent now helping taxpayers with audit defense, tax resolution, and IRS representation',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/carlos_mendez.png',
 '{"status": "available", "schedule": {}}',
 '{"avg_rating": 0, "resolution_rate": 0, "total_interactions": 0}');
