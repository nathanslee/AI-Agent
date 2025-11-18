"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { removeToken, isAuthenticated } from "@/lib/auth";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

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
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-glow">
              <span className="text-white font-bold text-xl">AI</span>
            </div>
            <span className="font-display text-xl font-semibold hidden sm:block">
              Database Assistant
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-4">
            {isAuth ? (
              <>
                <Link href="/dashboard">
                  <Button variant={pathname === "/dashboard" ? "default" : "ghost"}>
                    Dashboard
                  </Button>
                </Link>
                <Button variant="outline" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost">Login</Button>
                </Link>
                <Link href="/signup">
                  <Button>Sign Up</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
