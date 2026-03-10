'use client'

import posthog from 'posthog-js'
import { PostHogProvider as CSPostHogProvider } from 'posthog-js/react'
import { usePathname, useSearchParams } from 'next/navigation'
import { useEffect, Suspense } from 'react'

const isPostHogConfigured = () => {
    return typeof process.env.NEXT_PUBLIC_POSTHOG_KEY === 'string' &&
        process.env.NEXT_PUBLIC_POSTHOG_KEY !== 'your_posthog_key_here' &&
        process.env.NEXT_PUBLIC_POSTHOG_KEY !== ''
}

if (typeof window !== 'undefined' && isPostHogConfigured()) {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
        person_profiles: 'identified_only',
        capture_pageview: false, // Disable automatic pageview capture, as we capture manually
    })
}

export function PostHogPageView() {
    const pathname = usePathname()
    const searchParams = useSearchParams()

    useEffect(() => {
        if (pathname && posthog && isPostHogConfigured()) {
            let url = window.origin + pathname
            if (searchParams?.toString()) {
                url = url + `?${searchParams.toString()}`
            }
            posthog.capture('$pageview', {
                $current_url: url,
            })
        }
    }, [pathname, searchParams])

    return null
}

export function PostHogProvider({ children }: { children: React.ReactNode }) {
    if (!isPostHogConfigured()) {
        return <>{children}</>
    }

    return (
        <CSPostHogProvider client={posthog}>
            <Suspense fallback={null}>
                <PostHogPageView />
            </Suspense>
            {children}
        </CSPostHogProvider>
    )
}
