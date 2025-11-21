"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { removeToken, isAuthenticated } from "@/lib/auth";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import ThemeSwitch from "./ThemeSwitch";

export default function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuth, setIsAuth] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    setIsAuth(isAuthenticated());

    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [pathname]);

  const handleLogout = () => {
    removeToken();
    setIsAuth(false);
    router.push("/");
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "glass shadow-soft" : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-3 sm:px-6 py-2 sm:py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-1.5 sm:space-x-2">
            <div className="w-7 sm:w-10 h-7 sm:h-10 rounded-lg sm:rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-glow">
              <span className="text-white font-bold text-sm sm:text-xl">AI</span>
            </div>
            <span className="font-display text-lg sm:text-xl font-semibold hidden sm:block">
              Database Assistant
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
            <div className="scale-[0.65] sm:scale-100 origin-right mr-1 sm:mr-0">
              <ThemeSwitch />
            </div>
            {isAuth ? (
              <>
                <Link href="/dashboard">
                  <Button variant={pathname === "/dashboard" ? "default" : "ghost"} className="text-xs sm:text-sm px-3 sm:px-6 h-8 sm:h-12 rounded-lg sm:rounded-2xl">
                    Dashboard
                  </Button>
                </Link>
                <Button variant="outline" onClick={handleLogout} className="text-xs sm:text-sm px-3 sm:px-6 h-8 sm:h-12 rounded-lg sm:rounded-2xl">
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" className="text-xs sm:text-sm px-3 sm:px-6 h-8 sm:h-12 rounded-lg sm:rounded-2xl">
                    Login
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button className="text-xs sm:text-sm px-3 sm:px-6 h-8 sm:h-12 rounded-lg sm:rounded-2xl">
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
