/**
 * components/layout/Header.tsx
 * Главный header с навигацией
 */
'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth.store';
import { RealTimeNotifications } from '@/components/common/RealTimeNotifications';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { LogOut, Settings, User as UserIcon } from 'lucide-react';

export function Header() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  
  const handleLogout = () => {
    logout();
    router.push('/login');
  };
  
  const getDashboardUrl = () => {
    if (!user) return '/';
    
    switch (user.user_type) {
      case 'seller':
        return '/seller/dashboard';
      case 'channel_owner':
        return '/channel/dashboard';
      case 'admin':
        return '/admin/dashboard';
      default:
        return '/';
    }
  };
  
  return (
    <header className="border-b">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="font-bold text-xl">
          📱 Marketplace
        </Link>
        
        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm hover:text-gray-600">
            Home
          </Link>
          <Link href="/about" className="text-sm hover:text-gray-600">
            About
          </Link>
          <Link href="/how-it-works" className="text-sm hover:text-gray-600">
            How It Works
          </Link>
        </nav>
        
        {/* Auth */}
        <div className="flex items-center gap-2">
          {isAuthenticated && user && <RealTimeNotifications />}
          {isAuthenticated && user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>
                      {user.full_name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{user.full_name}</DropdownMenuLabel>
                <DropdownMenuLabel className="text-xs text-gray-500">
                  {user.user_type}
                </DropdownMenuLabel>
                
                <DropdownMenuSeparator />
                
                <DropdownMenuItem asChild>
                  <Link href={getDashboardUrl()}>
                    <UserIcon className="mr-2 h-4 w-4" />
                    Dashboard
                  </Link>
                </DropdownMenuItem>
                
                <DropdownMenuItem asChild>
                  <Link href={`/${user.user_type}/profile`}>
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                
                <DropdownMenuSeparator />
                
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" asChild>
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild>
                <Link href="/register">Sign Up</Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

