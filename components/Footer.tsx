"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import {
    RxGithubLogo,
    RxLinkedinLogo,
    RxEnvelopeClosed,
} from "react-icons/rx";
import { AuroraText } from "@/components/ui/aurora-text";

const Footer = () => {
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const checkIsMobile = () => {
            setIsMobile(window.innerWidth < 768);
        };
        checkIsMobile();
        window.addEventListener('resize', checkIsMobile);
        return () => window.removeEventListener('resize', checkIsMobile);
    }, []);

    if (isMobile) {
        return (
            <div id="contacts" className="w-full h-auto py-4 px-6 dark text-white bg-black">
                <div>
                    <h1 className="text-3xl font-bold text-center mb-4 leading-relaxed">
                        Get
                        <AuroraText> In </AuroraText>
                        Touch
                    </h1>
                </div>

                <div className="space-y-6">
                    {/* Logo Section */}
                    <div className="text-center">
                        <div className="flex justify-center py-2">
                            <Image
                                src="/shp_logos/shriharripriya_logo.svg"
                                alt="logo"
                                loading="eager"
                                width={200}
                                height={40}
                            />
                        </div>
                    </div>

                    {/* Social Icons */}
                    <div className="flex justify-center gap-8 py-2">
                        <a href="https://www.linkedin.com/in/rshriharripriya/" target="_blank" rel="noreferrer">
                            <button className="hover:text-blue-400 transition-colors">
                                <RxLinkedinLogo size={28} />
                            </button>
                        </a>
                        <a href="mailto:rshriharripriya@outlook.com" target="_blank" rel="noreferrer">
                            <button className="hover:text-red-400 transition-colors">
                                <RxEnvelopeClosed size={28} />
                            </button>
                        </a>
                        <a href="https://github.com/rshriharripriya" target="_blank" rel="noreferrer">
                            <button className="hover:text-gray-400 transition-colors">
                                <RxGithubLogo size={28} />
                            </button>
                        </a>
                    </div>

                    {/* Navigation Links */}
                    <div className="space-y-3 text-center">
                        <div className="text-xl font-semibold mb-2">Quick Links</div>
                        <div className="space-y-2">
                            <p className="cursor-pointer">
                                <Link href="https://rshriharripriya.vercel.app/#about" target="_blank" rel="noopener noreferrer">
                                    <span className="text-lg hover:text-purple-400 transition-colors">About Me</span>
                                </Link>
                            </p>
                            <p className="cursor-pointer">
                                <Link href="https://rshriharripriya.vercel.app/#projects" target="_blank" rel="noopener noreferrer">
                                    <span className="text-lg hover:text-purple-400 transition-colors">My Projects</span>
                                </Link>
                            </p>
                            <p className="cursor-pointer">
                                <Link href="https://rshriharripriya.vercel.app/#awards" target="_blank" rel="noopener noreferrer">
                                    <span className="text-lg hover:text-purple-400 transition-colors">My Awards</span>
                                </Link>
                            </p>

                            <p className="cursor-pointer">
                                <Link href="mailto:rshriharripriya@outlook.com" className="hover:text-purple-400 transition-colors">
                                    <div className="text-base">Hire Me </div>
                                </Link>
                            </p>
                            <p className="cursor-pointer">
                                <Link href="https://music.apple.com/profile/rshriharripriya" target="_blank" rel="noopener noreferrer" className="hover:text-purple-400 transition-colors">
                                    <span className="text-base">My Playlists</span>
                                </Link>
                            </p>
                        </div>
                    </div>

                    {/* Copyright at the bottom */}
                    <div className="border-t border-gray-800 pt-3 mt-4 text-center">
                        <div className="text-sm text-gray-400">
                            Made with 💌 by Shri Harri Priya Ramesh
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div id="contacts" className="w-full h-auto py-6 dark text-white bg-black">
            <div>
                <h1 className="flex justify-center text-4xl align-middle font-bold tracking-tighter md:text-5xl lg:text-5xl mb-6">
                    Get <AuroraText>In</AuroraText> Touch
                </h1>
            </div>
            <div className="w-full flex flex-col items-center justify-center">
                <div className="w-full max-w-7xl flex flex-row items-start justify-around flex-wrap gap-8 px-4">
                    <div className="min-w-[200px] h-auto items-center justify-start flex flex-col">
                        <div className="flex flex-row pb-3">
                            <Image className="flex" src="/shp_logos/shriharripriya_logo.svg"
                                alt="logo" loading="eager" width={700} height={120} style={{
                                    width: '14vw',
                                    height: 'auto',
                                }} />
                        </div>
                        <div className="flex flex-row flex-wrap h-15 justify-center gap-6">
                            <a href="https://www.linkedin.com/in/rshriharripriya/" target="_blank"
                                rel="noreferrer">
                                <button className="flex flex-row items-center hover:text-blue-400 transition-colors">
                                    <RxLinkedinLogo size={30} />
                                </button>
                            </a>
                            <a href="mailto:rshriharripriya@outlook.com" target="_blank"
                                rel="noreferrer">
                                <button className="flex flex-row items-center hover:text-red-400 transition-colors">
                                    <RxEnvelopeClosed size={30} />
                                </button>
                            </a>
                            <a href="https://github.com/rshriharripriya" target="_blank"
                                rel="noreferrer">
                                <button className="flex flex-row items-center hover:text-gray-400 transition-colors">
                                    <RxGithubLogo size={30} />
                                </button>
                            </a>
                        </div>
                        <div className="mt-0 text-[15px] text-center text-gray-400">
                            Made with 💌 by Shri Harri Priya Ramesh
                        </div>
                    </div>

                    <div className="min-w-[200px] h-auto flex flex-col items-center justify-start pt-4 space-y-7">
                        <p className="flex flex-row items-center cursor-pointer">
                            <Link href="https://rshriharripriya.vercel.app/#about" target="_blank" rel="noopener noreferrer">
                                <span className="text-[15px] hover:text-purple-400 transition-colors">About Me</span>
                            </Link>
                        </p>
                        <p className="flex flex-row items-center cursor-pointer">
                            <Link href="https://rshriharripriya.vercel.app/#projects" target="_blank" rel="noopener noreferrer">
                                <span className="text-[15px] hover:text-purple-400 transition-colors">My projects</span>
                            </Link>
                        </p>
                        <p className="flex flex-row items-center cursor-pointer">
                            <Link href="https://rshriharripriya.vercel.app/#awards" target="_blank" rel="noopener noreferrer">
                                <span className="text-[15px] hover:text-purple-400 transition-colors">My awards</span>
                            </Link>
                        </p>
                    </div>
                    <div className="min-w-[200px] h-auto flex flex-col items-center justify-start pt-4 space-y-7">
                        <p className="flex flex-row items-center cursor-pointer">
                            <Link href="mailto:rshriharripriya@outlook.com" target="_blank" className="hover:text-purple-400 transition-colors">
                                <span className="text-[15px]">Hire me</span>
                            </Link  >
                        </p>
                        <p className="flex flex-row items-center cursor-pointer">
                            <Link href="https://rshriharripriya.vercel.app" target="_blank" rel="noopener noreferrer" className="hover:text-purple-400 transition-colors">
                                <span className="text-[15px]">My blogs</span>
                            </Link>
                        </p>
                        <p className="flex flex-row items-center cursor-pointer">
                            <Link href="https://music.apple.com/profile/rshriharripriya" target="_blank" rel="noopener noreferrer"
                                className="flex flex-row items-center hover:text-purple-400 transition-colors">
                                <span className="text-[15px]">Check out my playlists</span>
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Footer;
