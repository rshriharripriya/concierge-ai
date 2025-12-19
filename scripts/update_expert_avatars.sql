-- Update existing expert avatars with Supabase Storage URLs
-- Replace 'YOUR_PROJECT_ID' with your actual Supabase project ID
-- Replace 'expert-avatars' with your actual bucket name

-- Update Sarah Chen (CPA - small business tax)
UPDATE experts
SET avatar_url = 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/sarah_chen.png',
    updated_at = NOW()
WHERE email = 'sarah@concierge.ai';

-- Update Emily Thompson (Bookkeeper - QuickBooks)
UPDATE experts
SET avatar_url = 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/emily_thompson.png',
    updated_at = NOW()
WHERE email = 'emily@concierge.ai';

-- Update David Kim (International tax)
UPDATE experts
SET avatar_url = 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/david_kim.png',
    updated_at = NOW()
WHERE email = 'david@concierge.ai';

-- Update Marcus Rodriguez (Crypto & capital gains)
UPDATE experts
SET avatar_url = 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/marcus_rodriguez.png',
    updated_at = NOW()
WHERE email = 'marcus@concierge.ai';

-- Update Lisa Patel (Financial planning)
UPDATE experts
SET avatar_url = 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/expert-avatars/lisa_patel.png',
    updated_at = NOW()
WHERE email = 'lisa@concierge.ai';

-- Verify updates
SELECT name, email, avatar_url 
FROM experts 
WHERE email IN ('sarah@concierge.ai', 'emily@concierge.ai', 'david@concierge.ai', 'marcus@concierge.ai', 'lisa@concierge.ai')
ORDER BY name;
